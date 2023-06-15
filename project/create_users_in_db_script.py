import django
import os
from dotenv import find_dotenv, load_dotenv
os.environ["DJANGO_SETTINGS_MODULE"] = 'project.settings'
from django.conf import settings

load_dotenv(find_dotenv())

if not settings.configured:
    django.setup()

from accounts.models import User


def create_superuser_for_adminpanel():
    user = User.objects.create_superuser(username=os.getenv("DJANGO_SUPERUSER_USERNAME", "ITeen.Admin"),
                                         password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin1admin1"))


if __name__ == "__main__":
    try:
        create_superuser_for_adminpanel()
    except django.db.utils.IntegrityError:
        print('User already exist!')
