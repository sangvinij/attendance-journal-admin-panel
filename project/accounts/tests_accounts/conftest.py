import os

from dotenv import load_dotenv

import pytest

from .api_requests import create_token, delete_token, delete_user, register_user

load_dotenv()


@pytest.fixture(scope="session")
def authenticate_superuser():
    superuser_username = os.getenv("DJANGO_SUPERUSER_USERNAME", "Iteen.Admin")
    superuser_password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "Admin1Admin1")
    superuser_token = create_token(username=superuser_username, password=superuser_password).json()["auth_token"]

    yield {
        "superuser_username": superuser_username,
        "superuser_password": superuser_password,
        "superuser_token": superuser_token,
    }

    delete_token(token=superuser_token)


@pytest.fixture()
def create_user(authenticate_superuser):
    superuser_token = authenticate_superuser["superuser_token"]
    superuser_password = authenticate_superuser["superuser_password"]
    username = "test_user"
    password = "+tU/vW-#]{q@9"
    user = register_user(username=username, password=password, superuser_token=superuser_token).json()
    token = create_token(username=username, password=password).json()["auth_token"]

    yield {"user": user, "username": username, "password": password, "token": token}

    delete_user(user_id=user["id"], superuser_password=superuser_password, superuser_token=superuser_token)


@pytest.fixture()
def create_methodist(authenticate_superuser):
    superuser_token = authenticate_superuser["superuser_token"]
    superuser_password = authenticate_superuser["superuser_password"]
    username = "test_methodist"
    password = "Password1"
    methodist = register_user(
        username=username, password=password, is_metodist=True, superuser_token=superuser_token
    ).json()

    yield methodist

    delete_user(user_id=methodist["id"], superuser_password=superuser_password, superuser_token=superuser_token)


@pytest.fixture()
def create_teacher(authenticate_superuser):
    superuser_token = authenticate_superuser["superuser_token"]
    superuser_password = authenticate_superuser["superuser_password"]
    username = "test_teacher"
    password = "Password1"
    teacher = register_user(
        username=username, password=password, is_teacher=True, superuser_token=superuser_token
    ).json()

    yield teacher

    delete_user(user_id=teacher["id"], superuser_password=superuser_password, superuser_token=superuser_token)
