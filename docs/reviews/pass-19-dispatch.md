# Dispatch — pass 19: settings security adapts to Google-auth accounts; themed set-password (2026-10-01)

**Scope:** single commit `22aa898` on baseline `2da4da3` (pass 18, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed (Robb-reported: he signs in with Google → no password, yet surfaces asked for one)

Probed as a passwordless user before fixing: Settings showed "Change" → redirect to `/accounts/password/set/` (allauth bare default); `reauthenticate` raises bare 403 for passwordless users (no reauth methods exist — direct-URL edge only, recorded in backlog).

1. **Settings Security password row branches on `user.has_usable_password`** (template-side, zero-arg callable): password-ful → "Change" → `account_change_password` (unchanged); passwordless (Google) → "Set password" → `account_set_password` with copy "You sign in with Google — add a password to also sign in with email."
2. **New `templates/account/password_set.html`** — the set-password page allauth redirects Google users to, previously allauth's bare default. Themed per the `password_change.html` precedent (auth-base, `password1`/`password2` fields, Google-specific sub copy). **Un-deferred from the recorded default list**: the "dormant Google path" premise is dead — Google auth is live on localhost; backlog updated (password_set moved to themed; reauthenticate-403 edge noted).
3. **No view/form/URL changes** — allauth owns all flows (`ChangePasswordView` itself redirects passwordless users to set-password; `SetPasswordView` redirects password-ful users back to change). Presentation only.
4. **Tests:** password_set page themed for a passwordless user + round-trip (302, `check_password` confirms); settings password row flips Change/Set based on `has_usable_password` (re-login after ORM hash change — real Google sessions don't mutate underneath).

## Review checklist

1. Render settings as a passwordless user: row shows "Set password" → themed set page (200, Dealwright marker, `password1` field); as a password-ful user: row shows "Change" → themed change page (pass 17). No cross-path: password-ful users can't reach set (allauth redirects) and vice versa.
2. Set-password round-trip: POST password1/password2 → 302, password hashes, session intact.
3. Tokens-only, structure matches `password_change.html`; csrf + redirect field present; no view/flow changes.
4. Backlog accuracy: default-list line updated (password_set themed, reauthenticate-403 edge recorded).
5. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **205 passed** (102 pre-existing warnings).
2. `.venv/bin/ruff check .` — clean; `git diff --check` — clean.

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

## Verdict — pass 19 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all gates matching recorded evidence (205 passed / 102 warnings on the working tree AND a clean-HEAD worktree at `22aa898` — no committed test depends on Robb's uncommitted edits; ruff clean; `git diff --check` clean) and adjudicated every checklist item by live test-client rendering: settings row branches on `has_usable_password` in both directions; set-password page themed with `password1`/`password2` and no `oldpassword`; allauth cross-path redirects confirmed both ways (password-ful → set redirects to change, passwordless → change redirects to set); round-trip hashes the password with session intact; tokens-only markup; backlog updated accurately (password_set themed; reauthenticate-403 passwordless edge recorded).

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. test_password_set_round_trip doesn't assert the redirect target or post-POST session persistence (manually verified: 302 → /accounts/password/change/, session intact) — cosmetic test depth, no fix required.
2. Settings-row test asserts raw href byte-strings instead of reverse()-derived URLs — mildly brittle, acceptable.
Rationale: All gates re-run and pass (pytest 205/102 warnings on working tree AND on a clean-HEAD worktree of 22aa898 — no committed test depends on Robb's uncommitted edits; ruff and git diff --check clean). Every checklist item verified by live test-client rendering: settings row branches correctly on has_usable_password in both directions, set-password page is themed with password1/password2 and no oldpassword, allauth cross-path redirects confirmed both ways, round-trip hashes the password with the session intact. Diff is presentation-only (2 templates + 2 test files); no view/form/URL changes; tokens-only markup matching the password_change.html precedent; backlog updated accurately.
```

**Disposition of minors:** both accepted as-is — smoke-tier depth choices that assert exactly the user-facing behavior; no action.

**Pass closed.** Scope commit `22aa898` stands as reviewed.
