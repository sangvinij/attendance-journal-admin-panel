import os

from dotenv import load_dotenv

import pytest

from sqlalchemy import Column, Integer, MetaData, String, Table, UnicodeText, create_engine

from .api_requests import create_token, delete_token, delete_user, register_user

load_dotenv()


@pytest.fixture(scope="session")
def superuser_credentials():
    superuser_username = os.getenv("DJANGO_SUPERUSER_USERNAME")
    superuser_password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
    superuser_token = create_token(username=superuser_username, password=superuser_password).json()["auth_token"]

    yield {
        "superuser_username": superuser_username,
        "superuser_password": superuser_password,
        "superuser_token": superuser_token,
    }

    delete_token(token=superuser_token)


@pytest.fixture()
def user_data(superuser_credentials):
    superuser_token = superuser_credentials["superuser_token"]
    superuser_password = superuser_credentials["superuser_password"]
    username = "test_user"
    password = "+tU/vW-#]{q@9"
    user = register_user(username=username, password=password, superuser_token=superuser_token).json()
    token = create_token(username=username, password=password).json()["auth_token"]

    yield {"user": user, "username": username, "password": password, "token": token}

    delete_user(user_id=user["id"], superuser_password=superuser_password, superuser_token=superuser_token)


@pytest.fixture()
def methodist(superuser_credentials):
    superuser_token = superuser_credentials["superuser_token"]
    superuser_password = superuser_credentials["superuser_password"]
    username = "test_methodist"
    password = "Password1"
    methodist = register_user(
        username=username, password=password, is_metodist=True, superuser_token=superuser_token
    ).json()

    yield methodist

    delete_user(user_id=methodist["id"], superuser_password=superuser_password, superuser_token=superuser_token)


@pytest.fixture()
def teacher(superuser_credentials):
    superuser_token = superuser_credentials["superuser_token"]
    superuser_password = superuser_credentials["superuser_password"]
    username = "test_teacher"
    password = "Password1"
    teacher = register_user(
        username=username, password=password, is_teacher=True, superuser_token=superuser_token
    ).json()

    yield teacher

    delete_user(user_id=teacher["id"], superuser_password=superuser_password, superuser_token=superuser_token)


@pytest.fixture(scope="session")
def mssql_fixture():
    server = os.environ.get("MSSQL_DATABASE_HOST")
    port = os.environ.get("MSSQL_DATABASE_PORT")
    database = os.environ.get("MSSQL_DATABASE_NAME")
    username = os.environ.get("MSSQL_DATABASE_USERNAME")
    password = os.environ.get("MSSQL_DATABASE_PASSWORD")
    driver = "ODBC Driver 18 for SQL Server"

    connection_string = (
        f"DRIVER={{{driver}}};SERVER={server},{port};DATABASE={database};"
        f"UID={username};PWD={password};TrustServerCertificate=yes"
    )
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")

    metadata = MetaData()
    metadata.bind = engine

    Table(
        "tblPrepods",
        metadata,
        Column("ID", Integer, primary_key=True),
        Column("Prepod", UnicodeText(100)),
        Column("Email", String(100)),
        Column("Napravlenie", UnicodeText(100)),
    )

    Table(
        "tblGroups",
        metadata,
        Column("ID", Integer, primary_key=True),
        Column("GroupName", UnicodeText(100)),
        Column("KursID", Integer),
        Column("Prepod", UnicodeText(100)),
        Column("PrepodId", Integer),
        Column("Kurs", UnicodeText(100)),
        Column("Napravlenie", UnicodeText(100)),
    )

    metadata.create_all(bind=engine)

    yield

    metadata.drop_all(bind=engine)
