import os

from dotenv import find_dotenv, load_dotenv

import requests

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def register_user(username, password, **kwargs):
    data = {"username": username, "password": password}
    data.update(kwargs)
    rs = requests.post(f"{host}/auth/users/", data=data)
    return rs


def create_token(username, password):
    rs = requests.post(f"{host}/auth/token/login/", data={"username": username, "password": password})
    return rs


def delete_token(token):
    rs = requests.post(f"{host}/auth/token/logout/", headers={"Authorization": f"Token {token}"})
    return rs


def get_access_to_protected_endpoint(token):
    rs = requests.get(f"{host}/auth/users/me/", headers={"Authorization": f"Token {token}"})
    return rs


class TestLogin:
    username = "test_username2"
    password = "admin1"

    def test_register_user(self):
        rs = register_user(username=self.username, password=self.password)
        assert rs.status_code == 201
        assert "username" in rs.json()
        assert rs.json()["username"] == self.username

    def test_get_token_with_wrong_and_correct_data(self):
        register_user(username=self.username, password=self.password)
        failed_rs = create_token(username=self.username, password=f"wrong {self.password}")
        assert failed_rs.status_code == 401
        valid_rs = create_token(username=self.username, password=self.password)
        assert valid_rs.status_code == 200
        assert "auth_token" in valid_rs.json()

    def test_get_access_to_protected_endpoint(self):
        register_user(username=self.username, password=self.password)
        token = create_token(username=self.username, password=self.password).json()["auth_token"]
        failed_rs = get_access_to_protected_endpoint(token="wrong token")
        assert failed_rs.status_code == 401
        valid_rs = get_access_to_protected_endpoint(token=token)
        assert valid_rs.status_code == 200
        assert "username" in valid_rs.json()
        assert valid_rs.json()["username"] == self.username

    def test_delete_token(self):
        register_user(username=self.username, password=self.password)
        token = create_token(username=self.username, password=self.password).json()["auth_token"]
        get_access_rs = get_access_to_protected_endpoint(token=token)
        assert get_access_rs.status_code == 200
        delete_token_rs = delete_token(token)
        assert delete_token_rs.status_code == 204
        final_rs = get_access_to_protected_endpoint(token)
        assert final_rs.status_code == 401

    def test_login_with_spaces_in_credentials(self):
        register_user(username=self.username, password=self.password)
        rs = create_token(username="\x20" + self.username, password=self.password)
        assert rs.status_code == 401
        rs2 = create_token(username=self.username + "\x20", password=self.password)
        assert rs2.status_code == 401
        valid_rs = create_token(username=self.username, password=self.password)
        assert valid_rs.status_code == 200
        rs3 = create_token(username=self.username, password="\x20" + self.password)
        assert rs3.status_code == 401
        rs4 = create_token(username=self.username, password=self.password + "\x20")
        assert rs4.status_code == 401
