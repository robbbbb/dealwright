"""Team services — every write goes through here, full_clean() before save.

Styleguide: plain functions, keyword-only args, services validate meaning;
constraints must hold from any entry path (app, admin, shell).
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Capability, ProviderProfile, Skill, SkillLevel, VAProfile

User = get_user_model()

Holder = ProviderProfile | VAProfile


def get_or_create_skill(*, owner: Any, name: str) -> Skill:
    """Registry row for one skill name — the single vocabulary source (2026-09-30
    Robb decision). Names are trimmed; uniqueness enforced per owner."""
    candidate = Skill(owner=owner, name=name.strip())
    # clean_fields (not full_clean): shape check BEFORE any write — no stray rows,
    # and no false unique error against the row we are about to look up.
    candidate.clean_fields()
    return Skill.objects.get_or_create(owner=owner, name=candidate.name)[0]


def get_provider_profile(user: Any) -> ProviderProfile:
    """The account holder's delivery identity — created solo-by-default on first need."""
    try:
        return user.provider_profile
    except ProviderProfile.DoesNotExist:
        profile = ProviderProfile(owner=user)
        profile.full_clean()
        profile.save()
        return profile


def create_va_profile(*, owner: Any, **fields: Any) -> VAProfile:
    """Add a team member from validated VAForm data."""
    va = VAProfile(owner=owner, **fields)
    va.full_clean()
    va.save()
    return va


def update_va_profile(*, va: VAProfile, **fields: Any) -> VAProfile:
    """Set only the provided fields; untouched fields stay (view passes full form data)."""
    for name, value in fields.items():
        setattr(va, name, value)
    va.full_clean()
    va.save()
    return va


@transaction.atomic
def add_capability(
    *,
    holder: Holder,
    skill: Skill,
    level: str = SkillLevel.BEGINNER,
    tasks: str = "",
) -> Capability:
    """Attach a registry skill (with proficiency + tasks) to exactly one holder."""
    kwargs: dict[str, Any] = {
        "skill": skill,
        "level": level,
        "tasks": tasks,
    }
    if isinstance(holder, ProviderProfile):
        kwargs["provider_profile"] = holder
    else:
        kwargs["va_profile"] = holder
    capability = Capability(**kwargs)  # type: ignore[arg-type]
    capability.full_clean()
    capability.save()
    return capability


def update_capability(
    *,
    capability: Capability,
    skill: Skill,
    level: str,
    tasks: str = "",
) -> Capability:
    """full_clean runs before save, so a rejected update writes nothing."""
    capability.skill = skill
    capability.level = level
    capability.tasks = tasks
    capability.full_clean()
    capability.save()
    return capability


def delete_capability(*, capability: Capability) -> None:
    capability.delete()
