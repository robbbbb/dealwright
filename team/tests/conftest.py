"""Shared fixtures for team tests."""

import pytest
from django.contrib.auth import get_user_model

from team.models import ProviderProfile, VAProfile

User = get_user_model()


@pytest.fixture
def user(db) -> User:  # type: ignore[name-defined]
    return User.objects.create_user(
        username="robb",
        email="robb@example.com",
        password="test-pass-123456",
    )


@pytest.fixture
def provider_profile(user) -> ProviderProfile:
    """Solo-by-default profile for the account owner (valid data, ORM-created)."""
    return ProviderProfile.objects.create(owner=user)


@pytest.fixture
def va(user) -> VAProfile:
    """One team member, hourly ₱250 — the Maria of the test suite."""
    return VAProfile.objects.create(owner=user, display_name="Maria", rate_per_hour=250)
