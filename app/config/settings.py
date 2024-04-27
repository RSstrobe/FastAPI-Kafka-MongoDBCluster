"""
Django settings for config project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from split_settings.tools import include

from .components import installed_apps, middleware

LOCALE_PATHS = ["movies/locale"]

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

include(
    r"components/database.py",
    r"components/installed_apps.py",
    r"components/middleware.py",
    r"components/templates.py",
    r"components/passwords.py",
    r"components/auth.py",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", False)

AUTH_API_HOST = os.environ.get("AUTH_API_HOST")
AUTH_API_PORT = os.environ.get("AUTH_API_PORT")
AUTH_API_LOGIN_URL = AUTH_API_HOST + ":" + AUTH_API_PORT + "/auth/login/"
AUTH_API_VERIFY_ROLE_URL = AUTH_API_HOST + ":" + AUTH_API_PORT + "/auth/roles/verify/"

# installed_apps
if DEBUG:
    installed_apps.INSTALLED_APPS.append("debug_toolbar")
    middleware.MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    ] + middleware.MIDDLEWARE

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
]

# Application definition

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
INTERNAL_IPS = ["0.0.0.0", "::1"]
