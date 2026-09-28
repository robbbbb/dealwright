"""Card 0 TDD anchors + minimal auth smoke."""

import importlib

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_renders(client: Client) -> None:
    """Anchor (Card 0): the login page renders for anonymous visitors."""
    response = client.get(reverse("account_login"))
    assert response.status_code == 200
    assert b"Dealwright" in response.content


@pytest.mark.django_db
def test_home_redirects_anonymous_to_login(client: Client) -> None:
    """Anonymous visitors to / are pushed to sign-in."""
    response = client.get(reverse("home"))
    assert response.status_code == 302
    assert reverse("account_login") in response.url


def test_settings_read_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Anchor (Card 0): settings are env-driven — SECRET_KEY comes from the environment."""
    import dealwright.settings.base as base

    monkeypatch.setenv("DJANGO_SECRET_KEY", "env-driven-value")
    module = importlib.reload(base)
    assert module.SECRET_KEY == "env-driven-value"
