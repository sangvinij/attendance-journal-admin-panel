import os
import django
import requests

from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.test import RequestFactory
from accounts.views import RefreshPoint
from accounts.models import Group, Prepod, User

load_dotenv()

host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def test_data_synchronization(mssql_fixture, superuser_credentials):
    factory = RequestFactory()
    synchronization_url = f"{host}/api/refresh/"

    access_token = superuser_credentials["superuser_token"]

    headers = {"Authorization": f"Token {access_token}"}

    response = requests.get(synchronization_url, headers=headers)
    assert response.status_code == 200

    prepods_count = Group.objects.count()
    groups_count = Prepod.objects.count()
    assert prepods_count == 1
    assert groups_count == 1

    synced_user = Prepod.objects.get(id=1)
    assert synced_user.fullname == "Петров Петр Петрович"
    assert synced_user.email == "piotr.petrovich@gmail.com"
    assert synced_user.direction == "Робототехника"

    synced_group = Group.objects.get(id=1)
    assert synced_group.study_groups == "MG1294749022"
    assert synced_group.course_id == 1
    assert synced_group.teacher_fullname == "Петров Петр Петрович"
    assert synced_group.teacher_id == 1
    assert synced_group.study_courses == "Алгоритмика"
    assert synced_group.direction == "Робототехника"

    synced_user = User.objects.get(id_crm=1)
    synced_user.delete()
