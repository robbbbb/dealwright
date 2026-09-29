"""Card 4 — supply-side models: provider profile (freelancer|team), Team roster, Capability.

Design refs: mvp-build-plan.md Card 4; design-log Q9 (provider personas), D4
(advanced > intermediate > beginner weighting feeds Card 5 matching). Tenancy rule:
top-level models carry an ``owner`` FK — Capability hangs off its parent
(ProviderProfile or VAProfile) and inherits tenancy from it.

Deviation from the build plan (design-log entry at card close, Robb decision
2026-09-29): the claimed/verified evidence ladder is superseded by a proficiency
ladder — beginner/intermediate/advanced — plus a free-text ``tasks`` description
of what the holder actually does with the skill. Matching weights advanced
highest. Green "verified" chip semantics stay reserved for future verification.

Protected personal characteristics (gender, age, religion, ethnicity, …) do not
exist in this schema by design; a test asserts their absence (Card 4 TDD).
"""

from typing import cast

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class DeliveryMode(models.TextChoices):
    """Q9: same want must generate different output for a freelancer vs a small team."""

    SOLO = "solo", "Freelancer"
    TEAM = "team", "Team"


class RateBasis(models.TextChoices):
    """How a team member charges. Never convert between bases — matching compares
    like with like only (hourly vs hourly); project rates surface on the one-time
    (setup) side of proposals, exactly like catalog setup prices."""

    HOURLY = "hourly", "Hourly"
    PROJECT = "project", "Per project"


class SkillLevel(models.TextChoices):
    """Self-reported proficiency ladder; ascending rank feeds Card 5 weighting."""

    # Knows the basics — needs guidance or supervision on real work.
    BEGINNER = "beginner", "Beginner"

    # Works independently on routine tasks; asks for help on edge cases.
    INTERMEDIATE = "intermediate", "Intermediate"

    # Owns it end to end — can design, execute, and teach it. Highest match weight.
    ADVANCED = "advanced", "Advanced"


_LEVEL_RANK: dict[str, int] = {
    SkillLevel.BEGINNER: 0,
    SkillLevel.INTERMEDIATE: 1,
    SkillLevel.ADVANCED: 2,
}


class ProviderProfile(models.Model):
    """The Dealwright account holder's delivery identity (Q9)."""

    owner = models.OneToOneField(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_profile",
    )
    delivery_mode = models.CharField(
        "delivery mode",
        max_length=10,
        choices=DeliveryMode.choices,
        default=DeliveryMode.SOLO,
        help_text=(
            "Freelancer = deal self-qualification; Team = small crew combining "
            "skills, ranked team shortlists."
        ),
    )
    branding_name = models.CharField(
        "branding name",
        max_length=120,
        blank=True,
        help_text="Name shown in proposals; falls back to the account name.",
    )
    persona = models.TextField(
        "persona",
        blank=True,
        help_text="Positioning statement; the writer model uses it for narrative slots.",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        verbose_name = "provider profile"
        verbose_name_plural = "provider profiles"

    def __str__(self) -> str:
        return f"{self.display_name} ({self.get_delivery_mode_display()})"

    @property
    def display_name(self) -> str:
        if self.branding_name:
            return self.branding_name
        user = self.owner
        return user.get_full_name() or user.get_username()


class VAProfile(models.Model):
    """One team member of a team-mode provider. Rate/availability/timezone/language
    are the Card 5 hard filters; industry experience is soft context only."""

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="va_profiles",
    )
    display_name = models.CharField("display name", max_length=120)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Inactive members stay on the team record but never match.",
    )
    rate_basis = models.CharField(
        "rate basis",
        max_length=10,
        choices=RateBasis.choices,
        default=RateBasis.HOURLY,
        help_text="Which rate field matching uses — never converted across bases.",
    )
    rate_per_hour = models.DecimalField(
        "rate per hour",
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Used when rate basis is hourly; Q3 currency passthrough, no FX.",
    )
    project_rate = models.DecimalField(
        "project rate",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="One-time fixed price per engagement; used when rate basis is project.",
    )
    currency = models.CharField("currency", max_length=3, default="PHP")
    availability_hours_per_week = models.PositiveSmallIntegerField(
        "availability (hrs/week)",
        default=40,
    )
    timezone = models.CharField("timezone", max_length=64, default="Asia/Manila")
    languages = models.CharField(
        "languages",
        max_length=200,
        blank=True,
        help_text="Comma-separated, e.g. 'English, Tagalog'. Hard filter in matching.",
    )
    industry_experience = models.CharField(
        "industry experience",
        max_length=200,
        blank=True,
        help_text="Comma-separated, e.g. 'e-commerce, podcasts'.",
    )
    notes = models.TextField("notes", blank=True)
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        verbose_name = "VA profile"
        verbose_name_plural = "VA profiles"
        ordering = ["display_name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rate_per_hour__gte=0),
                name="dw_va_rate_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(project_rate__isnull=True) | models.Q(project_rate__gte=0),
                name="dw_va_project_rate_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(availability_hours_per_week__gte=0),
                name="dw_va_availability_non_negative",
            ),
            models.UniqueConstraint(
                fields=["owner", "display_name"],
                name="dw_va_name_unique_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.display_name

    @property
    def engagement_incomplete(self) -> bool:
        """Commercial terms still at defaults — Card 5 excludes these members
        (with an explicit reason) and the roster shows 'Rates not set'."""
        if self.rate_basis == "project":
            return self.project_rate is None
        return not self.rate_per_hour

    def clean(self) -> None:
        """Shape integrity (services call full_clean before save; admin too)."""
        super().clean()
        if self.rate_basis == RateBasis.PROJECT and self.project_rate is None:
            raise ValidationError(
                {"project_rate": "Per-project team members need a project rate."}
            )


class Capability(models.Model):
    """A skill attached to exactly one holder: the freelancer or a team VA.

    ``level`` is self-reported proficiency; ``tasks`` says what the holder actually
    does with the skill — the concrete line proposals show, e.g.
    'Email marketing (Advanced): Klaviyo flows, campaign copy, list management'.
    """

    provider_profile = models.ForeignKey(
        ProviderProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="capabilities",
    )
    va_profile = models.ForeignKey(
        VAProfile,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="capabilities",
    )
    skill = models.CharField("skill", max_length=120, db_index=True)
    level = models.CharField(
        "level",
        max_length=12,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
    )
    tasks = models.CharField(
        "tasks — what you do",
        max_length=255,
        blank=True,
        help_text="Concrete work, e.g. 'Klaviyo flows, campaign copy, list management'.",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        verbose_name = "capability"
        verbose_name_plural = "capabilities"
        ordering = ["skill"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(provider_profile__isnull=False, va_profile__isnull=True)
                | models.Q(provider_profile__isnull=True, va_profile__isnull=False),
                name="dw_cap_exactly_one_holder",
            ),
            models.UniqueConstraint(
                fields=["provider_profile", "skill"],
                condition=models.Q(provider_profile__isnull=False),
                name="dw_cap_skill_unique_per_provider",
            ),
            models.UniqueConstraint(
                fields=["va_profile", "skill"],
                condition=models.Q(va_profile__isnull=False),
                name="dw_cap_skill_unique_per_va",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.skill} ({self.get_level_display()})"

    def clean(self) -> None:
        """Shape integrity (services call full_clean before save; admin too)."""
        super().clean()
        if self.provider_profile_id is not None and self.va_profile_id is not None:
            raise ValidationError(
                "A capability belongs to either the provider or one VA — not both."
            )

    @property
    def trust_rank(self) -> int:
        return _LEVEL_RANK[cast(SkillLevel, self.level)]
