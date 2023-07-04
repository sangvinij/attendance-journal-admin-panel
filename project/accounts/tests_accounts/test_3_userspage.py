from .api_requests import host

import requests


class TestUserModel:
    API_URL = f"{host}/api/users/list/"

    def response_to_api_url(self, token, **kwargs):
        rs = requests.get(self.API_URL, params=kwargs, headers={"Authorization": f"Token {token}"})
        return rs

    def test_unauthorized_request_to_endpoint(self):
        rs = self.response_to_api_url(token="")
        assert rs.status_code == 401

    def test_user_list_endpoint_accessible_for_superuser(self, authenticate_superuser):
        superuser_token = authenticate_superuser["superuser_token"]
        rs = self.response_to_api_url(superuser_token)
        assert rs.status_code == 200

    def test_user_list_endpoint_inaccessible_for_non_superuser(self, create_user):
        token = create_user["token"]
        rs = self.response_to_api_url(token)
        assert rs.status_code == 403

    def test_user_list_pagination(self, authenticate_superuser):
        superuser_token = authenticate_superuser["superuser_token"]
        rs = self.response_to_api_url(superuser_token)
        assert "next" in rs.json()
        assert "previous" in rs.json()

    def test_user_list_filter_by_role(self, authenticate_superuser, create_methodist):
        superuser_token = authenticate_superuser["superuser_token"]
        assert create_methodist["is_metodist"]

        rs = self.response_to_api_url(superuser_token, role="admin")
        assert rs.status_code == 200

        for user in rs.json()["results"]:
            assert user["is_superuser"] is True

        rs2 = self.response_to_api_url(superuser_token, role="metodist")
        for user in rs2.json()["results"]:
            assert user["is_metodist"] is True

    def test_check_user_page(self, authenticate_superuser, create_user, create_teacher):
        superuser_token = authenticate_superuser["superuser_token"]
        teacher = create_teacher

        not_teacher = create_user["user"]
        rs = self.response_to_api_url(superuser_token)
        assert rs.status_code == 200

        page_url = f"{host}/api/users/user/{teacher['id']}"
        rs2 = requests.get(page_url, headers={"Authorization": f"Token {superuser_token}"})
        assert rs2.json()["study_groups"] == ["stub group 1", "stub group 2", "stub group 3"]
        assert rs2.json()["study_courses"] == ["stub course 1", "stub course 2", "stub course 3"]
        assert rs2.status_code == 200

        page_url = f"{host}/api/users/user/{not_teacher['id']}"
        rs2 = requests.get(page_url, headers={"Authorization": f"Token {superuser_token}"})
        assert rs2.json()["study_groups"] is None
        assert rs2.json()["study_courses"] is None
        assert rs2.status_code == 200
