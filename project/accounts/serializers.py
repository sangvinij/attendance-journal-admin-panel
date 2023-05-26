from djoser.serializers import UserCreateSerializer, TokenCreateSerializer

from .models import User


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name")


class CustomTokenCreateSerializer(TokenCreateSerializer):
    default_error_messages = {
        "invalid_credentials": "Неверное имя пользователя и/или пароль.",
    }
