"""App config for bench: the supply side — freelancer profile, VA bench, shared Capability."""


from django.apps import AppConfig


class BenchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bench"
    verbose_name = "Bench — freelancer & VAs"
