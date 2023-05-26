from django.urls import include, path, re_path

from rest_framework.routers import DefaultRouter

from accounts.views import CustomTokenCreateView

router = DefaultRouter()

urlpatterns = [
    path(r"", include(router.urls)),
    path(r"auth/", include("djoser.urls")),
    path("auth/token/login/", CustomTokenCreateView.as_view(), name="token_obtain_pair"),
    re_path(r"auth/", include("djoser.urls.authtoken")),
]
