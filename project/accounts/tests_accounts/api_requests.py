import os

from dotenv import find_dotenv, load_dotenv

import requests

load_dotenv(find_dotenv())

host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def register_user(
    username: str,
    password: str,
    superuser_token: str,
    first_name: str = "Name",
    last_name: str = "Last Name",
    email: str = "example@example.com",
    **kwargs,
) -> requests.models.Response:
    data = {
        "username": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }

    data.update(kwargs)
    rs = requests.post(
        f"{host}/auth/users/", json=data, headers={"Authorization": f"Token {superuser_token}"}, timeout=5
    )
    return rs


def create_token(username: str, password: str) -> requests.models.Response:
    rs = requests.post(f"{host}/auth/token/login/", json={"username": username, "password": password}, timeout=5)
    return rs


def delete_token(token: str) -> requests.models.Response:
    rs = requests.post(f"{host}/auth/token/logout/", headers={"Authorization": f"Token {token}"}, timeout=5)
    return rs


def get_info_about_current_user(token: str) -> requests.models.Response:
    rs = requests.get(f"{host}/auth/users/me/", headers={"Authorization": f"Token {token}"}, timeout=5)
    return rs


def update_users_data(superuser_token: str, user_id: int, method: str = "patch", **kwargs) -> requests.models.Response:
    headers = {"Authorization": f"Token {superuser_token}"}
    url = f"{host}/auth/users/{user_id}/"
    timeout = 5
    match method:
        case "patch":
            rs = requests.patch(url, json=kwargs, headers=headers, timeout=timeout)
        case "put":
            rs = requests.put(url, json=kwargs, headers=headers, timeout=timeout)
        case _:
            raise TypeError("Invalid method")

    return rs


def get_detailed_info_about_user(token: str, user_id: int) -> requests.models.Response:
    rs = requests.get(f"{host}/auth/users/{user_id}", headers={"Authorization": f"Token {token}"}, timeout=5)
    return rs


def delete_user(user_id: int, superuser_password: str, superuser_token: str) -> requests.models.Response:
    rs = requests.delete(
        f"{host}/auth/users/{user_id}/",
        json={"current_password": superuser_password},
        headers={"Authorization": f"Token {superuser_token}"},
        timeout=5,
    )
    return rs
