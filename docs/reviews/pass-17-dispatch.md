# Dispatch — pass 17: themed password change page (2026-10-01)

**Scope:** single commit `3ae2013` on baseline `5401ac3` (pass 16, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed (Robb-reported: `/accounts/password/change/` renders off-brand)

- **New `templates/account/password_change.html`** — allauth's `PasswordChangeView` template name had no project override, so the page (now linked from Settings → Security since pass 16) fell back to allauth's bare default. New template extends `auth-base.html` per the `email.html` precedent: `dw-h1`/`dw-sub`, explicit `dw-field` blocks for `oldpassword` / `password1` / `password2` (labels from the form), `btn-primary` submit, `dw-swap` back-to-workspace link. Success flash renders via auth-base's existing messages block (allauth redirects back to the same page on success).
- **No view/form/URL changes** — allauth owns the flow; this is presentation-only. `account/password_set.html` (Google-only users without a password) deliberately stays default per the recorded backlog decision (dormant path, "style if pilots hit them").
- **Tests (core/tests/test_auth.py, smoke tier):** themed render (200, "Change password" + "Current Password" + "Dealwright" header marker, `oldpassword` input); full round-trip (correct old password → 302, `check_password` confirms the new one); wrong current password → 200 re-render, password unchanged; anonymous → login redirect.

## Review checklist

1. Render the page logged-in (test client or throwaway server): themed card, three fields with labels, submits to `account_change_password`; success shows the flash and lands back on the page; wrong current password re-renders inline.
2. Template tokens-only (no hardcoded hexes), consistent with `email.html`/`password_reset.html` structure; `{% csrf_token %}` + redirect field present.
3. Flow safety unchanged: allauth view untouched; no tenancy surface; `@login_required` behavior covered by test.
4. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **199 passed** (96 pre-existing warnings).
2. `.venv/bin/ruff check .` — clean; `git diff --check` — clean; clean-HEAD worktree at `3ae2013`: **199 passed**, ruff clean.

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

## Verdict — pass 17 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all gates matching recorded evidence (199 passed / 96 warnings, ruff clean, `git diff --check` clean; clean-HEAD worktree at `3ae2013` — no committed test depends on Robb's uncommitted edits) and adjudicated the checklist by **actually rendering the page**: themed auth-base card with allauth's own labels (Current / New / New again) and form contract (same action, csrf, redirect field); correct POST → 302 with `check_password` confirming the change and the success flash rendering via auth-base's messages block; wrong current password → 200 inline re-render with the password provably unchanged; anonymous → login redirect. Presentation-only diff; set-password deferral is the recorded backlog decision.

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. The committed success-path test asserts the 302 + password change but not the success flash text; reviewer probe confirmed the flash ("Password successfully changed.") renders via auth-base's messages block. Disposition: acceptable as-is — smoke tier; no action required.
Rationale: All four gates re-run and match builder evidence exactly, including a clean-HEAD worktree at 3ae2013 (199 passed / 96 warnings, ruff clean) proving no committed test depends on the uncommitted hand edits. Checklist item 1 verified by actually rendering the page logged-in via test client (GET, correct POST, wrong-password POST, anonymous): the themed override honors allauth's default template contract (same action, same three fields with allauth's labels, csrf + redirect field), the success flash lands back on the page, and wrong current password re-renders inline with the password provably unchanged. Template is tokens-only with all classes defined in committed CSS and mirrors the email.html/password_reset.html precedent. The diff is presentation-only — no view/form/URL/tenancy surface touched — and the password-set deferral is a recorded backlog decision.
```

**Disposition of minors:**
1. Success-flash assertion → accepted as-is: smoke tier covers the state change (302 + new password hashes); the reviewer's own probe confirmed the flash renders. No action.

**Pass closed.** Scope commit `3ae2013` stands as reviewed.
