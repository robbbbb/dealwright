"""Production settings — Railway. Strict: missing env vars fail at boot, never silently."""

import environ

from .base import *  # noqa: F403

_prod_env = environ.Env()

SECRET_KEY = _prod_env.str("DJANGO_SECRET_KEY")  # type: ignore[assignment]
DATABASES = {"default": _prod_env.db("DATABASE_URL")}

DEBUG = False
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")  # noqa: F405
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")  # noqa: F405

# Railway terminates TLS at the proxy.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = _prod_env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 315_36000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Transactional email (provider choice is open — see docs/backlog.md).
# Django 6.1 MAILERS form; env-driven so the provider is a deploy-time decision.
_prod_email_options = {
    "host": _prod_env.str("EMAIL_HOST"),
    "port": _prod_env.int("EMAIL_PORT", default=587),
    "username": _prod_env.str("EMAIL_HOST_USER", default=""),
    "password": _prod_env.str("EMAIL_HOST_PASSWORD", default=""),
    "use_tls": _prod_env.bool("EMAIL_USE_TLS", default=True),
}
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
        "OPTIONS": _prod_email_options,
    },
}
DEFAULT_FROM_EMAIL = _prod_env.str(
    "DEFAULT_FROM_EMAIL", default="Dealwright <no-reply@dealwright.io>"
)

# Q13: email verification required before proposals can send/share.
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
