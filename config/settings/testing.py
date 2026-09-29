"""Testing settings — fast, hermetic; Postgres only when opted in explicitly.

`base.py` read_env() copies .env values into os.environ, so os.environ cannot be
trusted here (pass-3 review: Env.db() reads os.environ first, constructor
defaults only apply to keys that are absent). DATABASE_URL is therefore captured
from the parent process BEFORE importing base and passed DIRECTLY to
db_url_config(): tests use sqlite unless DATABASE_URL was exported before Python
started (e.g. `DATABASE_URL=... pytest` — the documented opt-in).
"""

import os

_PARENT_DATABASE_URL = os.environ.get("DATABASE_URL")

from .base import *  # noqa: E402,F403

DEBUG = False
SECRET_KEY = "django-insecure-test-only"

DATABASES = {"default": environ.Env.db_url_config(_PARENT_DATABASE_URL or "sqlite://")}  # noqa: F405

MAILERS = {
    "default": {"BACKEND": "django.core.mail.backends.locmem.EmailBackend"},
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
