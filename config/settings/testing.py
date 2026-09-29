"""Testing settings — fast, hermetic; Postgres only when opted in explicitly.

`base.py` read_env() copies .env values into os.environ, which would make every
test run point at the local dev Postgres (and fail when it's down). Capture the
parent-process DATABASE_URL BEFORE importing base: tests use sqlite unless
DATABASE_URL was exported before Python started (e.g. `DATABASE_URL=... pytest`).
"""

import os

_PARENT_DATABASE_URL = os.environ.get("DATABASE_URL")

from .base import *  # noqa: E402,F403

DEBUG = False
SECRET_KEY = "django-insecure-test-only"

_test_env = environ.Env(  # noqa: F405
    DATABASE_URL=(str, _PARENT_DATABASE_URL or "sqlite://"),
)
DATABASES = {"default": _test_env.db("DATABASE_URL")}

MAILERS = {
    "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"},
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
