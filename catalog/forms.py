"""Catalog forms — input validation only; writes go through services."""

from __future__ import annotations

from django import forms

from team.models import Skill

from .models import RequiredSkill, Service, ServiceCategory

_CURRENCY_CHOICES = [
    ("PHP", "PHP ₱"), ("USD", "USD $"), ("EUR", "EUR €"), ("GBP", "GBP £"),
    ("AUD", "AUD A$"), ("CAD", "CAD C$"), ("SGD", "SGD S$"),
]


class ServiceForm(forms.ModelForm):
    """Provider-editable service fields; category picked from the owner's rows."""

    category = forms.ModelChoiceField(
        queryset=ServiceCategory.objects.none(),
        label="Category",
        empty_label="Select a category",
        help_text="Pick from your categories — add new ones from the catalog page.",
    )

    tags_text = forms.CharField(
        max_length=400,
        required=False,
        label="Problem tags",
        widget=forms.TextInput(attrs={"placeholder": "e.g. leads-lost, slow-response"}),
        help_text="Comma-separated; used to match services to client problems.",
    )

    class Meta:
        model = Service
        fields = [
            "category", "name", "currency",
            "setup_low", "setup_high", "monthly_low", "monthly_high",
            "custom_quote", "delivery_days_min", "delivery_days_max",
        ]
        widgets = {
            "currency": forms.Select(attrs={}, choices=_CURRENCY_CHOICES),
            "delivery_days_min": forms.NumberInput(attrs={"min": 0}),
            "delivery_days_max": forms.NumberInput(attrs={"min": 0}),
        }
        help_texts = {
            "currency": "Prices are declared per currency and never converted (Q3).",
            "custom_quote": "Priced per engagement instead of from ranges.",
        }

    def __init__(self, owner: object, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = ServiceCategory.objects.filter(
            owner=owner
        ).order_by("name")
        if self.instance.pk and self.instance.problem_tags:
            self.fields["tags_text"].initial = ", ".join(self.instance.problem_tags)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean()
        tags_text = str(cleaned.get("tags_text") or "").strip()
        cleaned["problem_tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]
        return cleaned


class CategoryForm(forms.Form):
    """Create a category row — the catalog vocabulary surface (like team skills)."""

    name = forms.CharField(
        max_length=80,
        label="Category name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Lead capture & CRM automation"}),
    )


class RequiredSkillForm(forms.Form):
    """Add a registry skill (with minimum level) to a service — dropdown, FK."""

    skill = forms.ModelChoiceField(queryset=Skill.objects.none(), label="Skill")
    min_level = forms.ChoiceField(
        choices=RequiredSkill._meta.get_field("min_level").choices,
        initial="beginner",
        label="Minimum level",
    )

    def __init__(self, owner: object, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["skill"].queryset = Skill.objects.filter(owner=owner).order_by("name")
