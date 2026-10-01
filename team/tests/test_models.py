"""Team model tests — claim-triple rules, holder integrity, rate bases, schema.

Through public APIs only: model full_clean() for shape rules, DB constraints
exercised via ORM create inside atomic blocks. No services (Card 4 step order).
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from team.models import Capability, ProviderProfile, Skill, SkillLevel, VAProfile

User = get_user_model()

# Protected personal characteristics must not exist anywhere in this schema.
PROTECTED_CHARACTERISTIC_FIELDS = {
    "gender",
    "sex",
    "age",
    "date_of_birth",
    "religion",
    "ethnicity",
    "race",
    "national_origin",
    "civil_status",
    "marital_status",
    "disability",
    "pregnancy",
}


# --- proficiency ladder (supersedes the claimed/verified TDD anchor; design-log
# entry at card close) --------------------------------------------------------------


@pytest.mark.django_db
class TestProficiencyLadder:
    def test_beginner_is_default_and_tasks_optional(self, va, skill) -> None:
        cap = Capability(va_profile=va, skill=skill)
        cap.full_clean()  # must not raise

        assert cap.level == SkillLevel.BEGINNER
        assert cap.trust_rank == 0

    def test_intermediate_ranks_between(self, va, skill) -> None:
        cap = Capability(
            va_profile=va, skill=skill, level=SkillLevel.INTERMEDIATE
        )
        cap.full_clean()  # must not raise

        assert cap.trust_rank == 1

    def test_advanced_is_top_rank(self, va, skill) -> None:
        cap = Capability(
            va_profile=va,
            skill=skill,
            level=SkillLevel.ADVANCED,
            tasks="Klaviyo flows, campaign copy, list management",
        )
        cap.full_clean()  # must not raise

        assert cap.trust_rank == 2

    def test_str_reports_skill_and_level(self, va, skill) -> None:
        cap = Capability(va_profile=va, skill=skill)

        assert str(cap) == "Email marketing (Beginner)"


# --- holder integrity: a claim belongs to exactly one of freelancer / VA -----------


@pytest.mark.django_db
class TestHolderIntegrity:
    def test_capability_without_holder_fails_clean(self, va, skill) -> None:
        cap = Capability(skill=skill)

        with pytest.raises(ValidationError):
            cap.full_clean()

    def test_capability_with_both_holders_fails_clean(self, user, va, skill) -> None:
        profile = ProviderProfile.objects.create(owner=user)
        cap = Capability(
            skill=skill,
            provider_profile=profile,
            va_profile=va,
        )

        with pytest.raises(ValidationError):
            cap.full_clean()

    def test_orphan_save_blocked_at_db_level(self, skill) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            Capability.objects.create(skill=skill)

    def test_skill_unique_per_holder(self, va, skill) -> None:
        Capability.objects.create(va_profile=va, skill=skill)

        with pytest.raises(IntegrityError), transaction.atomic():
            Capability.objects.create(va_profile=va, skill=skill)

    def test_same_skill_allowed_across_holders(self, user, va, skill) -> None:
        profile = ProviderProfile.objects.create(owner=user)
        Capability.objects.create(provider_profile=profile, skill=skill)
        Capability.objects.create(va_profile=va, skill=skill)

        assert Capability.objects.count() == 2


# --- member rates and numeric guards ----------------------------------------


@pytest.mark.django_db
class TestMemberRates:
    def test_project_basis_requires_project_rate(self, user) -> None:
        va = VAProfile(
            owner=user,
            display_name="Jen",
            rate_basis="project",
        )  # project_rate missing

        with pytest.raises(ValidationError) as err:
            va.full_clean()

        assert "project_rate" in err.value.message_dict

    def test_project_basis_with_rate_is_valid(self, user) -> None:
        va = VAProfile(
            owner=user,
            display_name="Jen",
            rate_basis="project",
            project_rate=25000,
        )
        va.full_clean()  # must not raise
        va.save()

        assert va.project_rate == 25000

    def test_hourly_basis_leaves_project_rate_optional(self, va) -> None:
        va.full_clean()  # must not raise

        assert va.rate_basis == "hourly"
        assert va.project_rate is None

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("rate_per_hour", -1),
            ("project_rate", -500),
            ("availability_hours_per_week", -5),
        ],
    )
    def test_negative_money_and_hours_blocked_at_db(self, user, field, value) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            VAProfile.objects.create(owner=user, display_name="Jen", **{field: value})

    def test_ph_anchored_defaults(self, user) -> None:
        va = VAProfile.objects.create(owner=user, display_name="Maria")

        assert va.rate_basis == "hourly"
        assert va.currency == "PHP"
        assert va.timezone == "Asia/Manila"
        assert va.is_active is True


# --- team roster rules ---------------------------------------------------------------


@pytest.mark.django_db
class TestTeamRoster:
    def test_display_name_unique_per_owner(self, va) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            VAProfile.objects.create(owner=va.owner, display_name="Maria")

    def test_same_display_name_ok_across_owners(self, user) -> None:
        other = User.objects.create_user(username="lea", password="test-pass-123456")
        VAProfile.objects.create(owner=user, display_name="Maria")
        VAProfile.objects.create(owner=other, display_name="Maria")

        assert VAProfile.objects.count() == 2


# --- provider profile ------------------------------------------------------------------


@pytest.mark.django_db
class TestProviderProfile:
    def test_one_profile_per_owner(self, provider_profile) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            ProviderProfile.objects.create(owner=provider_profile.owner)

    def test_freelancer_is_default_mode(self, provider_profile) -> None:
        assert provider_profile.delivery_mode == "solo"

    def test_display_name_prefers_branding_name(self, user) -> None:
        profile = ProviderProfile.objects.create(
            owner=user, branding_name="Rodriguez VA Services"
        )

        assert profile.display_name == "Rodriguez VA Services"

    def test_display_name_falls_back_to_account(self, provider_profile) -> None:
        assert provider_profile.display_name == "robb"


# --- provider engagement terms (pre-Card-5 card: design-log 2026-09-29) -------


@pytest.mark.django_db
class TestProviderEngagementTerms:
    def test_new_profile_carries_member_default_terms(self, provider_profile) -> None:
        assert provider_profile.rate_basis == "hourly"
        assert provider_profile.rate_per_hour == 0
        assert provider_profile.project_rate is None
        assert provider_profile.currency == "PHP"
        assert provider_profile.availability_hours_per_week == 40
        assert provider_profile.timezone == "Asia/Manila"
        assert provider_profile.languages == ""

    def test_defaults_count_as_incomplete(self, provider_profile) -> None:
        assert provider_profile.engagement_incomplete

    def test_hourly_rate_completes_terms(self, provider_profile) -> None:
        provider_profile.rate_per_hour = 350

        assert not provider_profile.engagement_incomplete

    def test_project_basis_incomplete_without_rate(self, provider_profile) -> None:
        provider_profile.rate_basis = "project"

        assert provider_profile.engagement_incomplete

    def test_project_basis_complete_with_rate(self, provider_profile) -> None:
        provider_profile.rate_basis = "project"
        provider_profile.project_rate = 25000

        assert not provider_profile.engagement_incomplete

    def test_project_basis_requires_project_rate(self, provider_profile) -> None:
        provider_profile.rate_basis = "project"

        with pytest.raises(ValidationError) as err:
            provider_profile.full_clean()

        assert "project_rate" in err.value.message_dict

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("rate_per_hour", -1),
            ("project_rate", -500),
            ("availability_hours_per_week", -5),
        ],
    )
    def test_negative_money_and_hours_blocked_at_db(
        self, user, field, value
    ) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            ProviderProfile.objects.create(owner=user, **{field: value})


# --- schema compliance ------------------------------------------------------------------


@pytest.mark.parametrize(
    "model",
    [ProviderProfile, VAProfile, Capability],
)
def test_no_protected_characteristic_fields(model) -> None:
    field_names = {f.name for f in model._meta.get_fields()}

    assert not PROTECTED_CHARACTERISTIC_FIELDS & field_names


class TestCapabilityRegistryGuard:
    def test_skill_from_other_registry_rejected(self, user, va) -> None:
        from django.contrib.auth.models import User

        other = User.objects.create_user(username="foreign-owner")
        foreign = Skill.objects.create(owner=other, name="Foreign")
        cap = Capability(va_profile=va, skill=foreign)
        with pytest.raises(ValidationError):
            cap.full_clean()
