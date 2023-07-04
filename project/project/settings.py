import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

from dotenv import find_dotenv, load_dotenv

from rest_framework.settings import api_settings

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG_MODE", "False")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

PROJECT_APPS = ["accounts.apps.AccountsConfig"]

OTHER_APPS = [
    "axes",
    "knox",
    "djoser",
    "drf_spectacular",
    "rest_framework",
]

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + OTHER_APPS

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "accounts.backends.CustomModelBackend",
]

AXES_ENABLED = True
AXES_FAILURE_LIMIT = 3
AXES_ONLY_USER_FAILURE = True
AXES_LOCKOUT_PARAMETERS = [["username"]]
AXES_RESET_ON_SUCCESS = True
AXES_SUPERUSER_CHECK_FORM_FIELD = ["is_superuser"]
AXES_COOLOFF_TIME = None
AXES_USER_USER_AGENT = False
AXES_BEHIND_REVERSE_PROXY = False

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

DATABASES = {
    "default":
        dj_database_url.parse(
            os.getenv("PRIMARY_DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "accounts.validators.PassValidator",
    },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Minsk"

USE_I18N = True

USE_TZ = True

STATIC_URL = "back_static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",),
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

DJOSER = {
    "SERIALIZERS": {
        "user_create": "accounts.serializers.CreateUserSerializer",
        "user": "accounts.serializers.CustomUserSerializer",
        "current_user": "accounts.serializers.CustomUserSerializer",
    },
    "PERMISSIONS": {
        "user": ["accounts.permissions.CurrentUserOrSuperUser"],
        "user_create": ["accounts.permissions.IsSuperUser"],
        "user_delete": ["accounts.permissions.IsSuperUser"]
    },
    "PASSWORD_RESET_CONFIRM_URL": "#/password/reset/confirm/{uid}/{token}",
}

REST_KNOX = {
    "SECURE_HASH_ALGORITHM": "cryptography.hazmat.primitives.hashes.SHA512",
    "AUTH_TOKEN_CHARACTER_LENGTH": 64,
    "TOKEN_TTL": timedelta(hours=24),
    "USER_SERIALIZER": "knox.serializers.UserSerializer",
    "TOKEN_LIMIT_PER_USER": None,
    "AUTO_REFRESH": False,
    "MIN_REFRESH_INTERVAL": 60,
    "AUTH_HEADER_PREFIX": "Token",
    "EXPIRY_DATETIME_FORMAT": api_settings.DATETIME_FORMAT,
    "TOKEN_MODEL": "knox.AuthToken",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Backend CRM",
    "DESCRIPTION": f"""ИНФОРМАЦИЯ ПО ПРОЕКТУ
    \nВремя жизни токена: {REST_KNOX['TOKEN_TTL']}
    \nФормат токена в header:
    \n\tAuthorization: Token <token>
    """,
    "VERSION": "1.4.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "PREPROCESSING_HOOKS": ["project.scheme.custom_preprocessing_hook"],
}
