"""Team forms — input validation only; writes go through services."""

from django import forms

from .models import SkillLevel, VAProfile


class VAForm(forms.ModelForm):
    """Create/update a team member. All fields map 1:1 to update_va_profile."""

    class Meta:
        model = VAProfile
        fields = [
            "display_name",
            "is_active",
            "rate_basis",
            "rate_per_hour",
            "project_rate",
            "currency",
            "availability_hours_per_week",
            "timezone",
            "languages",
            "industry_experience",
            "notes",
        ]
        widgets = {
            "rate_basis": forms.Select(
                attrs={
                    "class": "w-full rounded-[9px] border border-dw-line bg-white "
                    "px-2.5 py-2 text-[13.5px]"
                }
            ),
            "project_rate": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "rate_basis": "Which rate matching uses — never converted across bases.",
            "project_rate": "One-time fixed price per engagement (per-project basis).",
        }


class SkillForm(forms.Form):
    """Add/update a capability on the freelancer profile or a team VA."""

    skill = forms.CharField(
        max_length=120,
        label="Skill name",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Email marketing"}),
    )
    level = forms.ChoiceField(
        choices=SkillLevel.choices,
        initial=SkillLevel.BEGINNER,
        label="Level",
    )
    tasks = forms.CharField(
        max_length=255,
        required=False,
        label="Tasks — what do you actually do?",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g. Klaviyo flows, campaign copy, list management"}
        ),
    )
