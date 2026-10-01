# Dispatch — pass 20: confirmation gates on destructive actions (2026-10-01)

**Scope:** commit `5781edd` on baseline `18295b4` (see `git show 5781edd`; note `main` has moved since pass 12 — passes 13–19 plus a manual `update daashboard` commit are already closed and NOT under review). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## What changed

- **One shared confirmation gate:** a delegated `submit` listener in `app-base.html`'s existing `<script>` block (capture phase, IIFE, vanilla JS — no new dependency, no inline handlers). Forms opt in via a `data-confirm="<message>"` attribute; unmarked forms are untouched.
- **Gated forms (9):**
  1. `app-base.html` — both nav logout forms (mobile drawer + desktop avatar menu): "Log out of Dealwright?"
  2. `base.html` — auth-flows nav logout form: same message
  3. `team/team.html` — "Remove" my skill (provider capabilities)
  4. `team/team.html` — registry-skill ✕ (unused rows only): names the skill
  5. `team/member_detail.html` — desktop skill Remove: names skill + member
  6. `team/member_detail.html` — mobile skill Remove: same message
  7. `catalog/service_form.html` — required-skill Remove: names the skill
  8. `catalog/service_form.html` — Danger zone "Remove service": names the service + "This cannot be undone."
- **Deliberately not gated:** allauth's `/accounts/logout/` page (already a POST-only confirmation page — GET renders "Are you sure?"); idempotent non-destructive actions (seed catalog, add category, etc.).
- **Tests:** new per-surface smoke assertions — logout confirm ×2 in nav (team home), my-skill remove confirm, registry-skill confirm names the skill (single-quoted attribute with straight inner quotes), member page has exactly 2 removal confirms, catalog edit page pins the exact service-delete and requirement-removal attribute strings.
- **Test touch-ups (mechanical):** two pre-existing tests (`core/tests/test_views.py::test_signed_in_users_get_dashboard`, `core/tests/test_auth.py::test_mfa_authenticate_flow`) counted the substring `"Log out" == 2` in rendered pages; the new dialog text contains that substring, so they now count rendered buttons (`">Log out</button>" == 2`) — same intent, immune to dialog wording.
- **Docs:** design-log entry (pattern + accepted residual); backlog line: confirmations are JS-only — with JS disabled, forms submit directly (noscript has no dialog layer).

## Locked decisions to preserve

1. No new dependencies, no inline JS handlers, server-rendered templates — the gate extends the existing vanilla menu script only.
2. Chip semantics, tokens, money/claims discipline untouched — this commit changes no view/model/service code (templates + tests + docs only).
3. POST-only mutations remain the rule; the confirm layer is additive UX, never a security control (CSRF/tenancy guards unchanged and still authoritative).
4. Allauth logout page stays POST-only confirmation; nav logout is POST with dialog.

## Review checklist

1. **Complete coverage:** confirm no *destructive* POST form is left un-gated across `templates/` (grep `method="post"` + delete/remove/logout actions). Non-destructive forms (add/update/seed/login) should remain un-gated — flag any over-gating as a minor.
2. **Handler correctness:** capture-phase listener; `getAttribute` (not dataset) guard; `preventDefault` only when the user declines; no behavior change for unmarked forms; script placement after DOM (end of body).
3. **Attribute/escaping safety:** single-quoted `data-confirm` attributes contain interpolated names (`{{ rs.name }}`, `{{ service.name }}`, `{{ cap.skill }}`, `{{ va.display_name }}`) — verify Django auto-escaping makes hostile names safe in the attribute, and that a name containing a single quote cannot break out (auto-escape turns `'` into `&#x27;`).
4. **No-JS degradation:** with JS off, forms submit directly — confirm this residual is documented (backlog) and that noscript still reaches all core actions.
5. **Test integrity:** the two touched pre-existing tests preserve their original intent (two logout buttons in the nav); new assertions pin exact attribute strings, not loose substrings.
6. **Gates:** rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **210 passed** (107 pre-existing warnings).
2. `.venv/bin/python -m ruff check .` — clean.
3. `git diff --check` — clean.
4. No migration, model, view, or service changes in scope (`git show --stat 5781edd`).

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

## Verdict — pass 20 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) re-ran all gates and adjudicated all checklist items, including an engine-level escaping proof with hostile names.

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. base.html gate is inert: no template extends/renders base.html and it has no script block, so its data-confirm can never fire; the dispatch card's "gated form #2 (auth-flows nav logout)" claim is functionally inaccurate. Suggest deleting the dead base.html or dropping the attribute, and correcting the wording in the pass-20 disposition.
2. socialaccount/connections.html "Remove selected" is an un-gated remove-type POST on auth-base, which has no confirm listener; reversible and multi-step, but it warrants a backlog line under the card's "every destructive or one-way form" standard.
Rationale: All gates re-run and green, matching builder evidence (210 passed/107 warnings; ruff clean; git diff --check clean; no app-code changes in scope). All 9 claimed gates verified present with no over-gating of non-destructive forms; handler verified capture-phase, getAttribute-guarded, preventDefault-on-decline, no bypass via inline handlers or programmatic submit; escaping proven safe by engine-level render (hostile names entity-encoded, no attribute break-out in any of the 4 shapes); the two touched tests preserve their original intent (two logout buttons); the no-JS residual is documented in backlog. The two minors are record-keeping/coverage-edge issues with no user-facing impact today and can ride with a recorded disposition.
```

**Disposition of minors:**
1. Card correction accepted: `base.html` is an unused scaffold layout — the "gated form #2" claim was functionally false; real nav coverage is `app-base.html` (both forms verified gated). Dead-file cleanup backlogged rather than churned mid-pass.
2. Social-app remove → backlogged (extend pattern to auth-base or accept at next auth card).

**Correction to this card:** "Gated forms (9)" should read "8 live gates" — items 1 and 2 collapse to app-base's two nav forms; `base.html`'s attribute is inert (see minor 1).

**Pass closed.** Commit `5781edd` stands as reviewed.
