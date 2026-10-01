"""Service catalog: what you sell and what it costs — services + prices only.

Robb decision (2026-09-30, design-log): ROI lever fields (reduction, hours,
revenue effect, qualitative flag) were REMOVED from the model — no computation
in the catalog for now. ROI parameters, when Card 3 needs them, will come from
session data and/or a versioned benchmarks table, not from these rows.

Design refs:
- service-catalog-draft.md: two-part pricing, required VA skills feed
  matching, claims discipline (ranges not points), delivery estimate.
- design-log Q8 (8 categories), Q3 (no FX — per-row currency declarations, 2026-09-30).
- team app (Card 4): RequiredSkill reuses the team SkillLevel ladder so Card 5
  matches required levels against Capability levels on one scale.

Money discipline: every figure is a provider-editable *hypothesis* range,
never AI-generated; proposals always label catalog-derived numbers as estimates.

Protected personal characteristics do not exist in this schema by design.
"""

from __future__ import annotations

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from team.models import SkillLevel

_CURRENCY_RE = re.compile(r"[A-Z]{3}")
_CURRENCY_SYMBOLS = {
    "PHP": "₱", "USD": "$", "EUR": "€", "GBP": "£",
    "AUD": "A$", "CAD": "C$", "SGD": "S$",
}


class ServiceCategory(models.Model):
    """One named category in the provider's catalog vocabulary.

    Supersedes the Service CharField category (Robb, 2026-10-01): categories
    are picked, not retyped. Same registry pattern as team.Skill — owner-scoped,
    slug unique per owner and frozen at creation, PROTECTed while referenced.
    """

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_categories",
    )
    name = models.CharField("name", max_length=80)
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation; renames never break links
        help_text="URL name — set at creation from the name, unique per owner.",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        verbose_name = "service category"
        verbose_name_plural = "service categories"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"], name="dw_servicecategory_unique_per_owner"
            ),
            models.UniqueConstraint(
                fields=["owner", "slug"], name="dw_servicecategory_slug_unique_per_owner"
            ),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = self._unique_slug(slugify(self.name) or "category")
        super().save(*args, **kwargs)

    def _unique_slug(self, base: str) -> str:
        candidate, counter = base, 1
        while (
            ServiceCategory.objects.filter(owner=self.owner, slug=candidate)
            .exclude(pk=self.pk)
            .exists()
        ):
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate


class Service(models.Model):
    """One sellable service: what it solves, what it costs, skills it needs."""

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="Provider whose catalog this belongs to (custom catalogs are Tier 0).",
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,  # load-bearing for grouping/matching — not deletable while used
        related_name="services",
        verbose_name="category",
        help_text="Pick from the provider's own category rows (supersedes free text, 2026-10-01).",
    )
    name = models.CharField("name", max_length=120)
    problem_tags = models.JSONField(
        "problem tags",
        default=list,
        blank=True,
        help_text="Problems-solved tags, e.g. ['leads-lost', 'slow-response'].",
    )

    # --- Pricing: setup + monthly retainer (ranges, never points; Q3: no FX) ---
    currency = models.CharField(
        "currency",
        max_length=3,
        default="PHP",
        help_text=(
            "ISO 4217 code. Prices are declared per currency and never converted (Q3) —"
            " create one row per market if you charge in several currencies."
        ),
    )
    setup_low = models.DecimalField(
        "setup price — low", max_digits=10, decimal_places=2, null=True, blank=True
    )
    setup_high = models.DecimalField(
        "setup price — high", max_digits=10, decimal_places=2, null=True, blank=True
    )
    monthly_low = models.DecimalField(
        "retainer — low (monthly)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    monthly_high = models.DecimalField(
        "retainer — high (monthly)", max_digits=10, decimal_places=2, null=True, blank=True
    )
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation; renames never break links
        help_text="URL name — set at creation from the service name, unique per owner.",
    )
    custom_quote = models.BooleanField(
        "custom quote",
        default=False,
        help_text="Priced per engagement instead of from ranges ('— / by hrs' in the draft).",
    )
    delivery_days_min = models.PositiveSmallIntegerField(
        "delivery — min days", null=True, blank=True
    )
    delivery_days_max = models.PositiveSmallIntegerField(
        "delivery — max days", null=True, blank=True
    )

    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        verbose_name = "service"
        verbose_name_plural = "services"
        ordering = ["category", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "category", "name"], name="dw_service_unique_per_owner"
            ),
            models.UniqueConstraint(
                fields=["owner", "slug"], name="dw_service_slug_unique_per_owner"
            ),
            models.CheckConstraint(
                condition=models.Q(setup_low__isnull=True) | models.Q(setup_low__gte=0),
                name="dw_service_setup_low_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(monthly_low__isnull=True) | models.Q(monthly_low__gte=0),
                name="dw_service_monthly_low_non_negative",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.category})"

    _RANGES: tuple[tuple[str, str, str], ...] = (
        ("setup price", "setup_low", "setup_high"),
        ("retainer", "monthly_low", "monthly_high"),
        ("delivery days", "delivery_days_min", "delivery_days_max"),
    )

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = self._unique_slug(slugify(self.name) or "service")
        super().save(*args, **kwargs)

    def _unique_slug(self, base: str) -> str:
        candidate, counter = base, 1
        while (
            Service.objects.filter(owner=self.owner, slug=candidate)
            .exclude(pk=self.pk)
            .exists()
        ):
            counter += 1
            candidate = f"{base}-{counter}"
        return candidate

    def clean(self) -> None:
        """Shape integrity — services and admin call full_clean before save."""
        super().clean()
        errors: dict[str, list[str]] = {}

        for label, low_attr, high_attr in self._RANGES:
            low, high = getattr(self, low_attr), getattr(self, high_attr)
            if (low is None) != (high is None):
                errors[low_attr] = [f"{label.capitalize()} needs both ends of the range."]
            elif low is not None and high is not None and low > high:
                errors[high_attr] = [f"{label.capitalize()} low must not exceed high."]

        if not self.custom_quote and self.setup_low is None and self.monthly_low is None:
            errors["custom_quote"] = [
                "Declare a price range or mark the service custom quote."
            ]

        tags_ok = isinstance(self.problem_tags, list) and all(
            isinstance(t, str) for t in self.problem_tags
        )
        if not tags_ok:
            errors["problem_tags"] = ["Problem tags must be a list of strings."]

        # Only judge when both sides are known: ModelForm._post_clean runs
        # full_clean on an instance without owner (applied in the service layer);
        # every real write path sets owner, so cross-owner rows stay impossible.
        if self.category_id and self.owner_id and self.category.owner_id != self.owner_id:
            errors["category"] = ["Category must come from this provider's own list."]

        if not _CURRENCY_RE.fullmatch(self.currency or ""):
            errors["currency"] = ["Use a 3-letter ISO 4217 code, e.g. PHP, USD, EUR."]

        if errors:
            raise ValidationError(errors)

    @property
    def has_quantified_lever(self) -> bool:
        return any(getattr(self, low_attr) is not None for _, low_attr, _ in self._RANGES[:3])

    def currency_symbol(self) -> str:
        """Display symbol; unknown codes fall back to the code itself (no invented glyphs)."""
        return _CURRENCY_SYMBOLS.get(self.currency, f"{self.currency} ")

    def price_summary(self) -> str:
        """Range-not-points display for admin/lists; estimates always."""
        parts: list[str] = []
        sym = self.currency_symbol()
        if self.setup_low is not None:
            parts.append(f"setup {sym}{self.setup_low:,.0f}–{self.setup_high:,.0f}")
        if self.monthly_low is not None:
            parts.append(f"retainer {sym}{self.monthly_low:,.0f}–{self.monthly_high:,.0f}/mo")
        return " · ".join(parts) if parts else "Custom quote"


class RequiredSkill(models.Model):
    """A skill (with minimum level) a service needs — feeds Card 5 matching.

    ``skill`` is a registry row (team.Skill) — exact FK join against
    Capability, never string matching; ``min_level`` uses the same
    proficiency ladder the team app defines (advanced > intermediate > beginner).
    """

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="required_skills")
    skill = models.ForeignKey(  # type: ignore[var-annotated]
        "team.Skill",
        on_delete=models.PROTECT,
        related_name="required_by",
        verbose_name="skill",
    )
    min_level = models.CharField(
        "minimum level",
        max_length=12,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
        help_text="Draft's 'Verified only' maps to Advanced on the proficiency ladder.",
    )
    slug = models.SlugField(
        "slug",
        max_length=140,
        blank=True,  # generated once at creation from the skill name
        help_text="URL name — set at creation from the skill name, unique per service.",
    )

    class Meta:
        verbose_name = "required skill"
        verbose_name_plural = "required skills"
        ordering = ["skill"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "skill"], name="dw_reqskill_unique_per_service"
            ),
            models.UniqueConstraint(
                fields=["service", "slug"], name="dw_reqskill_slug_unique_per_service"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.skill} ≥ {self.get_min_level_display()}"

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            base = slugify(self.skill.name) or "skill"
            candidate, counter = base, 1
            while (
                RequiredSkill.objects.filter(service=self.service, slug=candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                counter += 1
                candidate = f"{base}-{counter}"
            self.slug = candidate
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Tenancy guard — a required skill must come from the service owner's registry."""
        from django.core.exceptions import ValidationError

        if self.service_id and self.skill_id:
            if self.skill.owner_id != self.service.owner_id:
                raise ValidationError(
                    {"skill": "Skill must come from this provider's own registry."}
                )
