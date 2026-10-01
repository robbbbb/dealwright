"""Team selectors — all reads live here; views never filter querysets inline."""

from typing import Any

from django.db.models import Count, Q, QuerySet

from .models import Capability, ProviderProfile, Skill, VAProfile


def list_vas(owner: Any) -> QuerySet[VAProfile]:
    """The owner's whole team (active and inactive; UI shows status)."""
    return VAProfile.objects.filter(owner=owner).prefetch_related("capabilities")


def list_registry_skills(owner: Any) -> QuerySet[Skill]:
    """The owner's vocabulary with total usage (capabilities + requirements),
    so the UI can offer removal only for unused rows."""
    return Skill.objects.filter(owner=owner).annotate(
        uses=Count("capabilities", distinct=True) + Count("required_by", distinct=True)
    )


def get_registry_skill_for_owner(owner: Any, skill_slug: str) -> Skill | None:
    """Ownership-checked registry lookup by slug — None means not found."""
    return Skill.objects.filter(owner=owner, slug=skill_slug).first()


def get_va_for_owner(owner: Any, member_slug: str) -> VAProfile | None:
    """Ownership-checked team member lookup by URL slug — None means not found."""
    return VAProfile.objects.filter(owner=owner, slug=member_slug).first()


def list_holder_capabilities(holder: ProviderProfile | VAProfile) -> QuerySet[Capability]:
    """Capabilities with their registry skill joined — templates render
    cap.skill (FK name) per row, so one select_related beats N+1."""
    return holder.capabilities.select_related("skill")


def get_capability_for_owner(owner: Any, cap_slug: str) -> Capability | None:
    """A capability is addressable only through its holder's owner (tenancy guard)."""
    return (
        Capability.objects.select_related("provider_profile", "va_profile")
        .filter(
            Q(provider_profile__owner=owner) | Q(va_profile__owner=owner),
            slug=cap_slug,
        )
        .first()
    )


def is_mfa_enabled(user: Any) -> bool:
    """A TOTP authenticator exists for this account (allauth.mfa; settings page)."""
    from allauth.mfa.models import Authenticator

    return Authenticator.objects.filter(
        user=user, type=Authenticator.Type.TOTP
    ).exists()
