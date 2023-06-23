from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models


from .managers import UserManager


class StudyField(models.Model):
    study_field = models.CharField(verbose_name="направление", max_length=255, null=True, blank=True)
    short_study_field = models.CharField(verbose_name="напр.", max_length=255, null=True, blank=True)

    def __str__(self):
        return self.study_field

    class Meta:
        verbose_name = "направление"
        verbose_name_plural = "направления"


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("username", max_length=255, unique=True)
    first_name = models.CharField("имя", max_length=255, null=True, blank=True)
    last_name = models.CharField("фамилия", max_length=255, null=True, blank=True)
    middle_name = models.CharField("отчество", max_length=255, null=True, blank=True)
    is_active = models.BooleanField("is_active", default=True)
    is_staff = models.BooleanField("is_staff", default=False)
    is_verified = models.BooleanField("is_verified", default=False)
    is_superuser = models.BooleanField("администратор", default=False)
    is_teacher = models.BooleanField("преподаватель", default=False)
    is_metodist = models.BooleanField("методист", default=False)
    date_added = models.DateTimeField("дата создания", auto_now_add=True)
    last_update = models.DateTimeField("дата последнего обновления", auto_now=True)
    email = models.EmailField("email", null=True, blank=True)
    study_fields = models.ManyToManyField(StudyField, verbose_name="направления", blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name"]

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
