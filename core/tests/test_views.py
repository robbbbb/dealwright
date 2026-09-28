"""Home view: public landing for anonymous visitors, app home for signed-in users.

Smoke tier (templates & UI): through public APIs only.
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_landing_renders_for_anonymous(client: Client) -> None:
    """Anonymous visitors get the marketing landing page with signup/login CTAs."""
    response = client.get(reverse("home"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Turn discovery calls into" in content
    assert reverse("account_signup") in content
    assert reverse("account_login") in content
    assert "estimates" in content.lower()  # estimate discipline on every public surface


@pytest.mark.django_db
def test_signed_in_users_get_app_home(client: Client) -> None:
    """Authenticated users skip the landing and get the signed-in home."""
    user = User.objects.create_user(username="pro", email="pro@example.com", password="pw12345!x")
    client.force_login(user)
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert b"Signed in as" in response.content
