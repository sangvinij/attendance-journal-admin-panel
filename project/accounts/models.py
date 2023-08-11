import os

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from dotenv import find_dotenv, load_dotenv

import redis
from redis.exceptions import ConnectionError

load_dotenv(find_dotenv())

from .managers import MssqlManager, UserManager


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
    email = models.EmailField("email", null=True, blank=True)
    first_name = models.CharField("имя", max_length=255, null=True, blank=True)
    last_name = models.CharField("фамилия", max_length=255, null=True, blank=True)
    middle_name = models.CharField("отчество", max_length=255, null=True, blank=True)
    id_crm = models.IntegerField("ID в системе CRM", unique=True, null=True, blank=True)
    is_active = models.BooleanField("is_active", null=True, blank=True)
    is_staff = models.BooleanField("is_staff", default=False)
    is_verified = models.BooleanField("is_verified", default=False)
    is_superuser = models.BooleanField("администратор", default=False)
    is_teacher = models.BooleanField("преподаватель", default=False)
    is_metodist = models.BooleanField("методист", default=False)
    date_added = models.DateTimeField("дата создания", auto_now_add=True)
    last_update = models.DateTimeField("дата последнего обновления", auto_now=True)
    study_fields = models.ManyToManyField(StudyField, verbose_name="направления", blank=True)
    study_groups = models.TextField("группы", null=True, blank=True)
    study_courses = models.TextField("курсы", null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "middle_name"]

    username.error_messages = {"unique": "Такой логин уже существует. Измените логин."}

    def __str__(self):
        return self.username

    def last_sync_func(self):
        redis_db_url = os.getenv("REDIS_DSN")
        storage = redis.from_url(redis_db_url)
        try:
            data = storage.get("last_sync")
        except ConnectionError:
            return None
        if data is None:
            return None
        return data.decode()

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"


class Prepod(models.Model):
    id = models.AutoField(db_column="ID", primary_key=True)
    fullname = models.CharField("ФИО", db_column="Prepod", max_length=255)
    email = models.CharField("email", db_column="Email", max_length=255)
    direction = models.CharField("Направления", db_column="Napravlenie", max_length=255)

    objects = MssqlManager()

    def __str__(self):
        return self.fullname

    class Meta:
        managed = False
        db_table = "tblPrepods"


class Group(models.Model):
    id = models.AutoField(db_column="ID", primary_key=True)
    study_groups = models.CharField("Группа", db_column="GroupName", unique=True, max_length=255, blank=True, null=True)
    course_id = models.IntegerField("id курса", db_column="KursID", blank=True, null=True)
    teacher_fullname = models.CharField("Преподаватель", db_column="Prepod", max_length=255)
    teacher_id = models.IntegerField("id преподавателя", db_column="PrepodId", blank=True, null=True)
    study_courses = models.CharField("Курс", db_column="Kurs", max_length=255)
    direction = models.CharField("Направления", db_column="Napravlenie", max_length=255)

    objects = MssqlManager()

    def __str__(self):
        return f"{self.teacher_fullname}, {self.group_name}, {self.course}"

    class Meta:
        managed = False
        db_table = "tblGroups"
