"""Settings behavior regression tests (pass-3 review blocking fix)."""

import os

from django.conf import settings
from environ import Env

from config.settings import testing as testing_settings


def test_database_hermetic_by_default() -> None:
    """DATABASES derives from the PARENT-process DATABASE_URL only.

    base.py read_env() leaks .env values into os.environ; the test settings must
    ignore that and use sqlite unless DATABASE_URL was explicitly exported
    before Python started. Deterministic regardless of .env contents.
    """
    parent_url = getattr(testing_settings, "_PARENT_DATABASE_URL", None)
    expected = Env.db_url_config(parent_url or "sqlite://")["ENGINE"]
    assert settings.DATABASES["default"]["ENGINE"] == expected


def test_runtime_env_leak_is_ignored() -> None:
    """When the parent didn't export DATABASE_URL, the .env leak must be ignored."""
    if testing_settings._PARENT_DATABASE_URL is None and "DATABASE_URL" in os.environ:  # noqa: SLF001
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
