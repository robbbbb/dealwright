"""Auth screens smoke tests (templates & UI tier) — docs/mockups/auth-mockup.html.

Through public APIs only: views, forms, and the response surfaces.
"""

import re

import pytest
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.mfa.totp.internal import auth as totp_auth
from django.contrib.auth.models import User
from django.core import mail
from django.shortcuts import render
from django.test import Client, RequestFactory
from django.urls import reverse

from core.templatetags.dw_auth import google_available

PASSWORD = "quiet-ember-loop-42"


def create_user(email: str = "rob@example.com", password: str = PASSWORD) -> User:
    return User.objects.create_user(username=email, email=email, password=password)


def login(client: Client, email: str, password: str) -> None:
    """Full allauth password login (writes allauth's authentication record)."""
    response = client.post(reverse("account_login"), {"login": email, "password": password})
    assert response.status_code == 302


def totp_code(secret: str) -> str:
    counter = next(iter(totp_auth.yield_hotp_counters_from_time()))
    return totp_auth.format_hotp_value(totp_auth.hotp_value(secret, counter))


# ---------------------------------------------------------------- frame 1: login


@pytest.mark.django_db
def test_login_page_renders(client: Client) -> None:
    response = client.get(reverse("account_login"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Welcome back" in content
    assert "Remember me" in content
    assert "Forgot password?" in content
    assert "Create an account" in content
    assert "From notes to numbers you can defend." in content


@pytest.mark.django_db
def test_login_google_button_hidden_without_credentials(client: Client) -> None:
    """No Google button when the provider is unconfigured — hermetic vs .env."""
    from allauth.socialaccount.providers import registry

    saved = registry.provider_map.pop("google", None)
    try:
        content = client.get(reverse("account_login")).content.decode()
        assert "Continue with Google" not in content
    finally:
        if saved is not None:
            registry.provider_map["google"] = saved


@pytest.mark.django_db
def test_login_rejects_bad_password(client: Client) -> None:
    create_user()
    response = client.post(
        reverse("account_login"), {"login": "rob@example.com", "password": "wrong-pass-1"}
    )
    content = response.content.decode()
    assert response.status_code == 200
    assert "errorlist" in content


@pytest.mark.django_db
def test_google_available_false_without_provider() -> None:
    from allauth.socialaccount.providers import registry

    saved = registry.provider_map.pop("google", None)
    try:
        assert google_available() is False
    finally:
        if saved is not None:
            registry.provider_map["google"] = saved


# ---------------------------------------------------------------- frame 2: signup


@pytest.mark.django_db
def test_signup_page_renders(client: Client) -> None:
    response = client.get(reverse("account_signup"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Create your account" in content
    assert "Full name" in content
    assert "14-day Professional trial" in content
    assert "Terms &amp; Privacy Policy" in content
    assert "At least 10 characters" in content


@pytest.mark.django_db
def test_signup_creates_user_with_full_name(client: Client) -> None:
    response = client.post(
        reverse("account_signup"),
        {
            "name": "Robb Rodriguez",
            "email": "rob@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
            "terms": "on",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(email="rob@example.com")
    assert user.first_name == "Robb"
    assert user.last_name == "Rodriguez"
    assert EmailAddress.objects.filter(email="rob@example.com", user=user).exists()
    assert len(mail.outbox) == 1  # verification email sent on signup


@pytest.mark.django_db
def test_signup_requires_terms(client: Client) -> None:
    response = client.post(
        reverse("account_signup"),
        {
            "name": "Robb",
            "email": "rob@example.com",
            "password1": PASSWORD,
            "password2": PASSWORD,
        },
    )
    assert response.status_code == 200
    assert not User.objects.filter(email="rob@example.com").exists()
    assert "Please accept the Terms" in response.content.decode()


@pytest.mark.django_db
def test_signup_enforces_min_length(client: Client) -> None:
    response = client.post(
        reverse("account_signup"),
        {
            "name": "Robb",
            "email": "rob@example.com",
            "password1": "short-pw1",
            "password2": "short-pw1",
            "terms": "on",
        },
    )
    assert response.status_code == 200
    assert not User.objects.filter(email="rob@example.com").exists()


# ---------------------------------------------------------------- frame 3: verify email


@pytest.mark.django_db
def test_verification_sent_renders(client: Client) -> None:
    response = client.get(reverse("account_email_verification_sent"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Check your inbox" in content
    assert "Click the link in the email" in content


@pytest.mark.django_db
def test_verified_email_required_template(client: Client) -> None:
    user = create_user()
    request = RequestFactory().get("/")
    request.user = user

    response = render(request, "account/verified_email_required.html")
    content = response.content.decode()
    assert "Check your inbox" in content
    assert user.email in content
    assert reverse("resend_confirmation") in content
    # The rendered form posts the user's address in a hidden field (review fix).
    assert f'name="email" value="{user.email}"' in content


@pytest.mark.django_db
def test_resend_confirmation_sends_and_is_anti_enumeration(client: Client) -> None:
    user = create_user()
    EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
    url = reverse("resend_confirmation")
    # Unknown address: same response, no mail.
    response = client.post(url, {"email": "ghost@example.com"})
    assert response.status_code == 302
    assert not mail.outbox
    # Known address, exact rendered-form payload (csrf + hidden email): mail sent.
    response = client.post(url, {"email": user.email})
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    # Logged-in fallback: posting the bare rendered form (no email field) still
    # resolves the address from the session user.
    client.force_login(user)
    response = client.post(url, {})
    assert response.status_code == 302
    assert len(mail.outbox) == 2
    # GET is not an entry point.
    assert client.get(url).status_code == 302


# ---------------------------------------------------------------- frames 4-5: password reset


@pytest.mark.django_db
def test_password_reset_is_anti_enumeration(client: Client) -> None:
    create_user()
    response = client.post(reverse("account_reset_password"), {"email": "ghost@example.com"})
    assert response.status_code == 302
    response2 = client.post(reverse("account_reset_password"), {"email": "rob@example.com"})
    assert response.url == response2.url  # identical landing — cannot probe accounts


@pytest.mark.django_db
def test_password_reset_full_flow(client: Client) -> None:
    create_user()
    client.post(reverse("account_reset_password"), {"email": "rob@example.com"})
    assert len(mail.outbox) == 1
    match = re.search(r"https?://[^\s\"]+", mail.outbox[0].body)
    assert match
    reset_url = match.group(0).split("/accounts/")[-1]
    # Link opened from the email validates the token and redirects to the form.
    token_resp = client.get(f"/accounts/{reset_url}")
    assert token_resp.status_code == 302
    form_url = token_resp.url
    page = client.get(form_url)
    assert page.status_code == 200
    assert "Choose a new password" in page.content.decode()
    assert "signs out all other devices" in page.content.decode()
    # Setting the new password works and the user can log in with it.
    posted = client.post(
        form_url,
        {"password1": "brand-new-password-77", "password2": "brand-new-password-77"},
        follow=True,
    )
    assert posted.status_code == 200
    login(client, "rob@example.com", "brand-new-password-77")


@pytest.mark.django_db
def test_password_reset_invalid_key(client: Client) -> None:
    response = client.get(
        reverse("account_reset_password_from_key", kwargs={"uidb36": "ab", "key": "bad-key"})
    )
    assert response.status_code == 200
    assert "expired" in response.content.decode()


# ---------------------------------------------------------------- frame 6: MFA authenticate


@pytest.mark.django_db
def test_social_cancelled_and_error_pages_on_brand(client: Client) -> None:
    """Google-flow error surfaces share the auth theme (user-requested, 2026-09-29)."""
    for url_name, marker, status in [
        ("socialaccount_login_cancelled", "Login cancelled", 200),
        ("socialaccount_login_error", "Sign-in failed", 401),  # allauth signals auth failure
    ]:
        response = client.get(reverse(url_name))
        assert response.status_code == status
        content = response.content.decode()
        assert marker in content
        assert "Dealwright" in content  # themed brand header, not allauth default
        assert reverse("account_login") in content


@pytest.mark.django_db
def test_mfa_authenticate_flow(client: Client) -> None:
    user = create_user()
    secret = totp_auth.generate_totp_secret()
    Authenticator.objects.create(user=user, type=Authenticator.Type.TOTP, data={"secret": secret})

    response = client.post(
        reverse("account_login"), {"login": "rob@example.com", "password": PASSWORD}
    )
    assert response.status_code == 302
    assert reverse("mfa_authenticate") in response.url

    page = client.get(reverse("mfa_authenticate"))
    assert page.status_code == 200
    content = page.content.decode()
    assert "Two-factor check" in content
    assert "recovery codes" in content  # escape hatch copy

    # Wrong code bounces back with an error.
    bad = client.post(reverse("mfa_authenticate"), {"code": "000000"})
    assert bad.status_code == 200
    assert "errorlist" in bad.content.decode()

    # Valid code completes the login.
    good = client.post(reverse("mfa_authenticate"), {"code": totp_code(secret)})
    assert good.status_code == 302
    home_html = client.get(reverse("home")).content.decode()
    assert home_html.count(">Log out</button>") == 2  # drawer (mobile) + avatar menu (desktop)


# ------------------------------------------------------------------ frame 7: MFA setup + codes


@pytest.mark.django_db
def test_mfa_setup_renders_qr_after_reauth(client: Client) -> None:
    create_user()
    login(client, "rob@example.com", PASSWORD)
    response = client.get(reverse("mfa_activate_totp"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Protect your deals" in content
    assert "data:image/svg+xml;base64," in content  # QR code
    assert "Confirm" in content


@pytest.mark.django_db
def test_mfa_activate_shows_recovery_codes_once(client: Client) -> None:
    """Frame 7 end-to-end: activate TOTP → recovery codes shown exactly once."""
    from allauth.mfa.models import Authenticator

    user = create_user()
    login(client, "rob@example.com", PASSWORD)

    # Setup page renders the QR and exposes the secret (also stored in session).
    page = client.get(reverse("mfa_activate_totp"))
    match = re.search(r"text-dw-800\">\s*([A-Z2-7]+)\s*<", page.content.decode())
    assert match, "authenticator secret should be displayed for manual entry"
    secret = match.group(1)

    # Confirm with a valid code → redirected to the recovery codes view.
    response = client.post(reverse("mfa_activate_totp"), {"code": totp_code(secret)})
    assert response.status_code == 302
    assert response.url == reverse("mfa_view_recovery_codes")

    authenticator = Authenticator.objects.get(user=user, type=Authenticator.Type.RECOVERY_CODES)
    unused = authenticator.wrap().get_unused_codes()
    assert unused

    first = client.get(reverse("mfa_view_recovery_codes"))
    assert first.status_code == 200
    assert "Shown once" in first.content.decode()
    assert unused[0] in first.content.decode()

    second = client.get(reverse("mfa_view_recovery_codes"))
    assert second.status_code == 200
    content = second.content.decode()
    assert unused[0] not in content  # masked after first view
    assert "can't be displayed again" in content


@pytest.mark.django_db
def test_mfa_index_renders_states(client: Client) -> None:
    user = create_user()
    login(client, "rob@example.com", PASSWORD)
    content = client.get(reverse("mfa_index")).content.decode()
    assert "Two-factor settings" in content
    assert "Set up authenticator app" in content

    from allauth.mfa.totp.internal.auth import TOTP

    TOTP.activate(user, totp_auth.generate_totp_secret())
    content = client.get(reverse("mfa_index")).content.decode()
    assert "Authenticator app is active" in content


# --- password change (settings → security; themed in pass 17) -----------------


@pytest.mark.django_db
def test_password_change_page_renders_on_brand(client: Client) -> None:
    """Reached from Settings → Security — themed, not allauth's bare default."""
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.get(reverse("account_change_password"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Change password" in content
    assert "Current Password" in content
    assert "Dealwright" in content  # themed brand header, not allauth default
    assert 'name="oldpassword"' in content


@pytest.mark.django_db
def test_password_change_flow_round_trip(client: Client) -> None:
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.post(
        reverse("account_change_password"),
        {
            "oldpassword": PASSWORD,
            "password1": "fresh-harbor-mint-77",
            "password2": "fresh-harbor-mint-77",
        },
    )

    assert response.status_code == 302
    user = User.objects.get(email="rob@example.com")
    assert user.check_password("fresh-harbor-mint-77")


@pytest.mark.django_db
def test_password_change_rejects_wrong_current_password(client: Client) -> None:
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.post(
        reverse("account_change_password"),
        {
            "oldpassword": "wrong-pass-1",
            "password1": "fresh-harbor-mint-77",
            "password2": "fresh-harbor-mint-77",
        },
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Current Password" in content  # re-rendered with inline error
    user = User.objects.get(email="rob@example.com")
    assert user.check_password(PASSWORD)  # nothing changed


@pytest.mark.django_db
def test_password_change_requires_login(client: Client) -> None:
    response = client.get(reverse("account_change_password"))

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


# --- reauthenticate (identity gate before 2FA setup; themed pass 18) ----------


@pytest.mark.django_db
def test_reauthenticate_page_renders_on_brand(client: Client) -> None:
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.get(
        reverse("account_reauthenticate"), {"next": reverse("mfa_activate_totp")}
    )

    assert response.status_code == 200
    content = response.content.decode()
    assert "Confirm it's you" in content
    assert "Dealwright" in content  # themed brand header, not allauth default
    assert 'name="password"' in content
    assert reverse("mfa_activate_totp") in content  # next carried through


@pytest.mark.django_db
def test_reauthenticate_round_trip(client: Client) -> None:
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.post(
        reverse("account_reauthenticate"),
        {"password": PASSWORD, "next": reverse("mfa_activate_totp")},
    )

    assert response.status_code == 302
    assert response.url == reverse("mfa_activate_totp")


@pytest.mark.django_db
def test_reauthenticate_rejects_wrong_password(client: Client) -> None:
    create_user()
    client.force_login(User.objects.get(email="rob@example.com"))

    response = client.post(
        reverse("account_reauthenticate"),
        {"password": "wrong-pass-1", "next": reverse("mfa_activate_totp")},
    )

    assert response.status_code == 200
    assert "Dealwright" in response.content.decode()  # error stays on brand


# --- set password (Google-only accounts; themed pass 19) ----------------------


@pytest.mark.django_db
def test_password_set_page_themed_for_google_users(client: Client) -> None:
    """Passwordless (Google) users land here from Settings -> Security — on brand."""
    user = create_user()
    user.set_unusable_password()
    user.save()
    client.force_login(user)

    response = client.get(reverse("account_set_password"))

    assert response.status_code == 200
    content = response.content.decode()
    assert "Set a password" in content
    assert "Dealwright" in content  # themed, not allauth default
    assert 'name="password1"' in content


@pytest.mark.django_db
def test_password_set_round_trip(client: Client) -> None:
    user = create_user()
    user.set_unusable_password()
    user.save()
    client.force_login(user)

    response = client.post(
        reverse("account_set_password"),
        {"password1": "fresh-harbor-mint-77", "password2": "fresh-harbor-mint-77"},
    )

    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("fresh-harbor-mint-77")
