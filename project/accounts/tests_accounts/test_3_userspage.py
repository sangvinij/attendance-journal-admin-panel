import os

from dotenv import find_dotenv, load_dotenv

import requests

from .test_2_login import create_token, register_user

load_dotenv(find_dotenv())
host = os.getenv("HOST_FOR_TESTS", "http://localhost:8000")


def create_study_field(study_field):
    url = f"{host}/api/users/study_fields/"
    rs = requests.post(url, data={"study_field": study_field})
    return rs.json()


class TestUserModel:
    API_URL = f"{host}/api/users/list/"

    def response_to_api_url(self, token, **kwargs):
        rs = requests.get(self.API_URL, params=kwargs, headers={"Authorization": f"Token {token}"})
        return rs

    def test_unauthorized_request_to_endpoint(self):
        rs = self.response_to_api_url(token="")
        assert rs.status_code == 401

    def test_user_list_endpoint_accessible_for_superuser(self):
        superuser_username = "test_userspage_superuser"
        superuser_password = "admin1"
        register_user(username=superuser_username, password=superuser_password, is_superuser=True)
        token = create_token(username=superuser_username, password=superuser_password).json()["auth_token"]
        rs = self.response_to_api_url(token)
        assert rs.status_code == 200

    def test_user_list_endpoint_inaccessible_for_non_superuser(self):
        username = "test_userpage_user"
        password = "password1"
        register_user(username=username, password=password)
        token = create_token(username=username, password=password).json()["auth_token"]
        rs = self.response_to_api_url(token)
        assert rs.status_code == 403

    def test_user_list_pagination(self):
        superuser_username = "test_userspage_superuser1"
        superuser_password = "admin1"
        register_user(username=superuser_username, password=superuser_password, is_superuser=True)
        token = create_token(username=superuser_username, password=superuser_password).json()["auth_token"]
        rs = self.response_to_api_url(token)
        assert "next" in rs.json()
        assert "previous" in rs.json()

    def test_user_list_filter_by_role(self):
        superuser_username = "test_userspage_superuser2"
        superuser_password = "admin1"
        username = "test_user1"
        password = "admin1"
        register_user(username=superuser_username, password=superuser_password, is_superuser=True, is_metodist=False)
        register_user(username=username, password=password, is_superuser=False, is_metodist=True)
        token = create_token(username=superuser_username, password=superuser_password).json()["auth_token"]
        rs = self.response_to_api_url(token, role="admin")
        assert rs.status_code == 200
        for user in rs.json()["results"]:
            assert user["is_superuser"] is True

        rs2 = self.response_to_api_url(token, role="metodist")
        for user in rs2.json()["results"]:
            assert user["is_metodist"] is True
