"""Team selectors — all reads live here; views never filter querysets inline."""

from typing import Any

from django.db.models import Q, QuerySet

from .models import Capability, ProviderProfile, VAProfile


def list_vas(owner: Any) -> QuerySet[VAProfile]:
    """The owner's whole team (active and inactive; UI shows status)."""
    return VAProfile.objects.filter(owner=owner).prefetch_related("capabilities")


def get_va_for_owner(owner: Any, va_id: int) -> VAProfile | None:
    """Ownership-checked team member lookup — None means not found for this owner."""
    return VAProfile.objects.filter(owner=owner, pk=va_id).first()


def list_holder_capabilities(holder: ProviderProfile | VAProfile) -> QuerySet[Capability]:
    """One query, no join: rows render local columns only (skill/level/note/pk) and
    the holder is already in context — the FKs are never accessed. Add select_related
    here only if templates start rendering holder names from capability rows."""
    return holder.capabilities.all()


def get_capability_for_owner(owner: Any, capability_id: int) -> Capability | None:
    """A capability is addressable only through its holder's owner (tenancy guard)."""
    return (
        Capability.objects.select_related("provider_profile", "va_profile")
        .filter(
            Q(provider_profile__owner=owner) | Q(va_profile__owner=owner),
            pk=capability_id,
        )
        .first()
    )
