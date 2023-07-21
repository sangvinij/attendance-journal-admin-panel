from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **other_fields):
        if not username:
            raise ValueError("username is required!")
        user = self.model(username=username, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **other_fields):
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_superuser", True)
        other_fields.setdefault("is_active", True)

        if other_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")

        if other_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")
        user = self.create_user(username, password=password, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class MssqlManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().using("mssql")
