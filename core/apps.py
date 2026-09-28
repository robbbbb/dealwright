"""Core app config."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app: shared/home surfaces; domain apps register alongside."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
