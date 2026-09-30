"""Team forms — input validation only; writes go through services."""

from django import forms

from .models import Skill, SkillLevel, VAProfile

_SELECT_CLASS = (
    "w-full rounded-[9px] border border-dw-line bg-white px-2.5 py-2 text-[13.5px]"
)


class TeamMemberForm(forms.ModelForm):
    """Identity fields only — adding a member needs a name, nothing else."""

    class Meta:
        model = VAProfile
        fields = ["display_name", "is_active", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}


class EngagementForm(forms.ModelForm):
    """Rates & availability — per-member commercial terms (Card 5 hard filters).

    Kept in VAProfile per design pass 2026-09-29; shown on the detail page,
    never required at member creation (Card 5 excludes incomplete members
    with an explicit reason instead of filtering on silent defaults).
    """

    class Meta:
        model = VAProfile
        fields = [
            "rate_basis",
            "rate_per_hour",
            "project_rate",
            "currency",
            "availability_hours_per_week",
            "timezone",
            "languages",
            "industry_experience",
        ]
        widgets = {
            "rate_basis": forms.Select(attrs={"class": _SELECT_CLASS}),
            "currency": forms.Select(
                attrs={"class": _SELECT_CLASS},
                choices=[("PHP", "PHP"), ("USD", "USD")],
            ),
            "project_rate": forms.NumberInput(attrs={"step": "0.01"}),
        }
        help_texts = {
            "rate_basis": "Which rate matching uses — never converted across bases.",
            "project_rate": "One-time fixed price per engagement (per-project basis).",
        }


class SkillForm(forms.Form):
    """Add/update a capability on the freelancer profile or a team member."""

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
        widget=forms.Textarea(
            attrs={
                "rows": 2,
                "placeholder": "e.g. Klaviyo flows, campaign copy, list management",
            }
        ),
    )


class SkillPickForm(forms.Form):
    """Attach one of the owner's registry skills to a team member (dropdown, FK)."""

    skill = forms.ModelChoiceField(queryset=Skill.objects.none(), label="Skill")
    level = forms.ChoiceField(
        choices=SkillLevel.choices,
        initial=SkillLevel.BEGINNER,
        label="Level",
    )
    tasks = forms.CharField(
        max_length=255,
        required=False,
        label="Tasks — what do they actually do?",
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, owner: object, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["skill"].queryset = Skill.objects.filter(owner=owner).order_by("name")
