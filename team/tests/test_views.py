"""View smoke tests (templates/UI tier, 40–50%) — through public URLs, factory data."""

import pytest
from django.urls import reverse

from team.models import Capability, Skill, VAProfile
from team.services import (
    add_capability,
    create_va_profile,
    get_or_create_skill,
    get_provider_profile,
    update_va_profile,
)

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

    response = client.get(reverse("team:member_detail", args=[va.slug]))

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
    assert "Manage skill list" in content
    assert content.index("Team roster") < content.index("Manage skill list")
    assert "Maria" in content
    assert "Kim" in content
    assert "Rates not set" in content  # identity-only member, honest state
    assert "₱250" in content  # engagement-complete member shows the real rate
    assert "Email marketing" in content


# --- roster preview cap + full roster page -------------------------------------------


def _make_members(owner, count: int) -> None:
    for i in range(count):
        create_va_profile(owner=owner, display_name=f"Member {i}")


def test_team_home_caps_roster_preview_at_four(client, user) -> None:
    _make_members(user, 5)
    _login(client, user)

    response = client.get(reverse("team:team_home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Member 3" in content  # four cards shown
    assert "Member 4" not in content  # fifth card held back
    assert reverse("team:member_list") in content  # see-all link present
    assert "See all 5 members" in content


def test_team_home_shows_all_when_four_or_fewer(client, user) -> None:
    _make_members(user, 4)
    _login(client, user)

    response = client.get(reverse("team:team_home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Member 3" in content
    assert "See all" not in content


def test_member_list_requires_login(client) -> None:
    response = client.get(reverse("team:member_list"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_member_list_shows_every_member(client, user, va) -> None:
    _make_members(user, 6)
    _login(client, user)

    response = client.get(reverse("team:member_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Maria" in content
    for i in range(6):
        assert f"Member {i}" in content


def test_member_list_is_scoped_to_owner(client, user) -> None:
    other = user.__class__.objects.create_user(
        username="lea", password="test-pass-123456"
    )
    create_va_profile(owner=other, display_name="Maria")
    _login(client, user)

    response = client.get(reverse("team:member_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Maria" not in content


def test_add_my_skill_from_team_page(client, user, skill) -> None:
    _login(client, user)

    copywriting = get_or_create_skill(owner=user, name="Copywriting")
    response = client.post(
        reverse("team:team_home"),
        {"skill": copywriting.pk, "level": "beginner", "tasks": ""},
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
    assert response.url == reverse("team:member_detail", args=[va.slug])


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

    response = client.post(reverse("team:member_engagement", args=[va.slug]), payload)

    assert response.status_code == 302
    va.refresh_from_db()
    assert va.rate_per_hour == 275
    assert va.availability_hours_per_week == 35


# NOTE: test_member_detail_groups_profile_terms_and_capabilities was removed in
# pass 11 review — it asserted markup from the still-uncommitted member_detail
# redesign (headings exist only in working-tree edits). Restore it when that
# redesign lands (reviewed scope), keeping its assertions with the template.


# --- skills on a team member ---------------------------------------------------------


def test_add_skill_to_team_member(client, user, va, skill) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:member_skill_add", args=[va.slug]),
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
        reverse("team:member_skill_add", args=[va.slug]),
        {"skill": "", "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 302
    assert not va.capabilities.exists()


def test_update_skill_to_advanced(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="n8n workflows"))
    _login(client, user)

    response = client.post(
        reverse("team:skill_update", args=[cap.slug]),
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

    response = client.post(reverse("team:skill_delete", args=[cap.slug]))

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
        reverse("team:skill_update", args=[cap.slug]),
        {"skill": cap.skill_id, "level": "beginner", "tasks": ""},
    )

    assert response.status_code == 404


# --- review pass 1 fixes: mutations are POST-only; currency symbol from stored field ---


def test_skill_delete_via_get_is_405_and_deletes_nothing(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="Bookkeeping"))
    _login(client, user)

    response = client.get(reverse("team:skill_delete", args=[cap.slug]))

    assert response.status_code == 405
    assert Capability.objects.filter(pk=cap.pk).exists()


def test_skill_update_via_get_is_405(client, user, va, skill) -> None:
    cap = add_capability(holder=va, skill=get_or_create_skill(owner=user, name="Bookkeeping"))
    _login(client, user)

    response = client.get(reverse("team:skill_update", args=[cap.slug]))

    assert response.status_code == 405


def test_member_skill_add_via_get_is_405(client, user, va) -> None:
    _login(client, user)

    response = client.get(reverse("team:member_skill_add", args=[va.slug]))

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

    response = client.get(reverse("team:member_engagement", args=[va.slug]))

    assert response.status_code == 405
    va.refresh_from_db()
    assert va.rate_per_hour == 250  # untouched


class TestTeamSlugSemantics:
    def test_member_slug_frozen_on_rename(self, client, user, va) -> None:
        _login(client, user)
        created_slug = va.slug
        update_va_profile(va=va, display_name="Renamed Member")
        va.refresh_from_db()
        assert va.slug == created_slug  # renames never break links

    def test_same_display_name_owner_scoped(self, user, va) -> None:
        other = user.__class__.objects.create_user(username="slug-other")
        twin = create_va_profile(owner=other, display_name=va.display_name)
        assert twin.slug == va.slug  # uniqueness is per owner, not global

    def test_capability_slug_dedupes_across_holders(self, user, va, skill) -> None:
        profile = get_provider_profile(user)
        on_va = add_capability(holder=va, skill=skill)
        on_profile = add_capability(holder=profile, skill=skill)
        assert on_va.slug != on_profile.slug  # same skill, owner-wide uniqueness
        assert on_profile.slug.startswith(on_va.slug + "-")


class TestSkillListManager:
    def _create(self, client, name: str):
        return client.post(reverse("team:skill_create"), {"name": name})

    def test_create_registry_skill(self, client, user) -> None:
        _login(client, user)
        assert self._create(client, "Podcast editing").status_code == 302
        assert Skill.objects.filter(owner=user, name="Podcast editing").exists()

    def test_create_is_idempotent(self, client, user) -> None:
        _login(client, user)
        self._create(client, "Podcast editing")
        self._create(client, "Podcast editing")
        assert Skill.objects.filter(owner=user, name="Podcast editing").count() == 1

    def test_blank_name_rejected(self, client, user) -> None:
        _login(client, user)
        assert self._create(client, "").status_code == 302  # flash error, no row
        assert Skill.objects.filter(owner=user).count() == 0

    def test_create_get_rejected(self, client, user) -> None:
        _login(client, user)
        assert client.get(reverse("team:skill_create")).status_code == 405

    def test_remove_unused_skill(self, client, user) -> None:
        _login(client, user)
        skill = get_or_create_skill(owner=user, name="Unused skill")
        url = reverse("team:skill_registry_delete", kwargs={"skill": skill.slug})
        assert client.post(url).status_code == 302
        assert not Skill.objects.filter(pk=skill.pk).exists()

    def test_cannot_remove_skill_in_use(self, client, user, va, skill) -> None:
        _login(client, user)
        add_capability(holder=va, skill=skill)
        url = reverse("team:skill_registry_delete", kwargs={"skill": skill.slug})
        assert client.post(url).status_code == 302  # flash error, row survives
        assert Skill.objects.filter(pk=skill.pk).exists()

    def test_remove_get_rejected(self, client, user, skill) -> None:
        _login(client, user)
        url = reverse("team:skill_registry_delete", kwargs={"skill": skill.slug})
        assert client.get(url).status_code == 405

    def test_cannot_remove_other_users_skill(self, client, user) -> None:
        _login(client, user)
        other = user.__class__.objects.create_user(username="reg-other")
        foreign = get_or_create_skill(owner=other, name="Foreign skill")
        url = reverse("team:skill_registry_delete", kwargs={"skill": foreign.slug})
        assert client.post(url).status_code == 404


# --- provider settings (delivery terms) -------------------------------------------------


def test_provider_settings_requires_login(client) -> None:
    response = client.get(reverse("team:provider_settings"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


def test_provider_settings_get_shows_current_terms(
    client, user, provider_profile
) -> None:
    provider_profile.branding_name = "Rodriguez VA Services"
    provider_profile.save()
    _login(client, user)

    response = client.get(reverse("team:provider_settings"))

    assert response.status_code == 200
    assert b"Rodriguez VA Services" in response.content


def test_provider_settings_number_inputs_carry_min_zero(client, user) -> None:
    """Browser-level guard: money/hours inputs advertise min=0 (server validates too)."""
    _login(client, user)

    response = client.get(reverse("team:provider_settings"))

    assert response.content.count(b'min="0"') == 3  # rate_per_hour, project_rate, availability


def test_provider_settings_security_card(client, user) -> None:
    """Security section links the existing allauth surfaces; email is the login method."""
    _login(client, user)

    response = client.get(reverse("team:provider_settings"))
    content = response.content

    assert user.email.encode() in content
    assert b'href="/accounts/email/"' in content
    assert b'href="/accounts/password/change/"' in content
    assert b'href="/accounts/2fa/"' in content
    assert b"Not set up" in content  # MFA off by default


def test_provider_settings_shows_mfa_on(client, user) -> None:
    from allauth.mfa.models import Authenticator

    Authenticator.objects.create(
        user=user, type=Authenticator.Type.TOTP, data={"secret": "a" * 32}
    )
    _login(client, user)

    response = client.get(reverse("team:provider_settings"))

    assert b"MFA on" in response.content
    assert b"Not set up" not in response.content


def test_provider_settings_post_saves_terms(client, user, provider_profile) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:provider_settings"),
        {
            # no delivery_mode — solo/team choice lives in the proposal flow
            "branding_name": "Rodriguez VA Services",
            "persona": "Podcast workflows for creators.",
            "rate_basis": "hourly",
            "rate_per_hour": "350",
            "currency": "PHP",
            "availability_hours_per_week": "30",
            "timezone": "Asia/Manila",
            "languages": "English, Tagalog",
        },
    )

    assert response.status_code == 302
    provider_profile.refresh_from_db()
    assert provider_profile.branding_name == "Rodriguez VA Services"
    assert provider_profile.rate_per_hour == 350
    assert provider_profile.availability_hours_per_week == 30
    assert provider_profile.languages == "English, Tagalog"


def test_provider_settings_post_negative_rate_writes_nothing(
    client, user, provider_profile
) -> None:
    """Negative money must get a friendly form error — never a 500 constraint trip."""
    _login(client, user)

    response = client.post(
        reverse("team:provider_settings"),
        {
            "branding_name": "Rodriguez VA Services",
            "rate_basis": "project",
            "project_rate": "-500",
            "rate_per_hour": "0",
            "currency": "PHP",
            "availability_hours_per_week": "40",
            "timezone": "Asia/Manila",
        },
    )

    assert response.status_code == 200
    assert "project_rate" in response.context["form"].errors
    provider_profile.refresh_from_db()
    assert provider_profile.branding_name != "Rodriguez VA Services"


def test_provider_settings_post_invalid_writes_nothing(
    client, user, provider_profile
) -> None:
    _login(client, user)

    response = client.post(
        reverse("team:provider_settings"),
        {
            "rate_basis": "project",  # project_rate missing → clean() rejects
            "rate_per_hour": "0",
            "currency": "PHP",
            "availability_hours_per_week": "40",
            "timezone": "Asia/Manila",
        },
    )

    assert response.status_code == 200
    provider_profile.refresh_from_db()
    assert provider_profile.rate_basis == "hourly"  # nothing written


def test_settings_url_beats_member_slug(client, user) -> None:
    """The literal /team/settings/ route must win over <slug:member>/ matching."""
    _login(client, user)

    assert client.get("/team/settings/").status_code == 200


def test_sidebar_highlights_exactly_one_team_item_per_page(client, user) -> None:
    """Settings lives in the team namespace — the skills link must not light up
    with it (pass 15: namespace-wide check was double-highlighting)."""
    _login(client, user)
    active = b"bg-white/12 font-bold text-white"

    settings_page = client.get(reverse("team:provider_settings"))
    team_page = client.get(reverse("team:team_home"))

    assert settings_page.content.count(active) == 1
    assert team_page.content.count(active) == 1


def test_member_engagement_negative_rate_writes_nothing(client, user, va) -> None:
    """Same friendly-rejection guarantee as settings: PRG + flash, zero writes."""
    _login(client, user)

    response = client.post(
        reverse("team:member_engagement", args=[va.slug]),
        {
            "rate_basis": "hourly",
            "rate_per_hour": "-1",
            "currency": "PHP",
            "availability_hours_per_week": "40",
            "timezone": "Asia/Manila",
        },
    )

    assert response.status_code == 302
    va.refresh_from_db()
    assert va.rate_per_hour == 250
