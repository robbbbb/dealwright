"""Template tags for the auth screens (docs/mockups/auth-mockup.html)."""

from allauth.socialaccount.providers import registry
from django import template

register = template.Library()


@register.simple_tag
def google_available() -> bool:
    """True when the Google provider is installed (i.e. credentials configured).

    The provider app is added to INSTALLED_APPS together with its credentials in
    settings, so a registered provider class is the single source of truth.
    """
    registry.load()
    return registry.get_class("google") is not None
