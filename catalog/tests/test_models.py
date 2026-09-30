"""Card 2 — catalog model validation.

Design refs: mvp-build-plan.md Card 2 (quantifier rule is the TDD anchor);
service-catalog-draft.md rules 1-5; styleguide — models validate shape.

Tier: catalog & profile management → 80-85%.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from catalog.models import RequiredSkill, Service
from catalog.tests.conftest import make_service, make_user
from team.models import SkillLevel


class TestQuantifierRule:
    """Every service declares machine-readable ROI parameters or is qualitative."""

    def test_service_must_declare_roi_parameter_or_qualitative(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError, match="[Qq]uantifier"):
            Service(
                owner=owner,
                category="Reporting, invoices, dashboards & data entry",
                name="No levers at all",
                setup_low=1000,
                setup_high=2000,
            ).full_clean()

    def test_qualitative_flag_alone_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category="Personal productivity ops",
            name="Purely qualitative",
            qualitative_value=True,
            custom_quote=True,
        ).full_clean()

    def test_reduction_pair_alone_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category="X",
            name="Reduction only",
            reduction_low=40,
            reduction_high=70,
            custom_quote=True,
        ).full_clean()

    def test_hours_pair_alone_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category="X",
            name="Hours only",
            hours_saved_low=3,
            hours_saved_high=6,
            custom_quote=True,
        ).full_clean()

    def test_revenue_pair_alone_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category="X",
            name="Revenue only",
            revenue_effect_type=Service.RevenueEffect.CONVERSION_UPLIFT_PCT,
            revenue_effect_low=10,
            revenue_effect_high=20,
            custom_quote=True,
        ).full_clean()


class TestPairs:
    def test_incomplete_range_fails(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner, category="X", name="Half a range", reduction_low=10, custom_quote=True
            ).full_clean()

    @pytest.mark.parametrize(
        "low_field,high_field,low,high",
        [
            ("reduction_low", "reduction_high", 70, 40),
            ("hours_saved_low", "hours_saved_high", 6, 3),
            ("revenue_effect_low", "revenue_effect_high", 30, 10),
            ("setup_low", "setup_high", 15000, 8000),
            ("monthly_low", "monthly_high", 4000, 2000),
            ("delivery_days_min", "delivery_days_max", 14, 7),
        ],
    )
    def test_low_must_not_exceed_high(self, db, low_field, high_field, low, high) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category="X",
                name="Inverted range",
                qualitative_value=True,
                custom_quote=True,
                **{low_field: low, high_field: high},
            ).full_clean()

    def test_negative_values_rejected(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category="X",
                name="Negative hours",
                hours_saved_low=-1,
                hours_saved_high=2,
                custom_quote=True,
            ).full_clean()


class TestPricing:
    def test_pricing_required_unless_custom_quote(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError, match="[Pp]ric"):
            Service(
                owner=owner, category="X", name="Free?", reduction_low=10, reduction_high=20
            ).full_clean()

    def test_custom_quote_without_ranges_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category="X",
            name="Custom",
            qualitative_value=True,
            custom_quote=True,
        ).full_clean()


class TestRevenueEffect:
    def test_type_requires_numbers(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category="X",
                name="Type without numbers",
                revenue_effect_type=Service.RevenueEffect.DSO_DAYS,
                custom_quote=True,
            ).full_clean()

    def test_numbers_require_type(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category="X",
                name="Numbers without type",
                revenue_effect_low=5,
                revenue_effect_high=15,
                custom_quote=True,
            ).full_clean()


class TestTagsAndTenancy:
    def test_problem_tags_must_be_strings(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category="X",
                name="Bad tags",
                problem_tags=["ok-tag", 42],
                qualitative_value=True,
                custom_quote=True,
            ).full_clean()

    def test_unique_owner_category_name(self, db) -> None:
        owner = make_user()
        make_service(owner, name="Dup")
        with pytest.raises(ValidationError):  # full_clean catches it before the DB
            make_service(owner, name="Dup")

    def test_services_cascade_with_owner(self, db) -> None:
        service = make_service(make_user())
        assert Service.objects.count() == 1
        service.owner.delete()
        assert Service.objects.count() == 0


class TestRequiredSkill:
    def test_reuses_team_proficiency_ladder(self) -> None:
        """Card 5 matches RequiredSkill.min_level against Capability.level — one ladder."""
        field = RequiredSkill._meta.get_field("min_level")
        assert {c[0] for c in field.choices} == set(SkillLevel.values)

    def test_default_level_is_beginner(self, db) -> None:
        service = make_service(make_user(), name="Skilled")
        skill = RequiredSkill(service=service, skill="CRM management")
        skill.full_clean()
        skill.save()
        assert skill.min_level == SkillLevel.BEGINNER

    def test_unique_skill_per_service(self, db) -> None:
        service = make_service(make_user(), name="One skill once")
        RequiredSkill.objects.create(service=service, skill="Copywriting")
        with pytest.raises(IntegrityError):
            RequiredSkill.objects.create(service=service, skill="Copywriting")
