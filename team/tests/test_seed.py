"""seed_skills tests — public API only (command → service → registry)."""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.core.management import CommandError, call_command

from team.models import Skill
from team.seed_data import DEFAULT_SKILLS

pytestmark = pytest.mark.django_db


def test_seeds_full_vocabulary() -> None:
    user = User.objects.create_user(username="pro")
    call_command("seed_skills", "pro", stdout=_Out())
    assert Skill.objects.filter(owner=user).count() == len(DEFAULT_SKILLS)


def test_idempotent_second_run_creates_nothing() -> None:
    user = User.objects.create_user(username="pro")
    call_command("seed_skills", "pro", stdout=_Out())
    call_command("seed_skills", "pro", stdout=_Out())
    assert Skill.objects.filter(owner=user).count() == len(DEFAULT_SKILLS)


def test_tenancy_other_users_untouched() -> None:
    User.objects.create_user(username="mine")
    other = User.objects.create_user(username="other")
    call_command("seed_skills", "mine", stdout=_Out())
    assert Skill.objects.filter(owner=other).count() == 0


def test_unknown_username_raises() -> None:
    with pytest.raises(CommandError):
        call_command("seed_skills", "ghost", stdout=_Out())


def test_all_rows_valid_and_draft_derived() -> None:
    user = User.objects.create_user(username="pro")
    call_command("seed_skills", "pro", stdout=_Out())
    for skill in Skill.objects.filter(owner=user):
        skill.full_clean()  # shape holds from the command path too
    # vocabulary is exactly the draft catalog's union — nothing invented
    assert {s.name for s in Skill.objects.filter(owner=user)} == set(DEFAULT_SKILLS)


def test_shares_rows_with_catalog_seed() -> None:
    """seed_skills then seed_catalog must reuse registry rows, never duplicate."""
    from catalog import services as catalog_services

    user = User.objects.create_user(username="pro")
    call_command("seed_skills", "pro", stdout=_Out())
    catalog_services.seed_default_catalog(owner=user)
    shared = {"Copy review", "Basic bookkeeping"} & set(DEFAULT_SKILLS)
    for name in shared:
        assert Skill.objects.filter(owner=user, name=name).count() == 1


class _Out:
    def write(self, *_args: object) -> None:
        pass

    def flush(self) -> None:
        pass
