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

---

## Verdict — pass 16 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all gates matching recorded evidence (195 passed / 92 warnings, ruff clean, `makemigrations --check` clean, `git diff --check` clean) plus the clean-HEAD worktree gate (195 passed at the commit excluding Robb's hand edits; every utility class the committed template uses exists in committed `app.css`). Checklist verified hands-on via test client: all three links reverse to real allauth views; anonymous access redirects to login; chip states flip exactly per locked semantics (green `bg-dw-700` only with a TOTP authenticator; a recovery-codes-only user correctly stays "Not set up"); selector is a single tenancy-safe `.exists()` on the right model/type; profile-form path unchanged (test delta = exactly the two new tests).

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. team/selectors.py: function-local import of allauth.mfa.models.Authenticator inside is_mfa_enabled — unidiomatic vs the file's module-level imports; no circular-import need. Disposition: cosmetic, fold into a later card if touched again.
2. team/tests/test_views.py: MFA-on test fabricates the TOTP secret directly via ORM — card explicitly scopes this to an existence check (allauth's flows own crypto). Disposition: accepted as scoped.
Rationale: All four gates re-run and match builder evidence (195 passed / 92 warnings, ruff clean, no migrations, diff --check clean), and the clean-HEAD worktree gate proves no committed test depends on the uncommitted hand edits (195 passed at f3265e2; all template utility classes present in committed app.css). Checklist verified hands-on via the test client: all three links reverse and resolve to real allauth views, anonymous access redirects to login, the chip states flip exactly per the locked chip semantics (green bg-dw-700 only when a TOTP authenticator exists; neutral border chip when off; tokens-only), the selector is a single tenancy-safe .exists() on the correct model/type (recovery-codes-only correctly does not flip it), and the profile-form path is unchanged with the baseline→HEAD test delta exactly the two new tests.
```

**Disposition of minors:**
1. Function-local import → **applied directly** (module-level in `team/selectors.py`; gates rerun green) — no need to wait for a later card.
2. ORM-fabricated TOTP secret → accepted as scoped: the test asserts existence/state, not crypto; allauth's flows own that.

**Pass closed.** Scope commits `2d59841` (+ minor follow-up) stand as reviewed.
