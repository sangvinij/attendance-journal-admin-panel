from axes.models import AccessAttempt

from django.contrib.auth import authenticate

from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import exceptions, serializers

from .models import StudyField, User


class CreateUserSerializer(UserCreateSerializer):
    is_active = serializers.BooleanField(default=True)
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "middle_name",
            "is_superuser",
            "is_teacher",
            "is_metodist",
            "is_active",
            "email",
            "date_added",
            "last_update",
        )


class StudyFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyField
        fields = ["study_field", "short_study_field"]


class AuthSerializer(serializers.Serializer):
    default_error_messages = {"invalid_credentials": "Неверное имя пользователя и/или пароль"}
    username = serializers.CharField(trim_whitespace=False)
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(request=self.context.get("request"), username=username, password=password)

        if not user:
            msg = self.default_error_messages["invalid_credentials"]
            raise exceptions.AuthenticationFailed(detail=msg, code="authentication")

        AccessAttempt.objects.filter(username=username).delete()
        attrs["user"] = user
        return attrs


class CustomUserSerializer(UserSerializer):
    study_fields = StudyFieldSerializer(many=True, read_only=True)
    study_groups = serializers.SerializerMethodField(method_name='get_study_groups')
    study_courses = serializers.SerializerMethodField(method_name='get_study_courses')

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
            "email",
            "study_groups",
            "study_courses",
        )

    @staticmethod
    def get_study_groups(user: User):
        if user.is_teacher:
            study_groups = ['stub group 1', 'stub group 2', 'stub group 3']
            return study_groups
        return None

    @staticmethod
    def get_study_courses(user: User):
        if user.is_teacher:
            study_courses = ['stub course 1', 'stub course 2', 'stub course 3']
            return study_courses
        return None
