"""Catalog model validation — services + prices + delivery + skills.

Robb decision (2026-09-30, recorded in design-log): the ROI lever fields and
the quantifier rule were REMOVED from the model — the catalog carries no
computation for now; ROI parameters move to session data / a future
benchmarks table (Card 3 planning).

Tier: catalog & profile management → 80-85%.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from catalog.models import RequiredSkill, Service, ServiceCategory
from catalog.tests.conftest import category_for, make_service, make_user
from team.models import Skill, SkillLevel


class TestPairs:
    def test_incomplete_range_fails(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category=category_for(owner),
                name="Half a range",
                setup_low=1000,
                custom_quote=True,
            ).full_clean()

    @pytest.mark.parametrize(
        "low_field,high_field,low,high",
        [
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
                category=category_for(owner),
                name="Inverted range",
                custom_quote=True,
                **{low_field: low, high_field: high},
            ).full_clean()

    def test_negative_values_rejected(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category=category_for(owner),
                name="Negative price",
                setup_low=-1000,
                setup_high=2000,
            ).full_clean()


class TestPricing:
    def test_pricing_required_unless_custom_quote(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError, match="[Pp]ric"):
            Service(owner=owner, category=category_for(owner), name="Free?").full_clean()

    def test_custom_quote_without_ranges_is_valid(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        Service(
            owner=owner,
            category=category_for(owner),
            name="Custom",
            custom_quote=True,
        ).full_clean()


class TestCurrency:
    """Q3 no-FX: prices are declared per currency, never converted."""

    def test_default_currency_is_php(self, db) -> None:
        service = make_service(make_user())
        assert service.currency == "PHP"

    def test_usd_price_summary_uses_dollar_symbol(self, db) -> None:
        service = make_service(make_user(), currency="USD")
        assert service.price_summary() == "setup $8,000–15,000 · retainer $2,000–4,000/mo"

    def test_unknown_currency_falls_back_to_code(self, db) -> None:
        service = make_service(make_user(), currency="JPY")
        assert service.price_summary().startswith("setup JPY ")

    def test_invalid_currency_rejected(self, db) -> None:
        with pytest.raises(ValidationError):
            make_service(make_user("cu1"), currency="usd")
        with pytest.raises(ValidationError):
            make_service(make_user("cu2"), currency="DOLLARS")


class TestTagsAndTenancy:
    def test_problem_tags_must_be_strings(self, db) -> None:
        owner = User.objects.create_user(username="pro")
        with pytest.raises(ValidationError):
            Service(
                owner=owner,
                category=category_for(owner),
                name="Bad tags",
                problem_tags=["ok-tag", 42],
                custom_quote=True,
            ).full_clean()

    def test_unique_owner_category_name(self, db) -> None:
        owner = make_user()
        make_service(owner, name="Dup")
        with pytest.raises(ValidationError):  # full_clean catches it before the DB
            make_service(owner, name="Dup")

    def test_owner_delete_blocked_while_category_in_use(self, db) -> None:
        """Categories are PROTECTed — account deletion is blocked until the
        catalog is emptied (residual logged in docs/backlog.md)."""
        from django.db.models import ProtectedError

        service = make_service(make_user("cascade-a"))
        with pytest.raises(ProtectedError):
            service.owner.delete()

    def test_services_cascade_with_owner(self, db) -> None:
        service = make_service(make_user("cascade-b"))
        owner = service.owner
        service.delete()  # free the category, then the account cascade works
        owner.delete()
        assert Service.objects.count() == 0
        assert not ServiceCategory.objects.filter(owner_id=owner.pk).exists()


class TestRequiredSkill:
    def test_reuses_team_proficiency_ladder(self) -> None:
        """Card 5 matches RequiredSkill.min_level against Capability.level — one ladder."""
        field = RequiredSkill._meta.get_field("min_level")
        assert {c[0] for c in field.choices} == set(SkillLevel.values)

    def test_default_level_is_beginner(self, db) -> None:
        owner = make_user()
        service = make_service(owner, name="Skilled")
        skill = RequiredSkill(
            service=service,
            skill=Skill.objects.create(owner=owner, name="CRM management"),
        )
        skill.full_clean()
        skill.save()
        assert skill.min_level == SkillLevel.BEGINNER

    def test_unique_skill_per_service(self, db) -> None:
        owner = make_user()
        service = make_service(owner, name="One skill once")
        skill = Skill.objects.create(owner=owner, name="Copywriting")
        RequiredSkill.objects.create(service=service, skill=skill)
        with pytest.raises(IntegrityError):
            RequiredSkill.objects.create(service=service, skill=skill)


class TestSkillRegistryGuards:
    def test_required_skill_from_other_registry_rejected(self, db) -> None:
        mine, other = make_user("mine"), make_user("other2")
        service = make_service(mine, name="Guarded")
        foreign = Skill.objects.create(owner=other, name="Foreign skill")
        rs = RequiredSkill(service=service, skill=foreign)
        with pytest.raises(ValidationError):
            rs.full_clean()


class TestServiceCategory:
    """Categories are a provider-owned registry (2026-10-01, supersedes free text)."""

    def test_slug_unique_per_owner_and_frozen_on_rename(self, db) -> None:
        mine, other = make_user("cat-a"), make_user("cat-b")
        mine_cat = category_for(mine, "Leads & CRM")
        other_cat = category_for(other, "Leads & CRM")
        assert mine_cat.slug == other_cat.slug  # uniqueness is per owner
        mine_cat.name = "Totally new name"
        mine_cat.save()
        mine_cat.refresh_from_db()
        assert mine_cat.slug == "leads-crm"  # renames never break links

    def test_same_name_same_owner_rejected(self, db) -> None:
        owner = make_user("cat-c")
        category_for(owner, "Dup")
        with pytest.raises(ValidationError):
            ServiceCategory(owner=owner, name="Dup").full_clean()

    def test_service_category_from_other_owner_rejected(self, db) -> None:
        mine, other = make_user("cat-d"), make_user("cat-e")
        foreign = category_for(other, "Foreign cat")
        service = Service(
            owner=mine,
            category=foreign,
            name="Smuggled",
            custom_quote=True,
        )
        with pytest.raises(ValidationError, match="own list"):
            service.full_clean()

    def test_in_use_category_is_protected(self, db) -> None:
        from django.db.models import ProtectedError

        owner = make_user("cat-f")
        service = make_service(owner)
        with pytest.raises(ProtectedError):
            service.category.delete()

    def test_cascades_with_owner(self, db) -> None:
        owner = make_user("cat-g")
        category = category_for(owner)
        owner.delete()
        assert not ServiceCategory.objects.filter(pk=category.pk).exists()
