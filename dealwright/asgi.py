"""ASGI config — production entrypoint (uses production settings)."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dealwright.settings.production")

application = get_asgi_application()
