from .api_requests import update_users_data, create_token


class TestUpdateUser:
    def test_update_teacher(self, teacher, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]

        data = {
            "username": "test_updated_teacher",
            "password": "UpdatedPas1",
            "email": "updateemail@example.com",
            "is_metodist": True,
        }

        rs = update_users_data(method="put", user_id=teacher["id"], superuser_token=superuser_token, **data)

        assert rs.status_code == 200

        updated_data = rs.json()

        assert updated_data["username"] == data["username"]
        assert updated_data["email"] == data["email"]
        assert updated_data["is_metodist"] == data["is_metodist"]

    def test_update_teacher_with_wrong_date(self, teacher, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]

        data = {
            "username": "test_updated_teacher",
            "password": "UpdatedPas1",
            "email": "updateemail@example.com",
            "is_metodist": True,
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "middle_name": "UpdatedMiddleName",
        }

        rs = update_users_data(method="put", user_id=teacher["id"], superuser_token=superuser_token, **data)

        assert rs.status_code == 200

        updated_data = rs.json()

        assert updated_data["username"] == data["username"]
        assert updated_data["email"] == data["email"]
        assert updated_data["is_metodist"] == data["is_metodist"]

        assert updated_data["first_name"] == teacher["first_name"]
        assert updated_data["last_name"] == teacher["last_name"]
        assert updated_data["middle_name"] == teacher["middle_name"]

        rs2 = update_users_data(
            method="patch", user_id=teacher["id"], superuser_token=superuser_token, first_name=data["first_name"]
        )

        assert rs2.status_code == 200
        assert updated_data["first_name"] == teacher["first_name"]

    def test_update_not_teacher(self, user_data, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        user = user_data["user"]

        data = {
            "username": "test_updated_teacher",
            "is_metodist": True,
            "first_name": "UpdatedFirstName",
            "last_name": "UpdatedLastName",
            "middle_name": "UpdatedMiddleName",
            "email": "updateemail@example.com",
        }

        rs = update_users_data(method="patch", user_id=user["id"], superuser_token=superuser_token, **data)

        updated_data = rs.json()
        assert rs.status_code == 200

        assert updated_data["username"] == data["username"]
        assert updated_data["email"] == data["email"]
        assert updated_data["is_metodist"] == data["is_metodist"]
        assert updated_data["first_name"] == data["first_name"]
        assert updated_data["last_name"] == data["last_name"]
        assert updated_data["middle_name"] == data["middle_name"]

    def test_update_password(self, user_data, teacher, superuser_credentials):
        superuser_token = superuser_credentials["superuser_token"]
        user = user_data["user"]

        data = {"password": "UpdatedPas1"}

        update_user_rs = update_users_data(method="patch", user_id=user["id"], superuser_token=superuser_token, **data)
        get_user_token_rs = create_token(username=update_user_rs.json()["username"], password=data["password"])

        assert get_user_token_rs.status_code == 200
        assert "auth_token" in get_user_token_rs.json()

        update_teacher_rs = update_users_data(
            method="patch", user_id=teacher["id"], superuser_token=superuser_token, **data
        )
        get_teacher_token_rs = create_token(username=update_teacher_rs.json()["username"], password=data["password"])

        assert get_teacher_token_rs.status_code == 200
        assert "auth_token" in get_teacher_token_rs.json()
