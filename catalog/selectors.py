"""Catalog selectors — all reads live here; views never filter querysets inline."""

from __future__ import annotations

from typing import Any

from django.db.models import QuerySet

from .models import RequiredSkill, Service


def list_services(owner: Any) -> QuerySet[Service]:
    """The owner's whole catalog, category-grouped for the list page."""
    return Service.objects.filter(owner=owner).prefetch_related("required_skills")


def get_service_for_owner(owner: Any, service_id: int) -> Service | None:
    """Ownership-checked service lookup — None means not found for this owner."""
    return Service.objects.filter(owner=owner, pk=service_id).first()


def get_required_skill_for_owner(owner: Any, skill_id: int) -> RequiredSkill | None:
    """A required skill is addressable only through its service's owner (tenancy)."""
    return RequiredSkill.objects.select_related("service").filter(
        service__owner=owner, pk=skill_id
    ).first()
