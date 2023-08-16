from django.urls import include, path

from knox import views as knox_views

from rest_framework.routers import DefaultRouter

from .views import LoginView, MsSqlTableViewSet, RefreshPoint, StudyFieldViewSet, UserViewSet

mssql_router = DefaultRouter()
mssql_router.register(r"mssql", MsSqlTableViewSet)

router = DefaultRouter()

users_router = DefaultRouter()
users_router.register("users", UserViewSet)
users_router.register("study_fields", StudyFieldViewSet)

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"auth/", include(users_router.urls)),
    path(r"auth/token/login/", LoginView.as_view(), name="knox_login"),
    path(r"auth/token/logout/", knox_views.LogoutView.as_view(), name="knox_logout"),
    path(r"auth/token/logoutall/", knox_views.LogoutAllView.as_view(), name="knox_logoutall"),
    path(r"api/", include(mssql_router.urls)),
    path(r"api/refresh/", RefreshPoint.as_view()),
]
