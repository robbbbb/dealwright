"""Shared helpers for catalog tests."""

from __future__ import annotations

from django.contrib.auth.models import User

from catalog.models import Service

VALID_SERVICE: dict = {
    "category": "Lead capture & CRM automation",
    "name": "Test service",
    "problem_tags": ["leads-lost"],
    "reduction_low": 10,
    "reduction_high": 30,
    "setup_low": 8000,
    "setup_high": 15000,
    "monthly_low": 2000,
    "monthly_high": 4000,
    "delivery_days_min": 7,
    "delivery_days_max": 14,
}


def make_user(username: str = "pro") -> User:
    return User.objects.create_user(
        username=username, email=f"{username}@example.com", password="pw12345!x"
    )


def make_service(owner: User, **overrides: object) -> Service:
    """full_clean + save, so tests exercise the same path services use."""
    data = {**VALID_SERVICE, **overrides}
    service = Service(owner=owner, **data)
    service.full_clean()
    service.save()
    return service
