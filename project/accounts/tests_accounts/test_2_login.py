import os

from dotenv import find_dotenv, load_dotenv

import requests

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def register_user(username, password, **kwargs):
    data = {"username": username, "password": password}
    data.update(kwargs)
    rs = requests.post(f"{host}/auth/users/", json=data)
    return rs


def create_token(username, password):
    rs = requests.post(f"{host}/auth/token/login/", json={"username": username, "password": password})
    return rs


def delete_token(token):
    rs = requests.post(f"{host}/auth/token/logout/", headers={"Authorization": f"Token {token}"})
    return rs


def get_access_to_protected_endpoint(token):
    rs = requests.get(f"{host}/auth/users/me/", headers={"Authorization": f"Token {token}"})
    return rs


def update_users_data(token, user_id, **kwargs):
    rs = requests.patch(f"{host}/auth/users/{user_id}/", json=kwargs, headers={"Authorization": f"Token {token}"})
    return rs


def get_detailed_info_about_user(token, user_id):
    rs = requests.get(f"{host}/auth/users/{user_id}", headers={"Authorization": f"Token {token}"})
    return rs


class TestLogin:
    username = "test_username2"
    password = "admin1"

    def test_get_token_with_wrong_and_correct_data(self):
        register_user(username=self.username, password=self.password)
        failed_rs = create_token(username=self.username, password=f"wrong {self.password}")
        assert failed_rs.status_code == 401
        assert "auth_token" not in failed_rs.json()
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
        valid_rs = create_token(username=self.username, password=self.password)
        assert "auth_token" in valid_rs.json()

    def test_change_flag_is_active(self):
        username = "test_active_user"
        super_username = "test_admin"
        password = self.password

        superuser = register_user(super_username, password, is_superuser=True)
        superuser_token = create_token(super_username, password).json()["auth_token"]

        register_user(username, password)
        token = create_token(username, password).json()["auth_token"]
        user_id = get_access_to_protected_endpoint(token).json()["id"]

        for _ in range(3):
            create_token(username, f"wrong {password}")

        get_users_info_rs = get_detailed_info_about_user(superuser_token, user_id)
        assert get_users_info_rs.status_code == 200
        users_data = get_users_info_rs.json()
        assert users_data["username"] == username
        assert users_data["is_active"] is False

        failed_login_rs = create_token(username, password)
        assert failed_login_rs.status_code == 429

        change_is_active_flag_rs = update_users_data(token=superuser_token, user_id=user_id, is_active=True)
        assert change_is_active_flag_rs.status_code == 200
        updated_users_data = change_is_active_flag_rs.json()
        assert updated_users_data["username"] == username
        assert updated_users_data["is_active"] is True

        valid_login_rs = create_token(username, password)
        assert valid_login_rs.status_code == 200
        assert "auth_token" in valid_login_rs.json()
