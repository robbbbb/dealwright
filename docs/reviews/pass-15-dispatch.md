# Dispatch — pass 15: min=0 money inputs + sidebar single-highlight fix (2026-10-01)

**Scope:** single commit `45f847b` on baseline `226560e` (pass 14, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed (both Robb-reported)

1. **"I can still input negative project_rate":** server-side was already safe (pass-14 validators → friendly field error, zero writes; DB CHECK backstop — both tested). What he saw was the **browser accepting the keystrokes**: the number inputs carried no `min` attribute. Fix: `min="0"` on `rate_per_hour`, `project_rate`, `availability_hours_per_week` widgets in **both** `ProviderProfileForm` (settings) and `EngagementForm` (member engagement). No model/migration change.
2. **Sidebar double-highlight:** `provider_settings` lives in the `team` namespace, and the "My skills & team" link activates on the whole namespace → on `/team/settings/` both it and "Settings" were active. Fix: skills-link condition excludes `url_name == 'provider_settings'`. Settings link's own condition (exact `url_name`) unchanged.
3. **Tests:** settings GET renders exactly 3 `min="0"` inputs; sidebar shows exactly one active item on `/team/settings/` and one on `/team/`.

## Review checklist

1. min="0" present on all three numeric inputs on **both** forms; no other widget drift; template rendering unaffected otherwise.
2. Sidebar: on settings page exactly the Settings link is active; on any other team page exactly the skills link; Dashboard/catalog conditions untouched; no page with zero or two active team-namespace items.
3. Confirm server-side negative rejection remains (pass-14 tests still green — no behavior regression hiding behind the HTML fix).
4. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **193 passed** (90 pre-existing warnings).
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

## Verdict — pass 15 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all gates in a clean detached worktree (193 passed / 90 warnings, ruff clean, `makemigrations --check` clean, `git diff --check` clean — exact match with recorded evidence; no committed test depends on Robb's uncommitted edits) and adjudicated the checklist on **rendered pages**: `min="0"` confirmed on all three numeric inputs in both forms (member detail renders the EngagementForm; its GET is 405 by design); sidebar shows exactly one active item on every GET-reachable page — Settings-only on `/team/settings/`, skills-link on `/team/`, `/team/members/`, member detail, `/team/add/` — with dashboard/catalog conditions untouched; all 15 negative-rejection tests still green.

```text
Verdict: APPROVED
Blocking findings:
1. None. All four gates pass in a clean-HEAD worktree (193 passed / 90 warnings, ruff clean, no migrations, diff --check clean), matching the card's evidence exactly; no committed test depends on Robb's uncommitted edits; both fixes verified on rendered pages.
Minor findings:
1. test_provider_settings_number_inputs_carry_min_zero pins a raw byte-count of min="0" — brittle if an unrelated min="0" input joins the settings page. Fail-loud; disposition: accept for MVP, no fix required.
2. The sidebar test counts active-class occurrences without asserting which anchor is active — weaker than the behavior it protects. Fail-loud; disposition: accept, optionally tighten in a later UI card.
Rationale: min="0" confirmed on rate_per_hour, project_rate (step preserved) and availability_hours_per_week in both ProviderProfileForm (/team/settings/) and EngagementForm (member detail; engagement POST route 405s on GET by design); sidebar shows exactly one active item on every GET-reachable page with Settings-only on /team/settings/ and skills-link elsewhere, dashboard/catalog conditions untouched; pass-14 negative-rejection tests (15 selected) all green; diff contains no widget or template drift beyond the two described fixes.
```

**Disposition of minors:** both accepted as-is per the reviewer's own suggestion — smoke-tier tests that fail loud (a false failure prompts a look, never a silent pass); tighten only in a future UI card if they ever bite.

**Pass closed.** Scope commit `45f847b` stands as reviewed.
