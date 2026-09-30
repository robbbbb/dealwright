"""Card 2 — seed catalog from docs/design/service-catalog-draft.md.

Tier: 80-85%. The seed is Tier-2 data (regenerable from git) and must never
clobber provider edits — re-running only creates missing services.
"""

from __future__ import annotations

from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.core.management import call_command

from catalog.models import RequiredSkill, Service
from catalog.tests.conftest import make_user

CATEGORIES = [
    "Lead capture & CRM automation",
    "Automated follow-ups",
    "Customer support & onboarding",
    "Reporting, invoices, dashboards & data entry",
    "Podcast & content distribution",
    "Social media management & scheduling",
    "Custom Django dashboards, portals & internal tools",
    "Personal productivity ops",
]
SERVICE_COUNT = 25  # draft: 8 categories, ~26 services — actual table count


@pytest.fixture
def seeded(db) -> User:
    owner = make_user()
    call_command("seed_catalog", owner.username, stdout=StringIO())
    return owner


def test_seed_creates_full_catalog(seeded: User) -> None:
    assert Service.objects.count() == SERVICE_COUNT
    assert set(Service.objects.values_list("category", flat=True)) == set(CATEGORIES)
    names = set(Service.objects.values_list("name", flat=True))
    assert any(n.startswith("Podcast distribution pipeline") for n in names)
    assert any(n.startswith("Personal assistant service") for n in names)
    assert all(s.owner_id == seeded.id for s in Service.objects.all())


def test_seed_is_idempotent(seeded: User) -> None:
    call_command("seed_catalog", seeded.username, stdout=StringIO())
    call_command("seed_catalog", seeded.username, stdout=StringIO())
    assert Service.objects.count() == SERVICE_COUNT


def test_seeded_services_pass_validation(seeded: User) -> None:
    """Quantifier rule + pair ordering hold for every transcribed row."""
    for service in Service.objects.all():
        service.full_clean()  # raises on any transcription gap


def test_seeded_services_have_required_skills(seeded: User) -> None:
    for service in Service.objects.prefetch_related("required_skills"):
        assert service.required_skills.exists(), f"{service.name} has no required skills"


def test_seed_does_not_clobber_edits(seeded: User) -> None:
    """Provider customizations survive re-seeding (Tier-0 discipline)."""
    edited = Service.objects.get(name__startswith="Podcast distribution pipeline")
    edited.name = "Podcast pipeline (customized)"
    edited.full_clean()
    edited.save()
    call_command("seed_catalog", seeded.username, stdout=StringIO())
    assert Service.objects.filter(name="Podcast pipeline (customized)").exists()
    # The renamed row no longer matches the natural key, so the seed re-creates
    # the original alongside the edit (bootstrap semantics — edits survive,
    # missing seed rows come back).
    assert Service.objects.filter(name__startswith="Podcast distribution pipeline").exists()
    assert Service.objects.count() == SERVICE_COUNT + 1


def test_seed_scopes_to_requested_owner(seeded: User) -> None:
    other = User.objects.create_user(username="other", email="o@example.com", password="pw12345!x")
    call_command("seed_catalog", other.username, stdout=StringIO())
    assert Service.objects.filter(owner=other).count() == SERVICE_COUNT
    assert Service.objects.count() == SERVICE_COUNT * 2
    assert RequiredSkill.objects.filter(service__owner=other).exists()


def test_seed_unknown_user_fails_clearly(db) -> None:
    from django.core.management.base import CommandError

    with pytest.raises(CommandError, match="[Nn]o user"):
        call_command("seed_catalog", "ghost", stdout=StringIO())
