"""App config for team: the supply side — freelancer profile, Team roster, shared Capability."""


from django.apps import AppConfig


class TeamConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "team"
    verbose_name = "Team — freelancer & VAs"
