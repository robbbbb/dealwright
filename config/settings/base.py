"""Shared settings — everything env-driven, per AGENTS.md (secrets from env, never chat)."""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# .env is a local-dev convenience only; production values come from Railway config.
_env_file = BASE_DIR / ".env"
if _env_file.is_file():
    environ.Env.read_env(_env_file)

env = environ.Env(
    DJANGO_SECRET_KEY=(str, "django-insecure-dev-only-change-me"),
    DJANGO_DEBUG=(bool, False),
    DATABASE_URL=(str, "sqlite:///db.sqlite3"),
    DJANGO_ALLOWED_HOSTS=(list, []),
    DJANGO_CSRF_TRUSTED_ORIGINS=(list, []),
    GOOGLE_OAUTH_CLIENT_ID=(str, ""),
    GOOGLE_OAUTH_SECRET=(str, ""),
)

SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Auth (Q13: django-allauth, email/password + Google social + TOTP MFA)
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",  # TOTP + recovery codes; templates per docs/mockups/auth-mockup.html
    # Dealwright
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL"),
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SITE_ID = 1

# Q13: email/password + Google; verification enforced in production (see production.py).
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "optional"
# Custom signup form: full name + terms checkbox (auth mockup, frame 2).
ACCOUNT_FORMS = {"signup": "core.forms.SignupForm"}
LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"

# Q13: forgot-password copy is anti-enumeration; reset link single-use (allauth), 24h expiry.
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24

# Q13: MFA — TOTP + one-time recovery codes (auth mockup frames 6–7). WebAuthn not in scope.
# SUPPORTED_TYPES default is already ["recovery_codes", "totp"].
MFA_RECOVERY_CODES_SHOW_ONCE = True  # codes shown once, download at reveal time

# Password hint on the signup/reset screens says "at least 10 characters".
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Google is wired only when both credentials are present (SOCIALACCOUNT_PROVIDERS
# APP form — no DB SocialApp rows needed). The provider app must be installed for
# the registry to expose it (provider_login_url / template Google button).
SOCIALACCOUNT_PROVIDERS = {}
if env("GOOGLE_OAUTH_CLIENT_ID") and env("GOOGLE_OAUTH_SECRET"):
    INSTALLED_APPS += ["allauth.socialaccount.providers.google"]  # noqa: F405
    SOCIALACCOUNT_PROVIDERS["google"] = {
        "APP": {
            "client_id": env("GOOGLE_OAUTH_CLIENT_ID"),
            "secret": env("GOOGLE_OAUTH_SECRET"),
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }

# PH-anchored product (PHP pricing, PH VA bench).
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
