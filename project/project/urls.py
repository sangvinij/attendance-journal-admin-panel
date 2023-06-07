from django.contrib import admin
from django.urls import include, path
from project.yasg import urlpatterns as dock_urls

urlpatterns = [
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
]

urlpatterns += dock_urls
