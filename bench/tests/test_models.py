"""Bench model tests — claim-triple rules, holder integrity, rate bases, schema.

Through public APIs only: model full_clean() for shape rules, DB constraints
exercised via ORM create inside atomic blocks. No services (Card 4 step order).
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from bench.models import Capability, ProviderProfile, SkillLevel, VAProfile

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
    def test_beginner_is_default_and_tasks_optional(self, va) -> None:
        cap = Capability(va_profile=va, skill="Email marketing")
        cap.full_clean()  # must not raise

        assert cap.level == SkillLevel.BEGINNER
        assert cap.trust_rank == 0

    def test_intermediate_ranks_between(self, va) -> None:
        cap = Capability(
            va_profile=va, skill="Email marketing", level=SkillLevel.INTERMEDIATE
        )
        cap.full_clean()  # must not raise

        assert cap.trust_rank == 1

    def test_advanced_is_top_rank(self, va) -> None:
        cap = Capability(
            va_profile=va,
            skill="Email marketing",
            level=SkillLevel.ADVANCED,
            tasks="Klaviyo flows, campaign copy, list management",
        )
        cap.full_clean()  # must not raise

        assert cap.trust_rank == 2

    def test_str_reports_skill_and_level(self, va) -> None:
        cap = Capability(va_profile=va, skill="Email marketing")

        assert str(cap) == "Email marketing (Beginner)"


# --- holder integrity: a claim belongs to exactly one of freelancer / VA -----------


@pytest.mark.django_db
class TestHolderIntegrity:
    def test_capability_without_holder_fails_clean(self, va) -> None:
        cap = Capability(skill="Orphan skill")

        with pytest.raises(ValidationError):
            cap.full_clean()

    def test_capability_with_both_holders_fails_clean(self, user, va) -> None:
        profile = ProviderProfile.objects.create(owner=user)
        cap = Capability(
            skill="Both holders",
            provider_profile=profile,
            va_profile=va,
        )

        with pytest.raises(ValidationError):
            cap.full_clean()

    def test_orphan_save_blocked_at_db_level(self) -> None:
        with pytest.raises(IntegrityError), transaction.atomic():
            Capability.objects.create(skill="Orphan skill")

    def test_skill_unique_per_holder(self, va) -> None:
        Capability.objects.create(va_profile=va, skill="Email marketing")

        with pytest.raises(IntegrityError), transaction.atomic():
            Capability.objects.create(va_profile=va, skill="Email marketing")

    def test_same_skill_allowed_across_holders(self, user, va) -> None:
        profile = ProviderProfile.objects.create(owner=user)
        Capability.objects.create(provider_profile=profile, skill="Email marketing")
        Capability.objects.create(va_profile=va, skill="Email marketing")

        assert Capability.objects.count() == 2


# --- VA bench: rate bases and numeric guards ----------------------------------------


@pytest.mark.django_db
class TestVARates:
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


# --- bench roster rules ---------------------------------------------------------------


@pytest.mark.django_db
class TestBenchRoster:
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


# --- schema compliance ------------------------------------------------------------------


@pytest.mark.parametrize(
    "model",
    [ProviderProfile, VAProfile, Capability],
)
def test_no_protected_characteristic_fields(model) -> None:
    field_names = {f.name for f in model._meta.get_fields()}

    assert not PROTECTED_CHARACTERISTIC_FIELDS & field_names
