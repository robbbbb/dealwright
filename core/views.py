"""Thin views — no business logic here; services/selectors live in domain apps."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    """Public landing for anonymous visitors; app home for signed-in users (dashboard: Card 9)."""
    if not request.user.is_authenticated:
        return render(request, "landing.html")
    return render(request, "home.html")
