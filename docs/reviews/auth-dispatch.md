# Review dispatch — between-card addition: auth mockup implementation (Q13)

**For:** fresh GLM-5.3 reviewer (read-only — run gates, edit nothing). Seed a fresh session with this file + repo root `/home/robbb/dealwright`.
**Builder:** builder session 2026-09-29 (pi coding session, Robb-directed: "implement all this mockup" → `docs/mockups/auth-mockup.html`). **Scope:** commits `9b89a06` (feat: allauth MFA + Google wiring + signup form), `d2c2e9b` (feat: auth mockup screens + CSS), `3e37fee` (test: smoke tests), plus the docs commit carrying this dispatch card and the backlog residuals (review `git show HEAD -- docs/backlog.md docs/reviews/auth-dispatch.md`).

## Scope summary

`docs/mockups/auth-mockup.html` (7 frames) translated into the Django app:

- **Frame 1 login** → `templates/account/login.html` (email-first, remember me, Google below the divider, forgot-password link)
- **Frame 2 signup** → `templates/account/signup.html` + custom `core.forms.SignupForm` via `ACCOUNT_FORMS` (full name → first/last name, required terms checkbox, ≥10-char password hint matching `MinimumLengthValidator min_length=10`)
- **Frame 3 verify email** → `account/verification_sent.html`, `account/verified_email_required.html`, `account/email_confirm.html` + POST-only resend endpoint (`core.services.resend_confirmation_email`, capped 5/h/address via Django cache, anti-enumeration copy)
- **Frame 4 password reset** → `account/password_reset.html` + `password_reset_done.html` (anti-enumeration banner); `PASSWORD_RESET_TIMEOUT = 24h`
- **Frame 5 set new password** → `account/password_reset_from_key.html` (+ `_done`); single-use link warning copy
- **Frame 6 MFA authenticate** → `templates/mfa/authenticate.html`; 6-box OTP as vanilla-JS progressive enhancement over allauth's `code` field (no-JS fallback intact); recovery-code escape-hatch copy
- **Frame 7 MFA setup + recovery codes** → `mfa/totp/activate_form.html` (QR via `qrcode`, secret code-box, confirm), `mfa/recovery_codes/index.html` (shown once — server-side via `MFA_RECOVERY_CODES_SHOW_ONCE=True`), plus small `mfa/index.html`, `mfa/recovery_codes/generate.html`, `mfa/totp/deactivate_form.html`
- Shared `templates/auth-base.html` (gradient brand header, no site nav); `dw-*` component classes in `static/css/src/input.css` (`@layer components`); teal + amber-line tokens added to `@theme`; `static/css/app.css` rebuilt from sources
- Settings: `allauth.mfa` installed; `allauth.socialaccount.providers.google` conditionally installed with the credentials env keys (fixes Card 0 gap — provider was never registered before); `django-allauth[mfa,socialaccount]` in pyproject (`qrcode` dep)
- Smoke tests: `core/tests/test_auth.py` (18, templates/UI tier)

## Spec baseline

- `docs/mockups/auth-mockup.html` — content/structure source of truth for the screens
- `docs/mockups/theme.html` + `AGENTS.md` design-system section — canonical tokens; chip semantics (green = verified/accepted, amber = estimate/warning, gold = premium only, red = gaps/errors, teal = info)
- `docs/design/design-log.md` Q13 (auth: allauth, Google, TOTP MFA + one-time recovery codes, anti-enumeration reset copy, 24h single-use link, other sessions invalidated) and Q12 (theme)
- `docs/styleguide.md` — thin views, forms validate input only, Tailwind v4 utilities + `@layer components`, smoke-tier UI tests, type hints everywhere
- `AGENTS.md` rules of engagement (secrets in env, estimates discipline)

## Gates (run all; paste real output into findings)

1. `.venv/bin/python -m pytest` — expect **22 passed** (4 pre-existing + 18 new in `core/tests/test_auth.py`)
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — no issues
4. `bash scripts/build_css.sh` then `git diff --stat static/css/app.css` — rebuild reproducible (no diff)
5. `manage.py makemigrations --check --dry-run` — no missing migrations (mfa app adds migrations of its own, already applied to dev db; none are project-authored)
6. Live smoke: `runserver` (dev settings) → anonymous: `/accounts/login/` 200 with "Welcome back"/"Remember me"/"Forgot password?" and **no** Google button (no credentials); `/accounts/signup/` 200 with "Full name" + "14-day Professional trial"; `/accounts/password/reset/` 200; `/accounts/2fa/` 302 (login required); `/static/css/app.css` 200
7. Template hygiene: no hardcoded hex colors in `templates/` (tokens/`dw-*` classes only); no business logic in templates; `core/views.py` stays thin
8. Security spot-checks: resend endpoint is POST-only; anti-enumeration copy on reset-done + resend; `GOOGLE_OAUTH_*` values only from env (grep for hardcoded secrets); no real secret values committed
9. Auth-flow spot-checks via test client (or extend tests temporarily in a scratch checkout only): MFA-enabled user logging in lands on `/accounts/2fa/authenticate/`; recovery codes viewable exactly once

## Checklist (adjudicate each)

- [ ] Each mockup frame faithfully mapped to its allauth template (frame notes name them); brand header, tagline, and body copy match
- [ ] Chip semantics respected: green banner = success/verified, amber banner = warnings (single-use link), teal banner = info (setup steps); no gold misuse; no red outside errors
- [ ] Q13 requirements: Google below email divider; anti-enumeration reset copy; 24h expiry; recovery codes shown once; MFA optional now (Agency-tier enforcement is a later card, recorded deferred)
- [ ] `ACCOUNT_FORMS` signup: full name stored on user (first/last split), terms required with friendly error
- [ ] Tests: smoke tier through public APIs, no implementation-coupled assertions, fast/order-independent
- [ ] `@source` coverage: new template classes present in committed `app.css` (rebuild gate 4 proves it)
- [ ] Backlog residuals recorded ("Auth implementation residuals (2026-09-29…)")

## Known deviations to adjudicate (each intentional; backlog has the section)

1. **Between-card work** — built at Robb's direct request between Card 0 review and Card 1; smoke-tier tests; this dispatch substitutes for a per-card review.
2. **Frame 3 "Wrong address? [input]" omitted for signed-out users** — pre-verification email change is an account-takeover vector; wrong-address routes back to signup (logged-in users get the styled email-manage page). Security-first deviation.
3. **Frame 6 OTP boxes via JS progressive enhancement** over allauth's single `code` field (no-JS fallback = single input). MVP has no build pipeline; the alternative was dropping the 6-box look entirely.
4. **Resend confirmation endpoint added** (in the mockup as a button; allauth has no equivalent view) — POST-only, rate-limited 5/h/address via Django cache, anti-enumeration.
5. **Verification-mode tension left untouched**: production keeps `ACCOUNT_EMAIL_VERIFICATION=mandatory` (Card 0 line) while the mockup note implies `optional` + gate-at-send (Card 8 `@verified_email_required`). Flagged in backlog for a between-card decision — deliberate non-change to avoid relitigating a locked setting mid-card.
6. **Non-branded allauth default pages remain** for edge surfaces (reauthenticate, trust, social errors, signup-closed, email-confirm-code) — self-contained, deferred in backlog.
7. **`fido2` arrives transitively** with `allauth[mfa]` extra (unused — WebAuthn not in `MFA_SUPPORTED_TYPES` default). Acceptable, or prefer pinning `qrcode` directly?

## Verdict format

```
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings: <list or none>
Minor findings: <list or none>
Rationale: <one line>
```

Record the verdict below under **Verdict (reviewer)** and mirror the disposition in `docs/backlog.md` ("Auth implementation residuals"). Blocking findings → builder fixes → fresh reviewer pass.

---

## Verdict (reviewer)

*(pending — fresh GLM-5.3 reviewer pass)*
