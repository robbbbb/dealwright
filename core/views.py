"""Thin views — no business logic here; services/selectors live in domain apps."""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from core import services
from core.forms import ResendConfirmationForm


def home(request: HttpRequest) -> HttpResponse:
    """Public landing for anonymous visitors; app home for signed-in users (dashboard: Card 9)."""
    if not request.user.is_authenticated:
        return render(request, "landing.html")
    return render(request, "home.html")


def resend_confirmation(request: HttpRequest) -> HttpResponse:
    """Re-send a verification email (auth mockup, frame 3).

    The response is identical whether or not the address exists (anti-enumeration,
    Q13); the actual send is capped per address in the service. The rendered form
    (verified_email_required.html) posts the signed-in user's address in a hidden
    field; the view falls back to it for authenticated users.
    """
    if request.method != "POST":
        return redirect("account_login")
    data = request.POST.copy()
    if not data.get("email") and request.user.is_authenticated:
        data["email"] = request.user.email
    form = ResendConfirmationForm(data)
    if form.is_valid():
        services.resend_confirmation_email(request, form.cleaned_data["email"])
        messages.info(
            request,
            "If that address needs confirmation, a new link is on its way. "
            "Check spam if it doesn't arrive in a few minutes.",
        )
        return redirect("account_email_verification_sent")
    return redirect("account_login")
