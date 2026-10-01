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

---

## Verdict — pass 18 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all gates matching recorded evidence (202 passed / 99 warnings, ruff clean, `git diff --check` clean; clean-HEAD worktree at `80a1398` — no committed test depends on Robb's uncommitted edits) and adjudicated the checklist by **live render**: themed GET with the hidden `next` field present verbatim; correct-password POST → 302 to `/accounts/2fa/totp/activate/`; wrong-password POST → themed 200 re-render with inline error and `next` preserved; URL resolves to allauth's own `ReauthenticateView` (override path correct); template matches the `email.html`/`password_change.html` structure token-for-token with all classes present in HEAD CSS.

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. Backlog line docs/backlog.md:41 still lists "reauthenticate (account + MFA)" on the intentionally-default list; per the card, the account variant is now themed and only the MFA-app variant (/accounts/2fa/reauthenticate/) remains default — that line must be updated when this verdict is recorded, as the card already commits.
2. The h1/dw-sub copy is hardcoded English while the submit button uses {% trans %} — consistent with email.html/password_change.html precedent, so no change requested; noting for any future i18n pass.
Rationale: All three gates re-run and pass exactly as recorded (202 passed / 99 warnings in the working tree and in a clean-HEAD worktree at 80a1398 — proving no committed test depends on Robb's uncommitted edits; ruff and diff-check clean). Live test-client render confirms every checklist item: themed GET with the hidden next field present verbatim, correct-password POST → 302 to /accounts/2fa/totp/activate/, wrong-password POST → themed 200 re-render with inline error and next preserved. The diff is presentation-only (template + smoke tests), matches the email.html/password_change.html structure token-for-token with all classes present in HEAD CSS, and leaves allauth's flow untouched.
```

**Disposition of minors:**
1. Backlog line → **updated now** (this recording): account reauthenticate themed (pass 18); only the MFA-app variant remains on the default list.
2. i18n copy note → accepted: matches the established auth-page precedent; whole-surface i18n is already a post-MVP backlog line ("i18n: EN-only for MVP").

**Pass closed.** Scope commit `80a1398` stands as reviewed.
