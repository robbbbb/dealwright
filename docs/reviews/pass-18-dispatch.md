# Dispatch — pass 18: themed reauthenticate page (2026-10-01)

**Scope:** single commit `80a1398` on baseline `0991e47` (pass 17, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed (Robb-reported: `/accounts/reauthenticate/?next=/accounts/2fa/totp/activate/` renders off-brand)

- **New `templates/account/reauthenticate.html`** — allauth's `ReauthenticateView` ("confirm it's you" password gate before sensitive actions like TOTP activation) had no project override. New template extends `auth-base.html` (email.html precedent): `dw-h1`/`dw-sub`, single `password` `dw-field`, `btn-primary` "Confirm", back-to-workspace link, and the **redirect hidden field carried through** so `?next=…` survives the POST (NextRedirectMixin contract).
- **Decision record:** this page was on the recorded "intentionally default" edge-page list; Robb's direction supersedes it for this page (backlog updated at verdict recording). The **mfa-app variant** (`/accounts/2fa/reauthenticate/`, shown to TOTP-enabled users) stays default until hit — noted in the same backlog line.
- **No view/form/URL changes** — presentation only; allauth owns the flow.
- **Tests (smoke tier):** themed render with `next` carried into the form; correct password → 302 to the `next` URL; wrong password → 200 themed re-render.

## Review checklist

1. Render logged-in with `?next=`: themed card, password field, hidden `next` present; POST correct password → 302 to next; POST wrong password → 200 themed with inline error; allauth flow untouched.
2. Tokens-only, structure consistent with `email.html`/`password_change.html`; csrf + redirect field present.
3. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **202 passed** (99 pre-existing warnings).
2. `.venv/bin/ruff check .` — clean; `git diff --check` — clean; clean-HEAD worktree at `80a1398`: **202 passed**, ruff clean.

## Required verdict format

```text
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings:
1. ...
Minor findings:
1. ...
Rationale: ...
```

Do not edit files. A blocking finding requires a fix and a fresh reviewer pass. The builder must record the verdict and disposition here before this pass is closed.
