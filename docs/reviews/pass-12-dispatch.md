# Dispatch — pass 12: category registry + roster cap + bundled team polish (2026-10-01)

**Scope:** commits `6db1b3c` → `592254f` on baseline `71d8eb3` (four commits: roster cap `6db1b3c`, category model `a36caaf`, review fixes `592254f`; see `git log 71d8eb3..HEAD`). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## Corrections to the pass-11 card (read first)

Pass 11 returned **CHANGES REQUIRED**. This card corrects two defects in that brief and records the fixes:

1. **Blocking (fixed in `592254f`):** `6db1b3c` shipped `test_member_detail_groups_profile_terms_and_capabilities`, which asserted headings ("Member profile", "Engagement terms", `member-profile-heading`, `capabilities-heading`) that exist **only in uncommitted working-tree edits** to `templates/team/member_detail.html`. HEAD was red on its own (clean-worktree run: 1 failed / 166 passed). Fix: the coupled test was **removed** from the committed suite with an explanatory NOTE in `team/tests/test_views.py` — it belongs to the still-uncommitted member-detail redesign and must be restored when that work lands as reviewed scope.
2. **Card accuracy:** pass 11's "What changed" under-described `6db1b3c`. **Disclosure:** the builder's working tree carried an uncommitted team-home UI polish from an earlier session; committing the roster change swept it in. `6db1b3c` therefore contains BOTH the roster cap AND that polish (described honestly below). The card's "verbatim extraction" claim was wrong — the card markup is a redesigned card, and the desktop roster/skills **tables were replaced** by cards. All polish is presentation-only: `dw-*` tokens only, no logic or money-behavior change, chip semantics preserved.

**Still out of scope (uncommitted, do not review):** `templates/member_detail.html` redesign, `templates/dashboard.html` title-glyph tweak, `static/css/app.css` one-liner — pre-existing working-tree edits from the earlier session.

## What changed (accurate)

**`6db1b3c` — team home + roster (includes pre-existing polish, disclosed):**
- *Polish riding along (earlier session, presentation-only):* team home rebuilt from tables to card layouts — skills table → stacked article cards, roster table → 2-col card grid; stats row (skills / members / delivery mode) added; "Manage skill list" moved into a `<details>` disclosure with registry chips and per-chip usage counts; mobile-first spacing. Tokens-only.
- *This session's change:* roster grid **capped at the first four cards** (`vas|slice:":4"`; header count still shows the true total); when more than four exist, a footer link **"See all N members →"** opens the new `/team/members/` page (`member_list` view reusing owner-scoped `selectors.list_vas`). Card markup lives in shared `templates/team/_member_card.html`, included by both surfaces. `path("members/", …)` registered before `path("<slug:member>/", …)`.
- Tests: roster cap, exactly-four (no link), login required, full-list render, tenancy.

**`a36caaf` — catalog category registry (schema change):**
- New **`ServiceCategory`**: owner FK (CASCADE), name unique per owner, slug unique per owner, frozen at creation (mirrors `team.Skill`). `Service.category` CharField → **FK PROTECT**; `Service.clean()` tenancy guard evaluates only when both `owner_id` and `category_id` are known (ModelForm `_post_clean` runs `full_clean` pre-owner; every real write path sets both).
- `ServiceForm` takes `owner`; `category` is a ModelChoiceField over the provider's own rows — cross-owner pks are invalid choices. `category_add` view + page at `/catalog/categories/add/` (GET+POST, idempotent `get_or_create_category`); "Add category" secondary button beside "Add service". Route precedes `<slug:category>/…`.
- Migrations `0006–0009`, data-preserving: model → nullable `category_fk` → backfill (one row per distinct owner+category string, slugs deduped per owner) → column swap, NOT NULL, constraint rebuild. The unique constraint is dropped **before** the column swap (SQLite rebuilds the table per column operation). Legacy empty-string categories backfill to a row named `""` (slug `category`) — preserved, not dropped (backlog note).
- Seed creates category rows via the same service; re-seed edit-safe on natural key. Service list groups by `category.name` with `select_related`. Admin updated (`category__name` search; ServiceCategory registered).
- Catalog tests updated for the FK world + new model/view coverage.

**`592254f` — pass-11 fixes:**
- Removed the coupled member-detail test (see correction 1).
- Locked the reviewer's cross-owner-pk POST probe as `test_post_cross_owner_category_pk_is_invalid_choice` (create path; invalid choice, zero services created).

**Docs:** design-log supersession entry (2026-10-01); backlog residuals: category rename/delete UI stays admin-only; account-deletion vs PROTECT; roster-card `.count` N+1 (prefetch doesn't serve `.count` — future `list_vas` annotation); migration 0008 empty-string note.

## Locked decisions to preserve

1. Money/claims discipline untouched — pricing, matching, FX, ranges-not-points, chip semantics all unchanged.
2. Tenancy enforced at every layer: form queryset scoping (invalid choice) + `Service.clean()` guard + canonical-category URL 404.
3. Slug discipline: category slugs frozen at creation, unique per owner; URL mismatch = 404.
4. Vocabulary pattern: category creation is the one free-text surface for this vocabulary, idempotent get_or_create per owner+name (mirrors team skill-list manager).
5. Tokens-only UI; no new dependencies; server-rendered; POST-only mutations; CSRF everywhere.
6. PROTECT (not CASCADE) between Service and ServiceCategory; owner deletion blocked while catalog rows exist (documented residual; no allauth delete-account path in MVP).

## Review checklist

1. **Verify the pass-11 blocking finding is actually fixed:** clean-HEAD worktree run must be fully green; the removed test's NOTE must be present; no remaining committed test depends on uncommitted templates.
2. **Migration safety:** replay 0006→0009 reasoning; adversarial legacy data (duplicate owner+category strings, cross-owner name reuse, slug-collision pairs, empty-string category) must dedupe/preserve/repoint with zero NULLs and the rebuilt constraint enforced.
3. **Tenancy probes:** cross-owner category pk on create AND edit POSTs → invalid choice, no writes; ORM mismatch fails full_clean; GET surfaces (list, select options, roster) never show other owners' rows.
4. **Route shadowing:** `/team/members/` and `/catalog/categories/add/` beat their slug routes.
5. **Polish accuracy check:** confirm the disclosed polish (tables→cards, stats row, details manager) is presentation-only — same behaviors, stored-field rendering, `dw-*` tokens only; chip semantics unchanged.
6. **Styleguide:** logic in services, reads in selectors, thin views, forms validate only, type hints.
7. **Gates:** rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **167 passed** (81 pre-existing warnings) in the working tree.
2. **Clean-HEAD worktree** (`git worktree add` at `592254f`): `pytest -q` → **167 passed**; `ruff check .` → clean. (This is the check that failed pass 11.)
3. `.venv/bin/python -m ruff check .` — clean. `manage.py check` — no issues. `makemigrations --check --dry-run` — no changes. `git diff --check` — clean.
4. Cross-owner pk POST probe committed and passing (create path).

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

## Verdict — pass 12 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) ran all gates including the clean-HEAD worktree check that failed pass 11.

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. Edit-path cross-owner category pk probe is not committed as a test (create path is); behavior verified correct live by this review (invalid choice, no write, control POST succeeds). Commit it with the next catalog card.
2. Weak type hints on ServiceForm.__init__ (owner: object, *args: object) — matches existing file convention; cosmetic.
3. Migration 0008 reverse is a documented noop (irreversible data migration) — disclosed, acceptable.
Rationale: All gates rerun and green, including the pass-11 failure mode itself: a clean-HEAD worktree at 94515e9 passes the full suite (167) and ruff, the coupled test is removed with an explanatory NOTE, and green-on-committed-templates proves no committed test depends on uncommitted markup. The 0006→0009 chain was verified by adversarial replay on legacy data (duplicate owner+strings, slug-collision pairs, empty strings, cross-owner reuse): zero NULLs, exact legacy strings preserved, one row per distinct pair, all constraints and FK PROTECT enforced at DB level. Tenancy verified live on both create and edit POSTs (invalid choice, no writes) plus GET surfaces; route shadowing verified via resolve(); the bundled polish is confirmed presentation-only with dw-* tokens and unchanged chip semantics; styleguide and locked decisions 1–6 preserved; builder evidence matched every reproduction.
```

**Disposition of minors:**
1. Edit-path probe → backlog ("Edit-path cross-owner category pk probe"); to be committed with the next catalog card.
2. Loose `owner: object` hint → accepted as-is; matches the established convention across `forms.py` (same shape as `RequiredSkillForm.__init__`).
3. Irreversible 0008 reverse → accepted; one-way column swap, documented in the migration docstring.

**Pass closed.** Scope commits `6db1b3c`, `a36caaf`, `592254f`, `94515e9` stand as reviewed.
