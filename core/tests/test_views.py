"""Home view: public landing for anonymous visitors, app home for signed-in users.

Smoke tier (templates & UI): through public APIs only.
"""

import re

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
    assert "From messy call notes" in content  # v2 mockup headline (Robb, 2026-09-29)
    assert reverse("account_signup") in content
    assert reverse("account_login") in content
    assert re.search(r'href="#features"[^>]*>View example proposal</a>', content)
    assert "estimates" in content.lower()  # estimate discipline on every public surface
    assert "₱399" in content and "₱1,990" in content  # Q10 pricing tiers


@pytest.mark.django_db
def test_signed_in_users_get_dashboard(client: Client) -> None:
    """Authenticated users land on the dashboard shell (Card 9 wires real data)."""
    user = User.objects.create_user(
        username="pro",
        email="pro@example.com",
        password="pw12345!x",
        first_name="Robb",
    )
    client.force_login(user)
    response = client.get(reverse("home"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Robb" in content  # greeting uses the first name
    # Mobile hamburger: button controls the drawer; nav still in DOM for no-JS users
    assert 'dw-menu-btn' in content and 'aria-controls="dw-drawer"' in content
    # Desktop: logout lives in the avatar account menu, not the sidebar
    assert 'dw-user-btn' in content and 'aria-controls="dw-user-menu"' in content
    assert content.count(">Log out</button>") == 2  # drawer (mobile) + avatar menu (desktop)
    # Sidebar sections (ROI estimates removed 2026-10-01: ROI is settings config
    # + engine embedded in sessions/proposals, not a provider-facing page)
    for nav_item in (
        "Dashboard", "Clients", "Discovery sessions",
        "Proposals", "Service catalog", "My skills", "Integrations", "Settings",
    ):
        assert nav_item in content, f"missing sidebar item: {nav_item}"
    # Stat labels render; counts are honest zeros — no mockup demo numbers
    for label in ("Clients", "Sessions · this month", "Proposals sent", "Win rate",
                  "Client benefit"):
        assert label in content, f"missing stat label: {label}"
    assert "62%" not in content and "₱41k" not in content
    # Empty states, not fabricated rows
    assert "No discovery sessions yet" in content
    assert "No proposals yet" in content
    assert "Your deal pipeline" in content
    assert "Complete your setup" in content
    assert reverse("team:team_home") in content
    # Estimate discipline on the app shell too; logout reachable
    assert "never guarantees" in content
    assert reverse("account_logout") in content
