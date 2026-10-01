"""Service-layer tests for team — write paths through public APIs."""

import pytest
from django.core.exceptions import ValidationError

from team.models import Capability, ProviderProfile, Skill, SkillLevel, VAProfile
from team.services import (
    add_capability,
    create_va_profile,
    delete_capability,
    get_provider_profile,
    update_capability,
    update_provider_profile,
    update_va_profile,
)


def _n8n(user):
    return Skill.objects.get_or_create(owner=user, name="n8n workflows")[0]


@pytest.mark.django_db
class TestProviderProfileService:
    def test_get_or_creates_once(self, user) -> None:
        first = get_provider_profile(user)
        second = get_provider_profile(user)

        assert first.pk == second.pk
        assert ProviderProfile.objects.count() == 1

    def test_created_profile_defaults_to_freelancer(self, user) -> None:
        profile = get_provider_profile(user)

        assert profile.delivery_mode == "solo"


@pytest.mark.django_db
class TestUpdateProviderProfileService:
    def test_updates_terms_and_identity(self, provider_profile) -> None:
        updated = update_provider_profile(
            profile=provider_profile,
            delivery_mode="team",
            branding_name="Rodriguez VA Services",
            persona="Podcast workflows for creators.",
            rate_basis="hourly",
            rate_per_hour=350,
            project_rate=None,
            currency="PHP",
            availability_hours_per_week=30,
            timezone="Asia/Manila",
            languages="English, Tagalog",
        )

        assert updated.delivery_mode == "team"
        assert updated.branding_name == "Rodriguez VA Services"
        assert updated.rate_per_hour == 350
        assert updated.availability_hours_per_week == 30
        assert updated.languages == "English, Tagalog"
        provider_profile.refresh_from_db()
        assert provider_profile.persona == "Podcast workflows for creators."

    def test_invalid_state_writes_nothing(self, provider_profile) -> None:
        with pytest.raises(ValidationError):
            update_provider_profile(
                profile=provider_profile,
                rate_basis="project",
                project_rate=None,
            )

        provider_profile.refresh_from_db()
        assert provider_profile.rate_basis == "hourly"


@pytest.mark.django_db
class TestVAProfileService:
    def test_create_and_update(self, user) -> None:
        va = create_va_profile(
            owner=user,
            display_name="Maria",
            rate_per_hour=250,
            availability_hours_per_week=30,
        )
        assert va.pk is not None

        updated = update_va_profile(
            va=va,
            rate_per_hour=275,
            rate_basis="project",
            project_rate=25000,
        )
        assert updated.rate_per_hour == 275
        assert updated.rate_basis == "project"
        assert updated.project_rate == 25000
        assert updated.availability_hours_per_week == 30  # untouched field stays

    def test_update_rejects_invalid_state(self, user) -> None:
        va = create_va_profile(owner=user, display_name="Maria")

        with pytest.raises(ValidationError):
            update_va_profile(va=va, display_name="")  # blank name never valid


@pytest.mark.django_db
class TestCapabilityService:
    def test_add_to_solo_provider_profile(self, user, skill) -> None:
        profile = get_provider_profile(user)

        cap = add_capability(holder=profile, skill=skill)

        assert cap.provider_profile == profile
        assert cap.va_profile is None
        assert list(profile.capabilities.all()) == [cap]

    def test_add_to_team_va(self, user, skill) -> None:
        va = create_va_profile(owner=user, display_name="Maria")

        cap = add_capability(holder=va, skill=_n8n(user))

        assert cap.va_profile == va
        assert list(va.capabilities.all()) == [cap]

    def test_add_with_proficiency_and_tasks(self, user, skill) -> None:
        va = create_va_profile(owner=user, display_name="Maria")

        cap = add_capability(
            holder=va,
            skill=skill,
            level=SkillLevel.ADVANCED,
            tasks="Klaviyo flows, campaign copy",
        )

        assert cap.level == SkillLevel.ADVANCED
        assert cap.tasks == "Klaviyo flows, campaign copy"

    def test_update_to_advanced_with_tasks(self, user, skill) -> None:
        va = create_va_profile(owner=user, display_name="Maria")
        cap = add_capability(holder=va, skill=_n8n(user))

        updated = update_capability(
            capability=cap,
            skill=_n8n(user),
            level=SkillLevel.ADVANCED,
            tasks="build + monitor podcast pipeline",
        )

        assert updated.level == SkillLevel.ADVANCED
        assert updated.trust_rank == 2
        assert updated.tasks == "build + monitor podcast pipeline"

    def test_delete_capability(self, user, skill) -> None:
        va = create_va_profile(owner=user, display_name="Maria")
        cap = add_capability(holder=va, skill=_n8n(user))

        delete_capability(capability=cap)

        assert Capability.objects.count() == 0

    def test_duplicate_skill_per_holder_rejected(self, user, skill) -> None:
        va = create_va_profile(owner=user, display_name="Maria")
        add_capability(holder=va, skill=skill)

        with pytest.raises(ValidationError):
            add_capability(holder=va, skill=skill)


@pytest.mark.django_db
def test_va_with_project_rate_visible_in_team(user) -> None:
    va = create_va_profile(
        owner=user, display_name="Jen", rate_basis="project", project_rate=25000
    )

    assert VAProfile.objects.get(pk=va.pk).project_rate == 25000
