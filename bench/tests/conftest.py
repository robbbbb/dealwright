"""Shared fixtures for bench tests."""

import pytest
from django.contrib.auth import get_user_model

from bench.models import ProviderProfile, VAProfile

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
    """One bench member, hourly ₱250 — the Maria of the test suite."""
    return VAProfile.objects.create(owner=user, display_name="Maria", rate_per_hour=250)
