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


class Names:
    def __init__(self, fullname):
        list_names = fullname.split()
        list_names += [""]
        self.last_name = list_names[0]
        self.first_name = list_names[1]
        self.middle_name = list_names[2]


def test_data_synchronization(mssql_fixture, superuser_credentials):
    factory = RequestFactory()
    synchronization_url = f"{host}/api/refresh/"

    access_token = superuser_credentials["superuser_token"]

    headers = {"Authorization": f"Token {access_token}"}

    response = requests.get(synchronization_url, headers=headers)
    assert response.status_code == 200

    prepods_count = Prepod.objects.count()
    groups_count = Group.objects.count()
    teachers_count = User.objects.filter(is_teacher=1).count()

    assert prepods_count == 2
    assert groups_count == 2
    assert teachers_count == 1

    synced_prepod = Prepod.objects.get(id=1)
    assert synced_prepod.fullname == "Петров Петр Петрович"
    assert synced_prepod.email == "piotr.petrovich@gmail.com"
    assert synced_prepod.direction == "Робототехника"

    synced_group = Group.objects.get(id=1)
    assert synced_group.study_groups == "MG1294749022"
    assert synced_group.course_id == 1
    assert synced_group.teacher_fullname == "Петров Петр Петрович"
    assert synced_group.teacher_id == 1
    assert synced_group.study_courses == "Алгоритмика"
    assert synced_group.direction == "Робототехника"

    synced_user = User.objects.get(id_crm=1)
    assert synced_user.first_name == "Петр"
    assert synced_user.last_name == "Петров"
    assert synced_user.middle_name == "Петрович"
    assert synced_user.email == "piotr.petrovich@gmail.com"
    assert synced_user.study_groups == str(["MG1294749022"])
    assert synced_user.study_courses == str(["Алгоритмика"])

    synced_user = User.objects.get(id_crm=1)
    synced_user.delete()
