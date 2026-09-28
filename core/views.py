"""Thin views — no business logic here; services/selectors live in domain apps."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def home(request: HttpRequest) -> HttpResponse:
    """Landing surface: anonymous visitors go to sign-in; the real dashboard is Card 9."""
    if not request.user.is_authenticated:
        return redirect("account_login")
    return render(request, "home.html")
