from django.db.models import Case, Min, OuterRef, Q, Subquery, When
from django.utils import timezone
from django.utils.decorators import method_decorator

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

from rest_framework.decorators import action
from rest_framework import filters, permissions, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .enums import StudyFieldOrder
from .models import StudyField, User
from .permissions import IsSuperUser
from .serializers import AuthSerializer, CustomUserSerializer, StudyFieldSerializer


class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AuthSerializer

    @swagger_auto_schema(
        operation_summary='Get bearer token',
        operation_description='''Return bearer token by login and password. Login and password send in JSON'''
    )
    def post(self, request, format=None):
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


@method_decorator(
    name='list',
    decorator=swagger_auto_schema(
        operation_summary='Get list users',
        operation_description='''Return list with all users by get-request. With empty query return list all the users. 
        In query might set: page, page_size, filter, sort_by.
        ''',
        manual_parameters=[
            openapi.Parameter('role', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
            openapi.Parameter('sort_by', in_=openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ]
    )
)
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ["username", "first_name", "last_name"]
    pagination_class = CustomUserPagination
    permission_classes = [IsSuperUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role", None)
        sort_by = self.request.query_params.get("sort_by", None)

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


class StudyFieldViewSet(viewsets.ModelViewSet):
    queryset = StudyField.objects.all()
    serializer_class = StudyFieldSerializer
    permission_classes = [IsSuperUser]
