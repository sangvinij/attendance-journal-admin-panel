import os

os.environ["DJANGO_SETTINGS_MODULE"] = 'project.settings'

import django
from django.conf import settings

if not settings.configured:
    django.setup()

from accounts.models import User


def create_superuser_for_adminpanel():
    user = User.objects.create_superuser(username='ITeen.Admin',
                                         password='admin1')


if __name__ == "__main__":
    try:
        create_superuser_for_adminpanel()
    except django.db.utils.IntegrityError:
        print('User already exist!')
