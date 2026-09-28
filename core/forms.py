"""Auth forms — input validation only (auth mockup, frame 2).

Subclassing allauth's SignupForm is the library's sanctioned extension point
for extra signup fields (``ACCOUNT_FORMS``); persistence happens through the
standard allauth signup flow that calls ``save()``.
"""

from __future__ import annotations

from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.contrib.auth.base_user import AbstractBaseUser


class SignupForm(AllauthSignupForm):
    """Email/password signup with full name and terms acceptance (mockup frame 2)."""

    field_order = ["name", "email", "password1", "password2", "terms"]

    name = forms.CharField(
        label="Full name",
        max_length=150,
        strip=True,
    )
    terms = forms.BooleanField(
        label="I agree to the Terms & Privacy Policy",
        error_messages={"required": "Please accept the Terms & Privacy Policy to continue."},
    )

    def clean_name(self) -> str:
        return " ".join(self.cleaned_data["name"].split())

    def save(self, request) -> AbstractBaseUser:
        """Create the user via allauth, then map the full name onto name fields."""
        user = super().save(request)
        first_name, _, last_name = self.cleaned_data["name"].partition(" ")
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=["first_name", "last_name"])
        return user


class ResendConfirmationForm(forms.Form):
    """Email input for the "Resend confirmation" button (mockup frame 3)."""

    email = forms.EmailField(label="Email", max_length=254)
