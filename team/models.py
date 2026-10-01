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

Robb decision 2026-09-30 (design-log): skill NAMES are no longer free text —
they live in a provider-owned Skill registry. Capability (team app) and
RequiredSkill (catalog app) both reference it by FK, so Card 5 matches on exact
joins instead of string heuristics. The proficiency ladder above is unchanged.

Protected personal characteristics (gender, age, religion, ethnicity, …) do not
exist in this schema by design; a test asserts their absence (Card 4 TDD).
"""

from typing import cast

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


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


def _unique_slug(queryset, base: str, exclude_pk: int | None) -> str:
    """First free `base`, `base-2`, `base-3`, … within the queryset's scope."""
    candidate, counter = base, 1
    while queryset.filter(slug=candidate).exclude(pk=exclude_pk).exists():
        counter += 1
        candidate = f"{base}-{counter}"
    return candidate


_LEVEL_RANK: dict[str, int] = {
    SkillLevel.BEGINNER: 0,
    SkillLevel.INTERMEDIATE: 1,
    SkillLevel.ADVANCED: 2,
}


class EngagementTermsMixin(models.Model):
    """Commercial terms shared by the account holder (ProviderProfile) and each
    team member (VAProfile) — one model powers both About-me and matching, no
    duplicate systems (design-log 2026-09-29). Rate basis/currency are
    declarations, never converted (Q3 no-FX); rate/availability/timezone/language
    are the Card 5 hard filters. ``industry_experience``/``notes`` stay VA-only —
    provider positioning is ``persona``."""

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
        validators=[MinValueValidator(0)],
        help_text="Used when rate basis is hourly; Q3 currency passthrough, no FX.",
    )
    project_rate = models.DecimalField(
        "project rate",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="One-time fixed price per engagement; used when rate basis is project.",
    )
    currency = models.CharField("currency", max_length=3, default="PHP")
    availability_hours_per_week = models.PositiveSmallIntegerField(
        "availability (hrs/week)",
        default=40,
        validators=[MinValueValidator(0)],
    )
    timezone = models.CharField("timezone", max_length=64, default="Asia/Manila")
    languages = models.CharField(
        "languages",
        max_length=200,
        blank=True,
        default="",
        help_text="Comma-separated, e.g. 'English, Tagalog'. Hard filter in matching.",
    )

    class Meta:
        abstract = True

    def clean(self) -> None:
        """Shape integrity (services call full_clean before save; admin too)."""
        super().clean()
        if self.rate_basis == RateBasis.PROJECT and self.project_rate is None:
            raise ValidationError(
                {"project_rate": "Per-project team members need a project rate."}
            )

    @property
    def engagement_incomplete(self) -> bool:
        """Commercial terms still at defaults — Card 5 excludes these holders
        (with an explicit reason) and surfaces show 'Rates not set'."""
        if self.rate_basis == "project":
            return self.project_rate is None
        return not self.rate_per_hour


class ProviderProfile(EngagementTermsMixin, models.Model):
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
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rate_per_hour__gte=0),
                name="dw_provider_rate_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(project_rate__isnull=True) | models.Q(project_rate__gte=0),
                name="dw_provider_project_rate_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(availability_hours_per_week__gte=0),
                name="dw_provider_availability_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.display_name} ({self.get_delivery_mode_display()})"

    @property
    def display_name(self) -> str:
        if self.branding_name:
            return self.branding_name
        user = self.owner
        return user.get_full_name() or user.get_username()


class VAProfile(EngagementTermsMixin, models.Model):
    """One team member of a team-mode provider. Commercial terms come from the
    shared EngagementTermsMixin; rate/availability/timezone/language are the
    Card 5 hard filters; industry experience is soft context only."""

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="va_profiles",
    )
    display_name = models.CharField("display name", max_length=120)
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation; renames never break links
        help_text="URL name — set at creation from the display name, unique per owner.",
    )
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Inactive members stay on the team record but never match.",
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
            models.UniqueConstraint(
                fields=["owner", "slug"],
                name="dw_va_slug_unique_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = _unique_slug(
                VAProfile.objects.filter(owner=self.owner),
                slugify(self.display_name) or "member",
                self.pk,
            )
        super().save(*args, **kwargs)


class Skill(models.Model):
    """One named skill in the provider's own vocabulary — the shared registry.

    Both Capability (who has it, team app) and RequiredSkill (what a service
    needs, catalog app) reference this table by FK. Registry rows are
    load-bearing for matching: PROTECTed from deletion while referenced.
    """

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField("name", max_length=120)
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation from the name
        help_text="URL name — set at creation from the skill name, unique per owner.",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        verbose_name = "skill"
        verbose_name_plural = "skills"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="dw_skill_unique_per_owner",
            ),
            models.UniqueConstraint(
                fields=["owner", "slug"],
                name="dw_skill_slug_unique_per_owner",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = _unique_slug(
                Skill.objects.filter(owner=self.owner),
                slugify(self.name) or "skill",
                self.pk,
            )
        super().save(*args, **kwargs)


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
    skill = models.ForeignKey(  # type: ignore[var-annotated]
        Skill,
        on_delete=models.PROTECT,
        related_name="capabilities",
        verbose_name="skill",
        help_text="Registry row — exact FK join feeds Card 5 matching.",
    )
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation from the skill name
        help_text="URL name — set at creation from the skill name, unique per owner.",
    )
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
            models.UniqueConstraint(
                fields=["provider_profile", "slug"],
                condition=models.Q(provider_profile__isnull=False),
                name="dw_cap_slug_unique_per_provider",
            ),
            models.UniqueConstraint(
                fields=["va_profile", "slug"],
                condition=models.Q(va_profile__isnull=False),
                name="dw_cap_slug_unique_per_va",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.skill} ({self.get_level_display()})"

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug and (self.provider_profile_id or self.va_profile_id):
            holder_owner = (
                self.provider_profile.owner if self.provider_profile_id else self.va_profile.owner
            )
            self.slug = _unique_slug(
                Capability.objects.filter(
                    Q(provider_profile__owner=holder_owner) | Q(va_profile__owner=holder_owner)
                ),
                slugify(self.skill.name) or "skill",
                self.pk,
            )
        super().save(*args, **kwargs)  # orphans still hit the DB check constraint

    def clean(self) -> None:
        """Shape integrity (services call full_clean before save; admin too)."""
        super().clean()
        if self.provider_profile_id is not None and self.va_profile_id is not None:
            raise ValidationError(
                "A capability belongs to either the provider or one VA — not both."
            )
        holder_owner = (
            self.provider_profile.owner if self.provider_profile_id
            else self.va_profile.owner if self.va_profile_id
            else None
        )
        if holder_owner is not None and self.skill_id and self.skill.owner_id != holder_owner.pk:
            raise ValidationError(
                {"skill": "Skill must come from this provider's own registry."}
            )

    @property
    def trust_rank(self) -> int:
        return _LEVEL_RANK[cast(SkillLevel, self.level)]
