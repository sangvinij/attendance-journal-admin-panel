from axes.models import AccessAttempt

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import exceptions, serializers

from .models import Prepod, StudyField, User


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
    last_sync = serializers.CharField(source="last_sync_func", read_only=True)

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
            "email",
            "study_groups",
            "study_courses",
            "date_added",
            "last_update",
            "last_sync",
        )


class PrepodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prepod
        fields = "__all__"


class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False, write_only=True)
    is_active = serializers.BooleanField(default=True)
    is_teacher = serializers.BooleanField(read_only=True)

    TEACHER_FIELDS = {
        "username",
        "password",
        "is_superuser",
        "is_metodist",
        "is_active",
    }

    NOT_TEACHER_FIELDS = {"is_teacher", "first_name", "last_name", "middle_name", "email"}

    united_fields = sorted(TEACHER_FIELDS | NOT_TEACHER_FIELDS)

    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes("update", self, validated_data)
        is_teacher = validated_data.get("is_teacher", instance.is_teacher)
        password = validated_data.pop("password", None)

        fields = self.TEACHER_FIELDS if is_teacher else self.united_fields

        for attr, value in validated_data.items():
            if attr in fields:
                setattr(instance, attr, value)

        if password:
            instance.set_password(password)
            try:
                validate_password(password, instance)
            except ValidationError as e:
                raise serializers.ValidationError({"password": e.messages})

        current_user = self.context["request"].user

        if current_user.is_superuser and current_user.pk == instance.pk and "is_active" in validated_data:
            raise serializers.ValidationError({"is_active": "Вы не можете изменить флаг is_active для себя"})

        instance.save()
        return instance

    class Meta:
        model = User
        fields = [
            "id",
        ]

    Meta.fields.extend(united_fields)
