import os

import django

import requests

from dotenv import load_dotenv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from accounts.models import Group, Prepod, User

from django.test import RequestFactory

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
    RequestFactory()
    synchronization_url = f"{host}/api/refresh/"

    access_token = superuser_credentials["superuser_token"]

    headers = {"Authorization": f"Token {access_token}"}

    valid_prepod = Prepod.objects.create(
        id=1, fullname="Петров Петр Петрович", email="piotr.petrovich@gmail.com", direction="Робототехника"
    )

    Prepod.objects.create(id=2, fullname="Невалидное_имя", email="piotr.petrovich@gmail.com", direction="Робототехника")

    group1 = Group.objects.create(
        id=1,
        study_groups="study_group1",
        course_id=1,
        teacher_fullname="Петров Петр Петрович",
        teacher_id=1,
        study_courses="study_courses1",
        direction="Робототехника",
    )

    Group.objects.create(
        id=2,
        study_groups="study_group2",
        course_id=1,
        teacher_fullname="Невалидное_имя",
        teacher_id=2,
        study_courses="study_courses2",
        direction="Робототехника",
    )

    response = requests.get(synchronization_url, headers=headers, timeout=5)
    assert response.status_code == 200

    prepods_count = Prepod.objects.count()
    groups_count = Group.objects.count()
    teachers_count = User.objects.filter(is_teacher=1).count()

    assert prepods_count == 2
    assert groups_count == 2
    assert teachers_count == 1

    synced_user = User.objects.get(id_crm=valid_prepod.id)
    assert synced_user.first_name == "Петр"
    assert synced_user.last_name == "Петров"
    assert synced_user.middle_name == "Петрович"
    assert synced_user.email == "piotr.petrovich@gmail.com"
    assert synced_user.study_groups == str(["study_group1"])
    assert synced_user.study_courses == str(["study_courses1"])

    valid_prepod.fullname = "Другой Петр Петрович"
    valid_prepod.save()
    group1.study_groups = "another_study_group1"
    group1.save()

    response = requests.get(synchronization_url, headers=headers, timeout=5)
    assert response.status_code == 200

    synced_user = User.objects.get(id_crm=valid_prepod.id)
    assert synced_user.first_name == "Петр"
    assert synced_user.last_name == "Другой"
    assert synced_user.middle_name == "Петрович"
    assert synced_user.email == "piotr.petrovich@gmail.com"
    assert synced_user.study_groups == str(["another_study_group1"])
    assert synced_user.study_courses == str(["study_courses1"])

    Prepod.objects.all().delete()
    Group.objects.all().delete()
    User.objects.filter(is_teacher=1).delete()
