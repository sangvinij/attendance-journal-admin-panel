from axes.models import AccessAttempt

from django.contrib.auth import authenticate

from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import exceptions, serializers

from .models import StudyField, User


class CreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "is_superuser", "is_metodist", "is_teacher")


class StudyFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyField
        fields = ["study_field", "short_study_field"]


class AuthSerializer(serializers.Serializer):
    default_error_messages = {"no_active_account": "Неверное имя пользователя и/или пароль"}
    username = serializers.CharField(trim_whitespace=False)
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), username=username, password=password)

        if not user:
            msg = self.default_error_messages["no_active_account"]
            raise exceptions.AuthenticationFailed(detail=msg, code="authentication")

        AccessAttempt.objects.filter(username=username).delete()
        attrs["user"] = user
        return attrs


class CustomUserSerializer(UserSerializer):
    study_fields = StudyFieldSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "middle_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_teacher",
            "is_metodist",
            "study_fields",
            "date_added",
            "last_update",
        )
