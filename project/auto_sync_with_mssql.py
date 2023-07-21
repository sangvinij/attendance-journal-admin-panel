import redis
import requests
import os
from dotenv import find_dotenv, load_dotenv
from datetime import datetime
from apscheduler.schedulers.background import BlockingScheduler
from redis.exceptions import ConnectionError

load_dotenv(find_dotenv())

scheduler = BlockingScheduler(timezone="Europe/Minsk")


def sync_scheduler():
    redis_db_url = os.getenv("REDIS_DSN")
    storage = redis.from_url(redis_db_url)
    response = requests.post(
        f'{os.getenv("WEBAPP_HOST")}/auth/token/login/',
        json={"username": os.getenv("DJANGO_SUPERUSER_USERNAME"), "password": os.getenv("DJANGO_SUPERUSER_PASSWORD")},
    )
    superuser_token = response.json()["auth_token"]
    sync_resp = requests.get(
        f'{os.getenv("WEBAPP_HOST")}/api/refresh/', headers={"Authorization": f"Token {superuser_token}"}
    )
    try:
        storage.set("last_sync", datetime.now().strftime("%H:%M %d-%m-%Y"))
    except ConnectionError:
        return None
    return None


sync_scheduler()
if __name__ == "__main__":
    scheduler.add_job(sync_scheduler, "cron", hour="4", id="1", name="auto_sync", max_instances=1)
    scheduler.start()
