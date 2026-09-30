"""View smoke tests (templates/UI tier, 40–50%) — through public URLs, factory data."""

import pytest
from django.urls import reverse

from team.models import Capability, VAProfile
from team.services import add_capability, create_va_profile, get_or_create_skill

pytestmark = pytest.mark.django_db


def _login(client, user) -> None:
    client.force_login(user)


# --- access control -------------------------------------------------------------------


def test_team_requires_login(client) -> None:
    response = client.get(reverse("team:team_home"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_other_users_team_member_is_404(client, user) -> None:
    other = user.__class__.objects.create_user(
        username="lea", password="test-pass-123456"
    )
    va = create_va_profile(owner=other, display_name="Maria")
    _login(client, user)

    response = client.get(reverse("team:member_detail", args=[va.pk]))

    assert response.status_code == 404


# --- team page -----------------------------------------------------------------------


def test_team_page_lists_vas_and_my_skills(client, user, va, skill) -> None:
    create_va_profile(owner=user, display_name="Kim")  # identity-only
    add_capability(holder=va, skill=skill)
    _login(client, user)

    response = client.get(reverse("team:team_home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "My skills" in content
    assert "Add a skill" in content
    assert "Team roster" in content
    assert "Maria" in content
    assert "Kim" in content
    assert "Rates not set" in content  # identity-only member, honest state
    assert "₱250" in content  # engagement-complete member shows the real rate
    assert "Email marketing" in content


def test_add_my_skill_from_team_page(client, user, skill) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:team_home"),
        {"skill": "Copywriting", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    cap = Capability.objects.filter(
        skill__name="Copywriting", provider_profile__owner=user
    )
    assert cap.exists()
    assert Capability.objects.first().provider_profile is not None


def test_add_my_skill_without_name_rerenders_with_error(client, user, skill) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:team_home"),
        {"skill": "", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 200
    assert "required" in response.content.decode().lower()
    assert Capability.objects.count() == 0


# --- team member CRUD ----------------------------------------------------------------


def test_add_team_member(client, user) -> None:
    _login(client, user)
    response = client.post(
        reverse("team:member_add"),
        {"display_name": "Jen", "is_active": "on", "notes": ""},
    )

    assert response.status_code == 302
    va = VAProfile.objects.get(display_name="Jen")
    assert va.engagement_incomplete  # identity-only: terms come later
    assert va.rate_basis == "hourly"
    assert response.url == reverse("team:member_detail", args=[va.pk])


def test_identity_only_member_passes_full_clean(user) -> None:
    """Design pass 2026-09-29: identity-only creation must not trip the
    project-basis rule; completeness is a Card 5 concern, not a save blocker."""
    va = VAProfile.objects.create(owner=user, display_name="Kim")
    va.full_clean()  # must not raise


def test_edit_team_member_rate(client, user, va) -> None:
    _login(client, user)
    payload = {
        "rate_basis": "hourly",
        "rate_per_hour": "275",
        "currency": "PHP",
        "availability_hours_per_week": "35",
        "timezone": "Asia/Manila",
        "languages": "English, Tagalog",
        "industry_experience": "",
    }

    response = client.post(reverse("team:member_engagement", args=[va.pk]), payload)

    assert response.status_code == 302
    va.refresh_from_db()
    assert va.rate_per_hour == 275
    assert va.availability_hours_per_week == 35


# --- skills on a team member ---------------------------------------------------------


def test_add_skill_to_team_member(client, user, va, skill) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:member_skill_add", args=[va.pk]),
        {
            "skill": get_or_create_skill(owner=user, name="n8n workflows").pk,
            "level": "beginner",
            "tasks": "",
        },
    )

    assert response.status_code == 302
    assert va.capabilities.filter(skill__name="n8n workflows").exists()


def test_add_skill_invalid_shows_flash_error(client, user, va, skill) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:member_skill_add", args=[va.pk]),
        {"skill": "", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    assert not va.capabilities.exists()


def test_update_skill_to_advanced(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="n8n workflows"))
    _login(client, user)

    response = client.post(
        reverse("team:skill_update", args=[cap.pk]),
        {
            "skill": cap.skill_id,
            "level": "advanced",
            "tasks": "build + monitor podcast pipeline",
        },
    )

    assert response.status_code == 302
    cap.refresh_from_db()
    assert cap.level == "advanced"


def test_delete_skill(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="Bookkeeping"))
    _login(client, user)

    response = client.post(reverse("team:skill_delete", args=[cap.pk]))

    assert response.status_code == 302
    assert not Capability.objects.exists()


def test_cannot_update_skill_of_other_owner(client, user, skill) -> None:
    other = user.__class__.objects.create_user(
        username="lea", password="test-pass-123456"
    )
    va = create_va_profile(owner=other, display_name="Maria")
    cap = add_capability(
        holder=va, skill=get_or_create_skill(owner=other, name="Bookkeeping")
    )
    _login(client, user)

    response = client.post(
        reverse("team:skill_update", args=[cap.pk]),
        {"skill": cap.skill_id, "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 404


# --- review pass 1 fixes: mutations are POST-only; currency symbol from stored field ---


def test_skill_delete_via_get_is_405_and_deletes_nothing(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="Bookkeeping"))
    _login(client, user)

    response = client.get(reverse("team:skill_delete", args=[cap.pk]))

    assert response.status_code == 405
    assert Capability.objects.filter(pk=cap.pk).exists()


def test_skill_update_via_get_is_405(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="Bookkeeping"))
    _login(client, user)

    response = client.get(reverse("team:skill_update", args=[cap.pk]))

    assert response.status_code == 405


def test_member_skill_add_via_get_is_405(client, user, va) -> None:
    _login(client, user)

    response = client.get(reverse("team:member_skill_add", args=[va.pk]))

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

    content = client.get(reverse("team:team_home")).content.decode()

    assert "$40" in content
    assert "₱40" not in content


def test_member_engagement_via_get_is_405(client, user, va) -> None:
    _login(client, user)

    response = client.get(reverse("team:member_engagement", args=[va.pk]))

    assert response.status_code == 405
    va.refresh_from_db()
    assert va.rate_per_hour == 250  # untouched
