import os
from datetime import datetime
from itertools import groupby

from django.db.models import Q
from django.db.utils import IntegrityError, InterfaceError, OperationalError
from django.http import JsonResponse
from django.utils import timezone

from djoser.conf import settings
from djoser.views import UserViewSet as DjoserViewSet

from dotenv import find_dotenv, load_dotenv

from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

import pytz

import redis
from redis.exceptions import ConnectionError

from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from transliterate import translit

from .enums import StudyFieldOrder
from .models import Group, Prepod, StudyField, User
from .permissions import IsSuperUser
from .serializers import AuthSerializer, PrepodsSerializer, StudyFieldSerializer


load_dotenv(find_dotenv())


@extend_schema_view(post=extend_schema(summary="Получить токен по логину и паролю"))
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthSerializer

    def post(self, request, form=None):
        serializer = self.serializer_class(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                return Response(
                    {"error": "Maximum amount of tokens allowed per user exceeded."}, status=status.HTTP_403_FORBIDDEN
                )
        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(user, token_ttl)
        return Response(
            {
                "expiry": self.format_expiry_datetime(instance.expiry),
                "auth_token": token,
            }
        )


class CustomUserPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"


@extend_schema_view(
    list=extend_schema(
        summary="Получить список пользователей по токену",
        parameters=[
            OpenApiParameter(name="role", location=OpenApiParameter.QUERY, description="фильтр"),
            OpenApiParameter(name="sort_by", location=OpenApiParameter.QUERY, description="сортировка"),
        ],
    )
)
class UserViewSet(DjoserViewSet):
    queryset = User.objects.all()
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]
    pagination_class = CustomUserPagination

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if settings.HIDE_USERS and self.action == "list" and not user.is_superuser:
            queryset = queryset.filter(pk=user.pk)
        role = self.request.query_params.get("role")
        sort_by = self.request.query_params.get("sort_by")

        if role is not None:
            queryset = queryset.filter(Q(is_superuser=True) | Q(is_teacher=True) | Q(is_metodist=True))

            if role == "admin":
                queryset = queryset.filter(is_superuser=True)
            elif role == "teacher":
                queryset = queryset.filter(is_teacher=True)
            elif role == "metodist":
                queryset = queryset.filter(is_metodist=True)

        if sort_by == "last_name":
            queryset = queryset.order_by("-last_name")
        elif sort_by == "study_field":
            sorted_users = []
            study_fields_order = list(StudyFieldOrder)
            for study_field in study_fields_order:
                users = queryset.filter(study_fields__study_field=study_field.value)
                sorted_users.extend(users)
            return sorted_users

        return queryset

    def get_serializer_class(self):
        if self.action == "update" or self.action == "partial_update":
            return settings.SERIALIZERS.user_update
        return super().get_serializer_class()


class StudyFieldViewSet(viewsets.ModelViewSet):
    queryset = StudyField.objects.all()
    serializer_class = StudyFieldSerializer
    permission_classes = [IsSuperUser]


class MsSqlTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prepod.objects.all()
    serializer_class = PrepodsSerializer
    permission_classes = [IsSuperUser]


class RefreshPoint(APIView):
    permission_classes = [IsSuperUser]

    class Names:
        def __init__(self, fullname):
            list_names = fullname.split()
            if len(list_names) > 2:
                self.last_name = list_names[0]
                self.first_name = list_names[1]
                self.middle_name = list_names[2]
            else:
                self.last_name = list_names[0]
                self.first_name = list_names[1]
                self.middle_name = ""

    class Groups:
        def __init__(self, groups):
            self.study_groups = []
            for group in groups:
                self.study_groups += [group.study_groups]
            self.study_courses = []
            for course in groups:
                if course.study_courses:
                    self.study_courses += [course.study_courses]
            self.study_courses = [el for el, _ in groupby(self.study_courses)]

    def username_generator(self, names, id_crm: int | str):
        first_name = translit(names.first_name[0], language_code="ru", reversed=True)
        last_name = translit(names.last_name, language_code="ru", reversed=True)
        return first_name + last_name + "_" + str(id_crm)

    def user_object_create(self, teacher, groups):
        groups_of_teacher = self.Groups(groups)
        names = self.Names(teacher.fullname)
        email = teacher.email.split("; ", 1)[0]
        id_crm = teacher.prepod_id
        username = self.username_generator(names, id_crm)

        new_teacher = User(
            username=username,
            first_name=names.first_name,
            last_name=names.last_name,
            middle_name=names.middle_name,
            email=email,
            is_teacher=1,
            id_crm=id_crm,
            study_groups=groups_of_teacher.study_groups,
            study_courses=groups_of_teacher.study_courses,
        )
        return new_teacher

    def user_object_upgrade(self, teacher, user, groups):
        groups_of_teacher = self.Groups(groups)
        names = self.Names(teacher.fullname)
        email = teacher.email.split("; ", 1)[0]
        user.first_name = names.first_name
        user.last_name = names.last_name
        user.middle_name = names.middle_name
        user.study_groups = groups_of_teacher.study_groups
        user.study_courses = groups_of_teacher.study_courses
        if email:
            user.email = email
        return user

    def users_are_equal(self, teacher_journal, teacher_crm, groups):
        inequality = 0
        groups_of_teacher_crm = self.Groups(groups)
        names = self.Names(teacher_crm.fullname)

        inequality += names.first_name != teacher_journal.first_name
        inequality += names.last_name != teacher_journal.last_name
        inequality += names.middle_name != teacher_journal.middle_name
        inequality += str(teacher_journal.study_groups) != str(groups_of_teacher_crm.study_groups)
        inequality += str(teacher_journal.study_courses) != str(groups_of_teacher_crm.study_courses)
        if teacher_crm.email and teacher_journal.email:
            inequality += teacher_crm.email.split("; ", 1)[0] != teacher_journal.email
        return not inequality

    def get(self, request):
        all_teachers_crm = Prepod.objects.all()
        all_teachers_journal = User.objects.filter(is_teacher=1)
        teacher_groups = Group.objects.all()
        new_teachers = []
        update_teachers = []
        redis_db_url = os.getenv("REDIS_DSN")
        storage = redis.from_url(redis_db_url)

        try:
            for teacher in all_teachers_crm:
                if len(teacher.fullname.split()) < 2:
                    continue

                groups = teacher_groups.filter(teacher_id=teacher.prepod_id)
                if not all_teachers_journal.filter(id_crm=teacher.prepod_id).exists():
                    if groups.filter(teacher_id=teacher.prepod_id).exists():
                        new_teacher = self.user_object_create(teacher, groups)
                        new_teachers.append(new_teacher)
                else:
                    user_for_upgrade = all_teachers_journal.get(id_crm=teacher.prepod_id)
                    if not self.users_are_equal(user_for_upgrade, teacher, groups):
                        upgraded_teacher = self.user_object_upgrade(teacher, user_for_upgrade, groups)
                        update_teachers.append(upgraded_teacher)

        except (OperationalError, InterfaceError, IntegrityError) as error:
            return JsonResponse({"Error": str(error)}, safe=False, status=418)

        User.objects.bulk_create(new_teachers)
        User.objects.bulk_update(
            update_teachers,
            ["first_name", "last_name", "middle_name", "email", "study_groups", "study_courses", "is_active"],
        )
        time_now = datetime.now(pytz.timezone("Europe/Minsk")).strftime("%H:%M %d-%m-%Y")
        try:
            storage.set("last_sync", time_now)
        except ConnectionError:
            return JsonResponse({"last_sync": "null"})
        return JsonResponse({"last_sync": time_now})
