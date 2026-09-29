"""Thin views — no business logic here; services/selectors live in domain apps."""

from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from core import services
from core.forms import ResendConfirmationForm


def home(request: HttpRequest) -> HttpResponse:
    """Public landing for anonymous visitors; dashboard shell for signed-in users.

    The dashboard is presentation-only until Cards 1-8 provide the domain data;
    Card 9 wires the real lists and counters (docs/design/mvp-build-plan.md).
    """
    if not request.user.is_authenticated:
        return render(request, "landing.html")
    hour = timezone.localtime().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    return render(
        request,
        "dashboard.html",
        {
            "greeting": greeting,
            "greeting_name": request.user.first_name or request.user.email,
            "today": timezone.localtime(),
        },
    )


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
