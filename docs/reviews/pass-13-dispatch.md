# Dispatch — pass 13: provider delivery terms (pre-Card 5, design-log 2026-09-29) (2026-10-01)

**Scope:** commits `2a28857` → `4be5ca1` on baseline `18295b4` (two commits: docs-only settings-surface record `2a28857`; feature `4be5ca1` — see `git log 18295b4..HEAD`). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits in the working tree — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css` (owner-confirmed; the committed suite must not depend on them — gate 2 proves it).

## What changed

**`2a28857` — docs:** backlog "Settings surface" section recording the Robb-directed chat decision (account-level default currency declined for MVP; settings scope folds into Cards 9/10 + the pre-Card-5 item).

**`4be5ca1` — feature (the reviewed scope):**
- **`EngagementTermsMixin`** (abstract, team/models.py): rate_basis, rate_per_hour, project_rate, currency, availability_hours_per_week, timezone, languages — verbatim from the old VAProfile fields — plus the project-basis `clean()` rule and the `engagement_incomplete` property, both moved up from VAProfile. `languages` gained `default=""` (migration no-op on VA; smooth AddField default on provider). Abstract `Meta` carries no constraints — each concrete model declares its own table-scoped names.
- **`ProviderProfile(EngagementTermsMixin)`**: gains the seven columns with VA-consistent defaults (hourly / 0 / NULL / PHP / 40 / Asia/Manila / "") + three mirrored non-negative CheckConstraints (`dw_provider_*`). `industry_experience`/`notes` stay VA-only (provider positioning = `persona`), per design-log line 95.
- **`VAProfile(EngagementTermsMixin)`**: fields/clean/property now inherited; schema unchanged except the no-op `languages` default declaration. VA Meta constraints keep their `dw_va_*` names.
- **Migration `team.0008`**: AddField ×7 on providerprofile + AlterField (languages default) on vaprofile + CreateConstraint ×3. Nothing deployed yet (pre-first-deploy; append-only rule from here).
- **Settings page**: `ProviderProfileForm` (delivery_mode, branding_name, persona + the seven terms; currency widget limited PHP/USD like the VA form), `provider_settings` view (GET form / POST → `update_provider_profile`, invalid POST re-renders 200 with errors and writes nothing), service `update_provider_profile` (setattr loop → `full_clean()` → save; single write, no atomic, mirrors `update_va_profile`). Route `path("settings/", …)` registered **before** `<slug:member>/` (literal-beats-slug, house rule).
- **Template** `templates/team/provider_settings.html`: one card, one form, shared `_form_fields.html` include, `dw-*` tokens only. **app-base.html**: the disabled "Settings" sidebar placeholder is now a real link with active state (this file was clean before this card; not one of Robb's dirty three).
- **Tests**: model (defaults, `engagement_incomplete` matrix, project-basis clean, DB-level negative rejection via CheckConstraint), service (updates persist; invalid state writes nothing), views (login required, GET shows stored branding name, POST saves, invalid POST writes nothing, literal `/team/settings/` beats member slug). VA behavior regression-covered by the untouched existing suite (project-basis, engagement POST, roster "Rates not set" path).

## Locked decisions to preserve

1. **No-FX (Q3):** currency is a per-row declaration, never converted; no cross-currency sums introduced. Account-level default currency was explicitly declined (backlog, 2026-10-01).
2. **Provider positioning = persona;** no industry_experience/notes on ProviderProfile — guardrail symmetry "one model powers both About-me and matching, no duplicate systems."
3. Card 5 contract: `engagement_incomplete` shared by both holders — solo self-qualification and team filtering read the same rule.
4. Money/claims discipline untouched — no pricing, matching, or chip-semantics change in this scope.
5. Styleguide: thin view, form validates only, write via service with full_clean, type hints, tokens-only UI, POST mutations with CSRF.

## Review checklist

1. **Mixin refactor correctness:** VAProfile behavior identical (fields, help texts, clean rule, property, constraints); ProviderProfile gains exactly the seven columns + constraints; no field drift between the two tables (names/types/defaults).
2. **Migration 0008:** reversible, state-consistent with models; `makemigrations --check` clean; new constraints actually enforced at DB level (negative INSERT fails).
3. **Route shadowing:** `/team/settings/` resolves to provider_settings, not member_detail; resolve() check.
4. **Tenancy:** profile is OneToOne on user — GET/POST can only touch the requester's row; no cross-owner surface introduced.
5. **Invalid-write guarantee:** project-basis POST without project_rate → 200 re-render, zero DB writes (service full_clean path, not just form validation).
6. **Committed-template independence:** clean-HEAD worktree run green — no committed test depends on Robb's uncommitted member_detail/dashboard edits.
7. **Styleguide + locked decisions 1–5.**
8. **Gates:** rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **183 passed** (86 pre-existing warnings).
2. **Clean-HEAD worktree** at `4be5ca1`: `pytest -q` → **183 passed**; `ruff check .` → clean.
3. `.venv/bin/ruff check .` — clean. `manage.py check` — no issues. `manage.py makemigrations --check --dry-run` — no changes. `git diff --check` — clean.

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

## Verdict — pass 13 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all six gates in both the working tree and a verified-clean worktree at `4be5ca1` (183 passed / 86 warnings each, matching recorded evidence), and re-verified every checklist item against the actual diff and live behavior: the seven shared fields programmatically identical across both tables (types, defaults, help texts) with table-scoped constraint names; migration 0008 reversed and re-applied on a scratch DB with its CHECK constraints provably rejecting negatives via `objects.create()`; `/team/settings/` resolves to `provider_settings`; tenancy structural (OneToOne + instance-bound form, no owner/pk fields); the invalid-write path reproduced live (only form error is the mixin `clean()` rule, committed tests at view and service layers); the committed suite renders the new page without Robb's uncommitted files (all referenced classes present in committed `app.css`).

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. No Postgres-parity test run this pass (no local daemon); CHECK-constraint SQL is backend-agnostic and the gate list doesn't require it — for the record.
2. engagement_incomplete compares rate_basis to the string "project" while clean() uses RateBasis.PROJECT — verbatim pre-existing pattern moved into the mixin, cosmetic only.
3. GET /team/settings/ silently creates the provider profile on first visit via get_provider_profile — pre-existing service semantics reused, observable but acceptable.
Rationale: All six gates rerun green in both the working tree and a verified-clean worktree at 4be5ca1 (183 passed / 86 warnings in each), matching the card's recorded evidence exactly. Every checklist item was re-verified against the actual diff and live behavior, not summaries: the seven shared fields are programmatically identical across both tables with table-scoped constraint names and an abstract constraint-free mixin; migration 0008 was reversed and re-applied on a scratch DB and its CHECK constraints provably reject negatives at DB level via objects.create(); /team/settings/ resolves to provider_settings; tenancy is structural (OneToOne + instance-bound form with no owner/pk fields); the invalid-write path was reproduced live (the only form error is the mixin clean() rule, with committed tests at both view and service layers); and the committed suite renders the new page without Robb's uncommitted files, with all referenced CSS classes present in the committed app.css. Locked decisions 1-5 (no-FX, persona positioning, shared engagement_incomplete, money/claims discipline, styleguide) are all preserved.
```

**Disposition of minors:**
1. Postgres-parity → already a standing backlog item ("Postgres-backed pytest verification pending", Card 0 residuals — no local Docker daemon); no new entry needed. For the record here.
2. String literal in `engagement_incomplete` → accepted as-is: verbatim preservation of the reviewed-out VAProfile code; changing it post-verdict would churn the reviewed diff for zero behavior change.
3. Profile creation on first GET → accepted: documented `get_provider_profile` semantics ("created solo-by-default on first need"), identical to the team-home surface; no action.

**Pass closed.** Scope commits `2a28857`, `4be5ca1` stand as reviewed.
