"""Catalog selectors — all reads live here; views never filter querysets inline."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from .models import RequiredSkill, Service


def list_services(owner: Any) -> QuerySet[Service]:
    """The owner's whole catalog, category-grouped for the list page."""
    return Service.objects.filter(owner=owner).prefetch_related("required_skills__skill")


def get_service_for_owner(owner: Any, slug: str) -> Service | None:
    """Ownership-checked service lookup by URL slug — None means not found."""
    return Service.objects.filter(owner=owner, slug=slug).first()


def get_required_skill_for_service(service: Service, slug: str) -> RequiredSkill | None:
    """Tenancy is inherited through the service — slug lookup within it only."""
    return RequiredSkill.objects.filter(service=service, slug=slug).first()
