from jsonschema import validate


from .api_requests import (
    create_token,
    delete_token,
    delete_user,
    get_detailed_info_about_user,
    get_info_about_current_user,
    register_user,
    update_users_data,
)
from .schemas import CREATE_USER_SCHEMA


class TestLogin:
    username = "test_username2"
    password = "Admin1337"

    def test_superuser_exists(self, superuser_credentials):
        superuser_username = superuser_credentials["superuser_username"]
        superuser_token = superuser_credentials["superuser_token"]
        rs = get_info_about_current_user(superuser_token)
        assert rs.status_code == 200
        assert rs.json()["username"] == superuser_username

    def test_create_user(self, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        superuser_password = superuser_credentials["superuser_password"]
        rs = register_user(
            username=self.username,
            password=self.password,
            first_name="TestName",
            last_name="TestLastName",
            middle_name="TestMiddleName",
            is_metodist=True,
            is_active=True,
            email="example@example.com",
            superuser_token=superuser_token,
        )
        assert rs.status_code == 400

        created_user_data = rs.json()
        validate(created_user_data, CREATE_USER_SCHEMA)
        assert created_user_data["username"] == self.username

        delete_user(
            user_id=created_user_data["id"], superuser_password=superuser_password, superuser_token=superuser_token
        )

    def test_get_token_with_wrong_and_correct_data(self, user_data):
        username = user_data["username"]
        password = user_data["password"]

        failed_rs = create_token(username=username, password=f"wrong {password}")
        assert failed_rs.status_code == 401
        assert "auth_token" not in failed_rs.json()

        valid_rs = create_token(username=username, password=password)
        assert valid_rs.status_code == 200
        assert "auth_token" in valid_rs.json()

    def test_get_access_to_protected_endpoint(self, user_data):
        token = user_data["token"]
        username = user_data["username"]

        failed_rs = get_info_about_current_user(token="wrong token")
        assert failed_rs.status_code == 401

        valid_rs = get_info_about_current_user(token=token)

        assert valid_rs.status_code == 200
        assert "username" in valid_rs.json()
        assert valid_rs.json()["username"] == username

    def test_delete_token(self, user_data):
        token = user_data["token"]
        get_access_rs = get_info_about_current_user(token=token)
        assert get_access_rs.status_code == 200

        delete_token_rs = delete_token(token)
        assert delete_token_rs.status_code == 204

        final_rs = get_info_about_current_user(token)
        assert final_rs.status_code == 401

    def test_login_with_spaces_in_credentials(self, user_data):
        username = user_data["username"]
        password = user_data["password"]
        rs = create_token(username="\x20" + username, password=password)
        assert rs.status_code == 401
        rs2 = create_token(username=username + "\x20", password=password)
        assert rs2.status_code == 401
        valid_rs = create_token(username=username, password=password)
        assert valid_rs.status_code == 200
        rs3 = create_token(username=username, password="\x20" + password)
        assert rs3.status_code == 401
        rs4 = create_token(username=username, password=password + "\x20")
        assert rs4.status_code == 401
        valid_rs = create_token(username=username, password=password)
        assert "auth_token" in valid_rs.json()

    def test_change_flag_is_active(self, superuser_credentials, user_data):
        superuser_token = superuser_credentials["superuser_token"]

        username = user_data["username"]
        password = user_data["password"]
        user = user_data["user"]

        for _ in range(3):
            create_token(username=username, password=f"wrong {password}")

        get_users_info_rs = get_detailed_info_about_user(superuser_token, user["id"])
        assert get_users_info_rs.status_code == 200
        users_data = get_users_info_rs.json()
        assert users_data["username"] == username
        assert users_data["is_active"] is False

        failed_login_rs = create_token(username, password)
        assert failed_login_rs.status_code == 429

        change_is_active_flag_rs = update_users_data(
            superuser_token=superuser_token, user_id=user["id"], is_active=True
        )

        assert change_is_active_flag_rs.status_code == 200
        updated_users_data = change_is_active_flag_rs.json()
        assert updated_users_data["username"] == username
        assert updated_users_data["is_active"] is True

        valid_login_rs = create_token(username, password)
        assert valid_login_rs.status_code == 200
        assert "auth_token" in valid_login_rs.json()
