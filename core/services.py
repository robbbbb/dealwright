"""Auth plumbing services — thin allauth integrations, no Dealwright business logic."""

from __future__ import annotations

import hashlib

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpRequest

# Max verification emails per address per rolling window (email-bombing guard).
_RESEND_LIMIT = 5
_RESEND_WINDOW_SECONDS = 60 * 60


def _resend_cache_key(email: str) -> str:
    digest = hashlib.sha256(email.strip().lower().encode()).hexdigest()[:32]
    return f"dw:resend-confirmation:{digest}"


def resend_confirmation_email(request: HttpRequest, email: str) -> bool:
    """Re-send the verification email for ``email``.

    Anti-enumeration (Q13): callers must render the same response whether or not
    the address exists — the return value is only for tests/telemetry. Sends are
    capped per address per hour regardless of account existence.
    """
    key = _resend_cache_key(email)
    count = cache.get(key)
    if count is None:
        cache.set(key, 1, timeout=_RESEND_WINDOW_SECONDS)
    elif count >= _RESEND_LIMIT:
        return False
    else:
        cache.incr(key)

    sent = False
    # Email addresses are shared by multiple accounts; cap the fan-out.
    addresses = EmailAddress.objects.filter(email__iexact=email.strip(), verified=False)[
        :_RESEND_LIMIT
    ]
    for address in addresses:
        if get_adapter().should_send_confirmation_mail(request, address, signup=False):
            address.send_confirmation(request, signup=False)
            get_adapter().add_message(
                request,
                messages.INFO,
                "account/messages/email_confirmation_sent.txt",
                {"email": address.email, "login": False, "signup": False},
            )
            sent = True
    return sent
