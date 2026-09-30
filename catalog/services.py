"""Catalog services — every write goes through here, full_clean() before save.

Styleguide: plain functions, keyword-only args; constraints must hold from any
entry path (app, admin, shell, seed).
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from .models import RequiredSkill, Service
from .seed_data import SERVICES


def _defaults_from_row(row: dict[str, Any]) -> dict[str, Any]:
    setup = row.get("setup")
    monthly = row.get("monthly")
    delivery = row.get("delivery")
    return {
        "problem_tags": row.get("problem_tags", []),
        "setup_low": Decimal(setup[0]) if setup else None,
        "setup_high": Decimal(setup[1]) if setup else None,
        "monthly_low": Decimal(monthly[0]) if monthly else None,
        "monthly_high": Decimal(monthly[1]) if monthly else None,
        "custom_quote": bool(row.get("custom_quote")),
        "delivery_days_min": delivery[0] if delivery else None,
        "delivery_days_max": delivery[1] if delivery else None,
    }


def seed_default_catalog(*, owner: Any) -> tuple[int, int]:
    """Create missing default services for one provider; never touch existing rows.

    Returns (created, total_seed_rows). Edit-safe by natural key (owner, category, name).
    """
    created = 0
    for row in SERVICES:
        if Service.objects.filter(owner=owner, category=row["category"], name=row["name"]).exists():
            continue
        service = Service(
            owner=owner,
            category=row["category"],
            name=row["name"],
            **_defaults_from_row(row),
        )
        service.full_clean()  # clean before save; guards transcription
        service.save()
        for skill, min_level in row["skills"]:
            RequiredSkill.objects.get_or_create(
                service=service, skill=skill, defaults={"min_level": min_level}
            )
        created += 1
    return created, len(SERVICES)


def create_service(*, owner: Any, **fields: Any) -> Service:
    """Create a service from validated ServiceForm data (tags already a list)."""
    service = Service(owner=owner, **fields)
    service.full_clean()
    service.save()
    return service


def update_service(*, service: Service, **fields: Any) -> Service:
    """Set only the provided fields; full_clean before save."""
    for name, value in fields.items():
        setattr(service, name, value)
    service.full_clean()
    service.save()
    return service


def delete_service(*, service: Service) -> None:
    service.delete()


@transaction.atomic
def add_required_skill(*, service: Service, skill: str, min_level: str) -> RequiredSkill:
    """Attach a required skill (validated) to a service."""
    required = RequiredSkill(service=service, skill=skill, min_level=min_level)
    required.full_clean()
    required.save()
    return required


def delete_required_skill(*, required: RequiredSkill) -> None:
    required.delete()
