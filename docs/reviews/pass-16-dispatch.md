# Dispatch — pass 16: settings security section (2026-10-01)

**Scope:** single commit `2d59841` on baseline `085da16` (pass 15, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed

Settings page gains a **Security card** under the existing profile/delivery-terms card — wiring the already-built allauth surfaces (backlog "Settings surface → Security", pulled forward from Card 9 wiring; that backlog line will be updated at verdict recording):

- **Account email** shown read-only (`{{ user.email }}` — email is the login method per Q13 `ACCOUNT_LOGIN_METHODS`) + "Manage" link → `account_email`
- **Password** row + "Change" link → `account_change_password`
- **Two-factor authentication** row with live status chip: TOTP authenticator exists → green "MFA on" chip + "Manage" link; otherwise neutral "Not set up" chip + "Set up" link → `mfa_index`. Green = enabled fits the locked chip semantics (green = verified/accepted; the neutral border style matches `_level_chip.html` precedent)
- **`selectors.is_mfa_enabled(user)`** — the one new query, in selectors per styleguide (`allauth.mfa.models.Authenticator`, TOTP type only — WebAuthn is disabled project-wide)
- View passes `mfa_enabled` in context; template presentation-only; no form/write-path change; no migration

**Tests:** security card renders the account email + all three hrefs + "Not set up" when off; with a TOTP `Authenticator` row, shows "MFA on" and not "Not set up" (existence check on `data` contents — no crypto validation in scope; allauth's own flows own that).

## Review checklist

1. All three links resolve to real allauth views (reverse them); login still required; no tenancy surface (reads only `request.user`'s own data).
2. Chip semantics: green used only for the enabled state; neutral border chip for off; tokens-only classes; no hardcoded hexes.
3. `is_mfa_enabled` — correct model/type, no N+1 or hidden writes; selector placement per styleguide; view stays thin.
4. No behavior change to the profile form (pass-13/14/15 tests untouched and green).
5. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **195 passed** (92 pre-existing warnings).
2. `.venv/bin/ruff check .` — clean; `manage.py makemigrations --check --dry-run` — no changes; `git diff --check` — clean.

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
