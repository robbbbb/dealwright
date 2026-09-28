"""Testing settings — fast, hermetic; Postgres if DATABASE_URL is set, else in-memory sqlite."""

import environ

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "django-insecure-test-only"

_test_env = environ.Env(DATABASE_URL=(str, "sqlite://"))
DATABASES = {"default": _test_env.db("DATABASE_URL")}

MAILERS = {
    "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"},
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
