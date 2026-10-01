# Dispatch — pass 11: category registry model + roster preview cap (2026-10-01)

**Scope:** commits `6db1b3c` + `a36caaf` on baseline `71d8eb3`. **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Note for reviewer:** three files (`templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`) carry pre-existing uncommitted edits from an earlier session. They are **out of scope** for this pass — do not review them and do not let them color verdicts on the committed work.

## What changed

**Commit 1 — `6db1b3c` (team, UI):**
- Team home roster grid is capped at the first **four** member cards (`vas|slice:":4"`); header counts still show the true total.
- When more than four members exist, a footer link **"See all N members →"** opens the new full-roster page `/team/members/` (`member_list` view reusing `selectors.list_vas` — owner-scoped).
- Member card markup extracted verbatim into `templates/team/_member_card.html`, included by both surfaces (no duplicated card logic).
- `path("members/", ...)` is registered **before** `path("<slug:member>/", ...)` so the slug route cannot swallow it.
- Six new smoke tests: cap at four, exactly-four shows no link, login required, full list renders every member, tenancy (other owner's member never listed).

**Commit 2 — `a36caaf` (catalog, schema):**
- New **`ServiceCategory`** registry model: owner FK (CASCADE), name unique per owner, slug unique per owner and frozen at creation — mirrors `team.Skill`.
- `Service.category` CharField → **FK `PROTECT`** to it. `Service.clean()` gains a tenancy guard (fires only when both `owner_id` and `category_id` are known — ModelForm `_post_clean` runs `full_clean` on an instance without owner; every real write path sets both).
- `ServiceForm` now takes `owner` (like `RequiredSkillForm`); `category` is a **ModelChoiceField** over the provider's own rows — cross-owner pks are invalid choices, never silent fallbacks.
- New `category_add` view + page at `/catalog/categories/add/` (GET form + POST), idempotent `get_or_create_category` (duplicate name → info flash, no error, no second row). "Add category" secondary button sits beside "Add service" on the catalog header. Route precedes `<slug:category>/…` patterns.
- Migration chain `0006–0009`, data-preserving: create model → nullable `category_fk` → **0008 backfill** (one category row per distinct owner+category string, slugs deduped per owner) → drop CharField, rename FK column to `category`, NOT NULL, rebuild `dw_service_unique_per_owner`. The constraint is dropped **before** the column swap because SQLite rebuilds the table per column operation (a constraint referencing a removed field breaks the rebuild — hit and fixed during development).
- Seed path creates category rows via the same `get_or_create_category`; re-seed remains edit-safe on natural key (owner, category name, service name).
- Service list groups by `category.name` with `select_related("category")` (no N+1); `_canonical_service` validates `slugify(service.category.name)`.
- Admin: `ServiceCategory` registered; Service search now `category__name`; `list_filter` unchanged (works on FK).
- Tests: catalog suite updated for the FK world (conftest resolves category names to rows; view POSTs use pks) + new coverage: category slug/unique/tenancy/PROTECT/owner-cascade semantics, `TestCategoryAdd` (login, create, duplicate idempotent, blank name, owner-scoped select, zero-categories hint), seed asserts via `category__name`.
- Docs: design-log supersession entry (2026-10-01) + two backlog residuals (category rename/delete UI stays admin-only; future account-deletion must handle PROTECTed rows).

## Locked decisions to preserve

1. **Money/claims discipline untouched:** no pricing, matching, or FX behavior changed; `price_summary`, `dw_symbol`, ranges-not-points all as before.
2. **Tenancy is enforced at every layer:** form queryset scoping (invalid choice, not fallback) + `Service.clean()` guard + URL canonical-category 404 — same as the `team.Skill` registry precedent.
3. **Slug discipline:** category slugs frozen at creation, unique per owner; canonical-category URL validation unchanged (mismatch = 404).
4. **Vocabulary pattern:** category creation is the one deliberate free-text surface for this vocabulary, idempotent get_or_create per owner+name — mirrors the team skill-list manager (design-log 2026-09-30).
5. **Chip semantics unchanged:** no new colors/fonts/tokens; both UI changes reuse existing `dw-*` tokens and markup patterns (secondary button style = existing "Add my own" outline style).
6. **PROTECT, not CASCADE, between Service and ServiceCategory** — grouping/matching inputs stay stable; owner deletion blocked while catalog rows exist (documented residual; allauth exposes no delete-account path in MVP).

## Review checklist

1. **Migration safety (highest priority):** replay `0006→0009` reasoning — nullable stage, backfill completeness (no string value dropped; every service repointed), NOT NULL only after backfill, constraint dropped before column swap and re-added after. Verify no data loss on a DB with existing rows.
2. **Tenancy probes:** cross-owner category pk via POSTed form data is rejected as invalid choice; direct ORM assignment with mismatched owner fails `full_clean()`; other owner's members/categories never appear on any GET surface (list, create form select, roster page).
3. **Route shadowing:** `/catalog/categories/add/` and `/team/members/` are matched before their respective `<slug:…>` routes; try both URL orders mentally and confirm no route swallows them.
4. **Behavior preservation:** seed still loads 25 services exactly once (categories included), edit-safe re-seed, service CRUD + required skills flows unchanged, roster card markup identical to the pre-refactor card (verbatim extraction).
5. **Styleguide:** business logic in services (get_or_create_category), reads in selectors, thin views, forms validate only, no signals, type hints present.
6. **Docs:** design-log entry accurately describes the supersession; backlog residuals are recorded (not chat-only).
7. **Gates:** rerun them yourself and compare against recorded evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **167 passed** (81 warnings: pre-existing staticfiles/UserWarning noise).
2. `.venv/bin/python -m ruff check .` — clean.
3. `.venv/bin/python manage.py check` — no issues.
4. `.venv/bin/python manage.py makemigrations --check --dry-run` — no changes detected (model state matches migrations).
5. `git diff --check` — clean.
6. Backfill exercised on scratch DB with 4 services across 2 owners: deduped to 3 category rows (per-owner grouping correct), all services repointed, cross-owner name reuse produces distinct rows.
7. Dev DB migrated and end-to-end smoke: POST category → created with slug `client-reporting`; duplicate POST idempotent (1 row); service created via select; list page groups under the new category; roster page caps at 4 with working see-all link.

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
