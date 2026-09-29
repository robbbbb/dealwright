"""View smoke tests (templates/UI tier, 40–50%) — through public URLs, factory data."""

import pytest
from django.urls import reverse

from bench.models import Capability, VAProfile
from bench.services import add_capability, create_va_profile

pytestmark = pytest.mark.django_db


def _login(client, user) -> None:
    client.force_login(user)


# --- access control -------------------------------------------------------------------


def test_bench_requires_login(client) -> None:
    response = client.get(reverse("bench:bench_home"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_other_users_bench_member_is_404(client, user) -> None:
    other = user.__class__.objects.create_user(
        username="lea", password="test-pass-123456"
    )
    va = create_va_profile(owner=other, display_name="Maria")
    _login(client, user)

    response = client.get(reverse("bench:va_detail", args=[va.pk]))

    assert response.status_code == 404


# --- bench page -----------------------------------------------------------------------


def test_bench_page_lists_vas_and_my_skills(client, user, va) -> None:
    add_capability(holder=va, skill="Email marketing")
    _login(client, user)

    response = client.get(reverse("bench:bench_home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "My skills" in content
    assert "Maria" in content
    assert "₱250" in content
    assert "Email marketing" in content


def test_add_my_skill_from_bench_page(client, user) -> None:
    _login(client, user)

    response = client.post(
        reverse("bench:bench_home"),
        {"skill": "Copywriting", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    assert Capability.objects.filter(skill="Copywriting").exists()
    assert Capability.objects.first().provider_profile is not None


def test_add_my_skill_without_name_rerenders_with_error(client, user) -> None:
    _login(client, user)

    response = client.post(
        reverse("bench:bench_home"),
        {"skill": "", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 200
    assert "required" in response.content.decode().lower()
    assert Capability.objects.count() == 0


# --- bench member CRUD ----------------------------------------------------------------


def test_add_bench_member(client, user) -> None:
    _login(client, user)
    payload = {
        "display_name": "Jen",
        "is_active": "on",
        "rate_basis": "project",
        "rate_per_hour": "0",
        "project_rate": "25000",
        "currency": "PHP",
        "availability_hours_per_week": "20",
        "timezone": "Asia/Manila",
        "languages": "English",
        "industry_experience": "e-commerce",
        "notes": "",
    }

    response = client.post(reverse("bench:va_add"), payload)

    assert response.status_code == 302
    va = VAProfile.objects.get(display_name="Jen")
    assert va.project_rate == 25000
    assert response.url == reverse("bench:va_detail", args=[va.pk])


def test_edit_bench_member_rate(client, user, va) -> None:
    _login(client, user)
    payload = {
        "display_name": "Maria",
        "is_active": "on",
        "rate_basis": "hourly",
        "rate_per_hour": "275",
        "currency": "PHP",
        "availability_hours_per_week": "35",
        "timezone": "Asia/Manila",
        "languages": "English, Tagalog",
        "industry_experience": "",
        "notes": "",
    }

    response = client.post(reverse("bench:va_detail", args=[va.pk]), payload)

    assert response.status_code == 302
    va.refresh_from_db()
    assert va.rate_per_hour == 275
    assert va.availability_hours_per_week == 35


# --- skills on a bench member ---------------------------------------------------------


def test_add_skill_to_bench_member(client, user, va) -> None:
    _login(client, user)

    response = client.post(
        reverse("bench:va_skill_add", args=[va.pk]),
        {"skill": "n8n workflows", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    assert va.capabilities.filter(skill="n8n workflows").exists()


def test_add_skill_invalid_shows_flash_error(client, user, va) -> None:
    _login(client, user)

    response = client.post(
        reverse("bench:va_skill_add", args=[va.pk]),
        {"skill": "", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    assert not va.capabilities.exists()


def test_update_skill_to_advanced(client, user, va) -> None:
    cap = add_capability(holder=va, skill="n8n workflows")
    _login(client, user)

    response = client.post(
        reverse("bench:skill_update", args=[cap.pk]),
        {
            "skill": "n8n workflows",
            "level": "advanced",
            "tasks": "build + monitor podcast pipeline",
        },
    )

    assert response.status_code == 302
    cap.refresh_from_db()
    assert cap.level == "advanced"


def test_delete_skill(client, user, va) -> None:
    cap = add_capability(holder=va, skill="Bookkeeping")
    _login(client, user)

    response = client.post(reverse("bench:skill_delete", args=[cap.pk]))

    assert response.status_code == 302
    assert not Capability.objects.exists()


def test_cannot_update_skill_of_other_owner(client, user) -> None:
    other = user.__class__.objects.create_user(
        username="lea", password="test-pass-123456"
    )
    va = create_va_profile(owner=other, display_name="Maria")
    cap = add_capability(holder=va, skill="Bookkeeping")
    _login(client, user)

    response = client.post(
        reverse("bench:skill_update", args=[cap.pk]),
        {"skill": "Bookkeeping", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 404


# --- review pass 1 fixes: mutations are POST-only; currency symbol from stored field ---


def test_skill_delete_via_get_is_405_and_deletes_nothing(client, user, va) -> None:
    cap = add_capability(holder=va, skill="Bookkeeping")
    _login(client, user)

    response = client.get(reverse("bench:skill_delete", args=[cap.pk]))

    assert response.status_code == 405
    assert Capability.objects.filter(pk=cap.pk).exists()


def test_skill_update_via_get_is_405(client, user, va) -> None:
    cap = add_capability(holder=va, skill="Bookkeeping")
    _login(client, user)

    response = client.get(reverse("bench:skill_update", args=[cap.pk]))

    assert response.status_code == 405


def test_va_skill_add_via_get_is_405(client, user, va) -> None:
    _login(client, user)

    response = client.get(reverse("bench:va_skill_add", args=[va.pk]))

    assert response.status_code == 405
    assert va.capabilities.count() == 0


def test_rate_renders_symbol_from_stored_currency(client, user) -> None:
    create_va_profile(
        owner=user,
        display_name="Sam",
        rate_per_hour=40,
        currency="USD",
    )
    _login(client, user)

    content = client.get(reverse("bench:bench_home")).content.decode()

    assert "$40" in content
    assert "₱40" not in content
