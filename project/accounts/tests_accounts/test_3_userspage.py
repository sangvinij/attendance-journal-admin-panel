from .api_requests import host, get_detailed_info_about_user

import requests


class TestUserModel:
    API_URL = f"{host}/auth/users/"

    def response_to_api_url(self, token, **kwargs):
        rs = requests.get(self.API_URL, params=kwargs, headers={"Authorization": f"Token {token}"})
        return rs

    def test_unauthorized_request_to_endpoint(self):
        rs = self.response_to_api_url(token="")
        assert rs.status_code == 401

    def test_user_list_endpoint_accessible_for_superuser(self, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        rs = self.response_to_api_url(superuser_token)
        assert rs.status_code == 200

    def test_user_list_endpoint_inaccessible_for_non_superuser(self, user_data):
        token = user_data["token"]
        rs = self.response_to_api_url(token)
        assert rs.status_code == 404

    def test_user_list_pagination(self, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        rs = self.response_to_api_url(superuser_token)
        assert "next" in rs.json()
        assert "previous" in rs.json()

    def test_user_list_filter_by_role(self, superuser_credentials, methodist):
        superuser_token = superuser_credentials["superuser_token"]
        assert methodist["is_metodist"]

        rs = self.response_to_api_url(superuser_token, role="admin")
        assert rs.status_code == 200

        for user in rs.json()["results"]:
            assert user["is_superuser"] is True

        rs2 = self.response_to_api_url(superuser_token, role="metodist")
        for user in rs2.json()["results"]:
            assert user["is_metodist"] is True

    def test_check_user_page(self, superuser_credentials, user_data, teacher):
        superuser_token = superuser_credentials["superuser_token"]

        not_teacher = user_data["user"]
        rs = self.response_to_api_url(superuser_token)
        assert rs.status_code == 200

        rs2 = get_detailed_info_about_user(user_id=teacher["id"], token=superuser_token)

        assert rs2.json()["study_groups"] is None
        assert rs2.json()["study_courses"] is None
        assert rs2.status_code == 200

        rs3 = get_detailed_info_about_user(user_id=not_teacher["id"], token=superuser_token)
        assert rs3.json()["study_groups"] is None
        assert rs3.json()["study_courses"] is None
        assert rs3.status_code == 200

    def test_get_access_to_invalid_id(self, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        rs = get_detailed_info_about_user(user_id=9_000_000, token=superuser_token)
        assert rs.status_code == 404
