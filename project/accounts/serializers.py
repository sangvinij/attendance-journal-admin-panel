from djoser.serializers import UserCreateSerializer, TokenCreateSerializer

from .models import User

from rest_framework import serializers


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name")


class CustomTokenCreateSerializer(TokenCreateSerializer):
    default_error_messages = {
        "invalid_credentials": "Неверное имя пользователя и/или пароль",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"] = serializers.CharField(trim_whitespace=False)
        self.fields["password"] = serializers.CharField(trim_whitespace=False)
