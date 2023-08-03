import redis
import requests
import os
import pytz
from dotenv import find_dotenv, load_dotenv
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from redis.exceptions import ConnectionError

load_dotenv(find_dotenv())

scheduler = BlockingScheduler(timezone="Europe/Minsk")


def sync_scheduler():
    redis_db_url = os.getenv("REDIS_DSN")
    storage = redis.from_url(redis_db_url)
    webapp_host = os.getenv("WEBAPP_HOST")
    django_superuser_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "Iteen.Admin")
    django_superuser_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin1Admin1")
    try:
        response = requests.post(
            f"{webapp_host}/auth/token/login/",
            json={
                "username": django_superuser_username,
                "password": django_superuser_password,
            },
        )
    except requests.exceptions.ConnectionError:
        print("No connection to server")
        return None
    superuser_token = response.json()["auth_token"]
    try:
        sync_resp = requests.get(f"{webapp_host}/api/refresh/", headers={"Authorization": f"Token {superuser_token}"})
    except requests.exceptions.ConnectionError:
        print("No connection to server")
        return None

    try:
        storage.set("last_sync", datetime.now(pytz.timezone("Europe/Minsk")).strftime("%H:%M %d-%m-%Y"))
    except ConnectionError:
        return None
    return None


sync_scheduler()
if __name__ == "__main__":
    scheduler.add_job(sync_scheduler, "cron", hour="4", id="1", name="auto_sync", max_instances=1)
    scheduler.start()
