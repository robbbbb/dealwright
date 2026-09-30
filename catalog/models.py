"""Card 2 — service catalog: the deterministic source of prices and ROI parameters.

Design refs:
- mvp-build-plan.md Card 2 (quantifier rule is the TDD anchor; seed from
  service-catalog-draft.md; admin CRUD in MVP).
- service-catalog-draft.md rules 1-5: quantifier rule, two-part pricing,
  required VA skills feed matching, claims discipline (ranges not points),
  delivery estimate.
- design-log Q8 (8 categories incl. Personal productivity ops), Q3 (currency
  passthrough — no FX, prices in the account's currency).
- team app (Card 4): RequiredSkill reuses the team SkillLevel ladder so Card 5
  matches required levels against Capability levels on one scale.

Money discipline: every figure here is a provider-editable *hypothesis* range,
never AI-generated; proposals always label catalog-derived numbers as estimates.

Protected personal characteristics do not exist in this schema by design.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from team.models import SkillLevel


class Service(models.Model):
    """One sellable service: what it solves, its ROI levers, prices, skills."""

    class RevenueEffect(models.TextChoices):
        """Mechanism + unit for the money lever. Ranges carry the unit's scale."""

        RECOVER_LEADS_PCT = "recover_leads_pct", "Recovered leads (% of missed)"
        CONVERSION_UPLIFT_PCT = "conversion_uplift_pct", "Conversion uplift (%)"
        DSO_DAYS = "dso_days", "Payment days saved (DSO)"

    owner = models.ForeignKey(  # type: ignore[var-annotated]
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="Provider whose catalog this belongs to (custom catalogs are Tier 0).",
    )
    category = models.CharField(
        "category",
        max_length=80,
        db_index=True,
        help_text="Seed ships 8 canonical categories; providers may use their own.",
    )
    name = models.CharField("name", max_length=120)
    problem_tags = models.JSONField(
        "problem tags",
        default=list,
        blank=True,
        help_text="Problems-solved tags, e.g. ['leads-lost', 'slow-response'].",
    )

    # --- ROI levers (quantifier rule: >=1 pair or qualitative flag) ---
    reduction_low = models.DecimalField(
        "time reduction — low (%)",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Automation lever: % of task time removed (Card 3 automation mode).",
    )
    reduction_high = models.DecimalField(
        "time reduction — high (%)",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    hours_saved_low = models.DecimalField(
        "hours saved — low (hrs/week)",
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Delegation lever: weekly hours removed (Card 3 delegation mode).",
    )
    hours_saved_high = models.DecimalField(
        "hours saved — high (hrs/week)",
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
    )
    revenue_effect_type = models.CharField(
        "revenue effect type",
        max_length=30,
        choices=RevenueEffect.choices,
        blank=True,
        help_text="Unit of the money lever; blank unless numbers are declared.",
    )
    revenue_effect_low = models.DecimalField(
        "revenue effect — low",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    revenue_effect_high = models.DecimalField(
        "revenue effect — high",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
    )
    qualitative_value = models.BooleanField(
        "qualitative value only",
        default=False,
        help_text="Honest-but-unquantifiable: proposal's non-financial benefits, never the math.",
    )

    # --- Two-part pricing (ranges, never points; Q3: account currency) ---
    setup_low = models.DecimalField(
        "setup price — low", max_digits=10, decimal_places=2, null=True, blank=True
    )
    setup_high = models.DecimalField(
        "setup price — high", max_digits=10, decimal_places=2, null=True, blank=True
    )
    monthly_low = models.DecimalField(
        "monthly price — low", max_digits=10, decimal_places=2, null=True, blank=True
    )
    monthly_high = models.DecimalField(
        "monthly price — high", max_digits=10, decimal_places=2, null=True, blank=True
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
            models.CheckConstraint(
                condition=models.Q(reduction_low__isnull=True) | models.Q(reduction_low__gte=0),
                name="dw_service_reduction_low_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(hours_saved_low__isnull=True) | models.Q(hours_saved_low__gte=0),
                name="dw_service_hours_low_non_negative",
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
        ("reduction", "reduction_low", "reduction_high"),
        ("hours saved", "hours_saved_low", "hours_saved_high"),
        ("revenue effect", "revenue_effect_low", "revenue_effect_high"),
        ("setup price", "setup_low", "setup_high"),
        ("monthly price", "monthly_low", "monthly_high"),
        ("delivery days", "delivery_days_min", "delivery_days_max"),
    )

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

        has_revenue_numbers = self.revenue_effect_low is not None
        if has_revenue_numbers and not self.revenue_effect_type:
            errors["revenue_effect_type"] = ["Numbers need a revenue effect type (their unit)."]
        if self.revenue_effect_type and not has_revenue_numbers:
            errors["revenue_effect_low"] = ["A revenue effect type needs its numbers."]

        has_roi_parameter = any(
            getattr(self, low_attr) is not None
            for _, low_attr, _ in self._RANGES[:3]
        )
        if not has_roi_parameter and not self.qualitative_value:
            errors["qualitative_value"] = [
                "Quantifier rule: declare a reduction/hours/revenue range"
                " or flag qualitative value."
            ]

        if not self.custom_quote and self.setup_low is None and self.monthly_low is None:
            errors["custom_quote"] = [
                "Declare a price range or mark the service custom quote."
            ]

        tags_ok = isinstance(self.problem_tags, list) and all(
            isinstance(t, str) for t in self.problem_tags
        )
        if not tags_ok:
            errors["problem_tags"] = ["Problem tags must be a list of strings."]

        if errors:
            raise ValidationError(errors)

    @property
    def has_quantified_lever(self) -> bool:
        return any(getattr(self, low_attr) is not None for _, low_attr, _ in self._RANGES[:3])

    def price_summary(self) -> str:
        """Range-not-points display for admin/lists; estimates always."""
        parts: list[str] = []
        if self.setup_low is not None:
            parts.append(f"setup ₱{self.setup_low:,.0f}–{self.setup_high:,.0f}")
        if self.monthly_low is not None:
            parts.append(f"monthly ₱{self.monthly_low:,.0f}–{self.monthly_high:,.0f}")
        return " · ".join(parts) if parts else "Custom quote"


class RequiredSkill(models.Model):
    """A skill (with minimum level) a service needs — feeds Card 5 matching.

    ``skill`` matches Capability.skill by name; ``min_level`` uses the same
    proficiency ladder the team app defines (advanced > intermediate > beginner).
    """

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="required_skills")
    skill = models.CharField("skill", max_length=120, db_index=True)
    min_level = models.CharField(
        "minimum level",
        max_length=12,
        choices=SkillLevel.choices,
        default=SkillLevel.BEGINNER,
        help_text="Draft's 'Verified only' maps to Advanced on the proficiency ladder.",
    )

    class Meta:
        verbose_name = "required skill"
        verbose_name_plural = "required skills"
        ordering = ["skill"]
        constraints = [
            models.UniqueConstraint(
                fields=["service", "skill"], name="dw_reqskill_unique_per_service"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.skill} ≥ {self.get_min_level_display()}"
