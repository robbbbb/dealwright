# Dispatch — Card 2: service catalog (2026-09-29)

**Scope:** commit `6c25ab9` (+ the docs commits around it). New `catalog` app: `Service` + `RequiredSkill` models (migration `catalog/0001_initial`), `seed_catalog` command (25 services / 8 categories from `docs/design/service-catalog-draft.md`), Django admin with skill inline, tests at the 80–85% tier. Design decisions recorded in `docs/design/design-log.md` "Card 2 build decisions". **For:** fresh GLM-5.3 reviewer (read-only, run gates). Seed: repo root `/home/robbb/dealwright`, venv `.venv/`.

**Spec baseline:** `docs/design/mvp-build-plan.md` Card 2 + `docs/design/service-catalog-draft.md` + styleguide (models validate shape; feature-app rule) + design-log Card 4 deviation (proficiency ladder). TDD anchor required: `test_service_must_declare_roi_parameter_or_qualitative`.

**Gates:**
1. `.venv/bin/python -m pytest` — expect **111 passed** (79 pre-existing + 32 catalog)
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — clean
4. `manage.py migrate` idempotent; `manage.py seed_catalog <user>` on the dev DB already ran ("25 created, 0 already present")
5. Seed audit: run seed twice on a scratch user via a /tmp django script; assert 25 services, 8 categories, every row passes `full_clean()`, every service has ≥1 RequiredSkill, re-run is a no-op, renamed rows are preserved (not clobbered)
6. Model discipline: no protected-characteristic fields anywhere in the catalog schema (grep migration + models); money fields are ranges (low/high pairs) or custom_quote; no currency conversion anywhere (Q3 passthrough)
7. Admin: changelist + add render (smoke tests cover; may verify via test client)

**Adjudicate:**
- The lever split (reduction % + hours/week) and typed revenue effect — design-log "Card 2 build decisions" documents rationale; confirm the anchor test name matches the plan.
- RequiredSkill imports `team.SkillLevel` (cross-app choice reuse, no FK dependency) — one-ladder rule for Card 5.
- Seed edit-safety semantics (renames → original re-created alongside).
- Coverage tier: 32 tests across validation/constraints/seed/admin = 80–85% target for catalog management.

## Verdict (pass 1)
### Pass 1 verdict — APPROVED

All 7 gates green with pasted evidence (111 passed, ruff/check clean, migration idempotent, seed audit clean, no protected characteristics, money discipline holds, admin renders); TDD anchor verified in both directions; seed figures spot-checked against the draft with no drift on the three probes.

```
Verdict: APPROVED
Blocking findings: none. All 7 gates pass with pasted evidence; quantifier rule, money discipline, tenancy, ladder reuse, seed idempotency/edit-safety, and hermeticity all verified against the spec baseline.
Minor findings: (1) model/migration help_text drift inside the card; (2) qualitative-flag drift — client portal + podcast pipeline unflagged vs draft's "(qualitative)" markers; (3) response-time lever (hrs→minutes) unrepresented — Card 3 units; (4) price_summary hardcodes ₱ — Q3 i18n; (5) seed validates after insert; (6) dead admin overrides.
Rationale: The card delivers exactly what mvp-build-plan Card 2 specifies — models with the quantifier rule as the TDD anchor, seed transcribed from the draft with correct figures on every spot-checked row, admin CRUD, idempotent/edit-safe seeding — at the mandated 80–85% tier, with all seven gates green on re-run by a fresh reviewer.
```

**Builder disposition (2026-09-29):** minors 1–2, 5–6 → fixed in the follow-up commit (0001 regenerated, no migration drift; both draft-marked rows flagged — 8 total per updated design-log entry; clean-before-save seeding; dead admin code removed). Minors 3–4 → backlog lines recorded (Card 3 units; Q3 i18n). **Card 2: approved & closed.**

---

# Pass 2 — ROI levers removed from Service (Robb decision, 2026-09-30)

**Scope:** the refactor commit removing reduction/hours_saved/revenue_effect/qualitative_value fields, the RevenueEffect enum, the quantifier rule, and the 10 lever tests; migration regenerated pre-deploy; seed data kept verbatim minus lever keys. Design basis: design-log "Robb decision: catalog is price-only" + backlog Card 3 planning item. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest (expect **101 passed** — 111 minus 10 removed lever tests), ruff, manage.py check, `makemigrations --check --dry-run` clean, seed still 25 services / 8 categories with every row passing full_clean, no ROI field names anywhere in catalog models/migration/seed (grep: reduction|hours_saved|revenue_effect|qualitative), admin still renders, pricing rule (custom_quote or ranges) and pair validation intact.

**Adjudicate:** removal is complete and coherent (no dead references); the Card 3 dependency break is properly recorded (design-log + backlog + research doc §C supersession note); test count delta is exactly the removed lever tests.

## Verdict (pass 2)
### Pass 2 verdict — APPROVED

Removal complete and coherent: zero live lever references (docstring records only), migration regenerated with no drift, test delta exactly the 10 removed quantifier/lever tests, seed 25/8 all-valid with 76 skill rows, pricing rule + pair validation intact, decision trail present in all three required places.

```
Verdict: APPROVED
Blocking findings: none. All 7 gates pass with pasted evidence; the removal is complete (zero live field references — only docstring records of the removal, which are permitted), the migration was regenerated with no drift, the test delta is exactly the 10 removed quantifier/lever tests (7 functions + 3 parametrize cases), seed still yields 25 services / 8 categories with all rows full_clean-valid and ≥1 RequiredSkill per service, and the pricing rule (custom_quote-or-ranges + pair ordering) survives intact per tests and direct probe. The decision trail is coherent: design-log entry with named Card 3 consequence, backlog planning item, research doc §C supersession note.
Minor findings: (1) mvp-build-plan.md still carries the superseded Service/Card-3 text — amend when Card 3 is planned; (2) pre-existing uncommitted one-line dashboard.html edit (Robb's, untouched).
Rationale: Pass 2 supersedes pass 1's quantifier-rule approval per Robb's recorded decision, and the refactor delivers exactly that: a price-only Service with owner/category/name/tags/price ranges/custom_quote/delivery/skills, lever fields and their rule fully excised, hermetic gates green on re-run by a fresh reviewer, and the Card 3 dependency break documented in all three required places.
```

**Builder disposition (2026-09-30):** minor 1 → backlog line added (amend build-plan text at Card 3 planning). Minor 2 → Robb's edit, untouched. **Pass 2: approved & closed.**

---

# Pass 3 — retainer vocabulary (Robb decision, 2026-09-30)

**Scope:** label-only change — verbose names "monthly price — low/high" → "retainer — low/high (monthly)", `price_summary()` → "retainer ₱…/mo", draft rule 2 annotated, design-log vocabulary entry (precedent: bench→team). Internal field names unchanged by design; migration regenerated pre-deploy. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest (101 passed), ruff, manage.py check, no migration drift, seed 25/8 re-loads and validates, grep confirms no stray "monthly price" labels in catalog/ (code names excluded by design), price_summary renders retainer format.

## Verdict (pass 3)
### Pass 3 verdict — APPROVED

Label-only as designed: field names stable everywhere, migration structurally identical modulo the two verbose_name strings, price_summary renders "setup ₱… · retainer ₱…/mo" with "Custom quote" fallback, all gates green, decision trail (design-log vocabulary entry + draft rule 2 annotation) present.

```
Verdict: APPROVED
Blocking findings: none. All six verification items green with pasted evidence: the feature commit touches only the four claimed files; monthly_low/monthly_high survive intact in models, seed, tests, and migration (label-only as designed); pytest 101 passed, ruff clean, manage.py check clean, no migration drift; migration 0001 is structurally identical to pass 2's modulo the two verbose_name strings and generator timestamp; the /tmp probe seeds 25 services idempotently, renders price_summary as 'setup ₱4,000–8,000 · retainer ₱1,500–3,000/mo' with the 'Custom quote' fallback, and every row passes full_clean(); zero stray "monthly price" labels in catalog/; decision trail present at HEAD.
Minor findings: (1) pre-existing uncommitted templates/dashboard.html edit (Robb's); (2) pass-2 minor 1 (build-plan text amendment) remains backlog-dispositioned.
Rationale: Pass 3 delivers exactly what the dispatch specifies — a vocabulary-only relabel of the monthly pricing concept to "retainer" ... with internal field names deliberately stable per the recorded decision and its bench→team precedent, migration regenerated pre-deploy with zero structural drift, and all hermetic gates green on re-run by a fresh reviewer.
```

**Builder disposition (2026-09-30):** minors → both pre-existing/out-of-scope, untouched. **Pass 3: approved & closed.**

---

# Pass 4 — per-service currency (Robb request, 2026-09-30)

**Scope:** the feature commit adding `Service.currency` (ISO 4217 CharField, default PHP, clean() validates 3 uppercase letters), `currency_symbol()` map (₱ $ € £ A$ C$ S$ + code fallback), symbol-aware `price_summary()`, 5 currency tests, migration regenerated pre-deploy, design-log Q3 refinement + backlog minor resolved. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest (**105 passed** = 101 + 5 currency), ruff, manage.py check, no migration drift, seed 25/8 reloads and validates (all PHP), admin renders, grep: no hardcoded ₱ in price_summary, currency validation covers lowercase/toolong.

**Adjudicate:** no-FX discipline (declarations only, one row per market); Card 5 same-currency rule recorded; symbol fallback never invents glyphs.

## Verdict (pass 4)
### Pass 4 verdict — APPROVED

Probes confirm: default PHP, USD symbol rendering, JPY code fallback (no invented glyphs), both invalid inputs rejected; zero conversion logic anywhere; migration drift is exactly the currency field; PHP behavior byte-identical to pass 3; Card 5 same-currency rule recorded; backlog minor struck resolved.

```
Verdict: APPROVED
Blocking findings: none. All gates pass with pasted evidence: pytest 105 passed, ruff clean, manage.py check clean, no migration drift; the feature commit touches only the five claimed files; the /tmp sqlite probe confirms default PHP, USD symbol rendering, JPY code fallback, and both invalid inputs rejected; no-FX discipline holds (zero conversion logic); migration 0001 differs from pass 3's by exactly the currency field; seed reloads 25/8 idempotently, all-PHP, all rows full_clean-valid; decision trail complete.
Minor findings: (1) dispatch arithmetic label said "101 + 5 currency" — TestCurrency contributes 4 test functions; total 105 correct, label off by one, docs-only. (2) Pre-existing uncommitted templates/dashboard.html edit (Robb's).
Rationale: Pass 4 delivers exactly the dispatch scope — an ISO 4217 CharField declaration with default PHP and uppercase-3 validation, a symbol map with honest code fallback, and a symbol-aware price_summary — with zero FX logic anywhere (declarations only, one row per market, per Q3) ... all hermetic gates green on re-run by a fresh reviewer.
```

**Builder disposition (2026-09-30):** minor 1 → noted (this file's own label; total gate number was correct). Minor 2 → Robb's edit, untouched. **Pass 4: approved & closed.**

---

# Pass 5 — provider catalog UI (Robb request, 2026-09-30)

**Scope:** the feature commit after 985d0f4 (git log --oneline -3). Catalog app grows views/selectors/forms/urls + templates/catalog/ (list, form, skills manager, empty-state seed button); seed data extracted to `catalog/seed_data.py` with the command now a thin wrapper over `services.seed_default_catalog` (single write path); sidebar "Service catalog" wired live. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest (**124 passed** = 105 + 19 view tests), ruff, manage.py check, no migration drift (models untouched), CSS rebuilt & committed, DOM probes via headless Chromium: list 8 category sections / 25 rows / correct ₱ price strings / 76 skill chips / sidebar active; mobile 390px: 25 stacked cards, no horizontal overflow; edit page 11 fields, tags prefilled, 7 currency options, skills list + add form; empty state (fresh user) shows seed button, click → 25 rows.

**Adjudicate:** team-app conventions held (services full_clean, selectors, POST-only, tenancy 404s); tags comma-parse in form only (input validation, not business logic); seed reuse not duplication; claims discipline (prices still labelled ranges via price_summary, no computed conversions).

## Verdict (pass 5)
### Pass 5 verdict — APPROVED

Probes confirm: exact scope (models/migrations untouched), 124 passed/ruff/check/no-drift, seed data byte-equivalent (25/8/76) with single write path for command + in-app button, login gating, 404 tenancy on all four pk-addressed ops, ISO-4217 rejection via ModelForm, trimmed tag parsing, seed idempotency (25 then 0), live sidebar wiring with namespace-active isolation, claims discipline (price_summary only, zero conversion logic).

```
Verdict: APPROVED
Blocking findings: none. Scope is exact (13 expected files, models/migrations untouched); all four hermetic gates green on re-run; seed data byte-equivalent to the pass-2-reviewed command with the command now a thin wrapper over the single services.seed_default_catalog write path used by both entry points; probes confirm login gating, 404 tenancy on all four pk-addressed ops, ISO-4217 field-error rejection with zero rows created, trimmed tag parsing, skill round-trip, seed idempotency, live sidebar wiring with namespace-active isolation, and claims discipline.
Minor findings: (1) seed_default_catalog performs 25+76 writes without @transaction.atomic (only add_required_skill wrapped) — pass-1/2-approved path moved verbatim, so atomic wrap is a follow-up nicety, not a regression. (2) Currency select offers 7 codes while the model accepts any well-formed ISO 4217 code — consistent declaration-only design; select is convenience. (3) Dispatch listed headless-Chromium DOM probes; reviewer verified DOM structure via test client instead of a live viewport. (4) services_status helper in test_views.py oddly placed, asserts only 302 — cosmetic. (5) Pre-existing uncommitted templates/dashboard.html edit (Robb's), untouched.
Rationale: Pass 5 delivers exactly the dispatch scope — thin views over selectors/services with the house pattern held line for line, forms restricted to input validation, POST-only mutations, ownership-404 tenancy, the seed command refactored to share one write path with the in-app empty-state action without data drift, and the sidebar wired live — with all gates, probes, and claims-discipline checks green on independent re-run, and the card's coverage tier respected.
```

**Builder disposition (2026-09-30):** minor 1 → applied (`@transaction.atomic` on seed_default_catalog). Minor 2 → by design (Q3 declarations; select = convenience). Minor 3 → acceptable (same DOM structure; live probes were builder-side evidence). Minor 4 → applied (helper removed). Minor 5 → Robb's, untouched. **Pass 5: approved & closed.**

---

# Pass 6 — skill registry: FKs replace free-text (Robb decision, 2026-09-30)

**Scope:** the feature commit after 59e89e6 (`754bc80`). New `team.Skill` registry (unique per owner+name); `Capability.skill` + `RequiredSkill.skill` become PROTECT FKs; owner-scoped dropdowns (member skills, catalog required skills); seed grows the registry via `get_or_create_skill`; data-preserving migrations team/0002-0003 + catalog/0002-0003; design-log entry superseding the free-text half of 2026-09-29; backlog: rename affordance. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest **124 passed** (team + catalog suites updated to the FK API), ruff, check, no drift; fresh-sqlite migrate + seed verified (76 reqskills → 22 deduped skills); dev Postgres data preserved (50 services / 152 reqskills / 46 skills); DOM probes: catalog edit dropdown (23 options) adds work; member detail dropdown lists owner's 25 skills; team-home free-text add creates registry + capability.

**Adjudicate:** tenancy at the form (ModelChoiceField queryset owner-scoped — cross-owner pk = invalid choice); PROTECT semantics on referenced skills; migration discipline (constraint dance for SQLite, pending-trigger split for Postgres — recorded in design-log); no string matching anywhere in code paths.

## Verdict (pass 6)
### Pass 6 verdict — APPROVED

Probes confirm: registry unique per owner+name with PROTECT from both referencing tables; data migrations verified in both directions (real backfill over old-schema TEXT rows: per-owner dedup, cross-app row sharing, NOT NULL + constraints survive); tenancy at the form (cross-owner pk = invalid choice, zero rows) plus 404 at the view; production query paths FK-join only; house rules + POST-only discipline hold; decision trail complete.

```
Verdict: APPROVED
Blocking findings: none. Scope is exact (20 files, no templates — chips render via Skill.__str__ unchanged); all four hermetic gates green; registry integrity proven (unique per owner+name, PROTECT from both Capability and RequiredSkill); data migrations verified in both directions on fresh sqlite including a real backfill probe over old-schema TEXT rows; tenancy holds at the form and view; string matching fully excised from production query paths.
Minor findings: (1) get_or_create_skill validates AFTER get_or_create — stray invalid rows possible from direct calls; docstring overclaims. (2) FK chip rendering is N+1 on list/team paths (no select_related); team selector docstring stale. (3) Dev-Postgres counts drifted append-only vs card snapshot — no action. (4) DOM probes verified structurally via test client, not live viewport (pass-5 disposition). (5) No model-level owner-consistency check between skill registry and holder/service. (6) Cosmetic over-indent in catalog/0003.
Rationale: Pass 6 delivers exactly the dispatch scope — a provider-owned team.Skill registry, PROTECT FKs on both referencing models, owner-scoped dropdowns pushing tenancy into form validation, seed vocabulary growth via get_or_create_skill, and data-preserving migrations independently verified (including on real old-schema rows and in reverse) — with every gate green on re-run by a fresh reviewer.
```

**Builder disposition (2026-09-30):** minor 1 → applied (`clean_fields()` before lookup — validate-before-write, no stray rows, no false unique errors; +tests). Minor 2 → applied (`select_related("skill")` / `prefetch_related("required_skills__skill")` + docstring fixed). Minor 3 → trail only. Minor 4 → accepted (pass-5 precedent; live probes were builder-side). Minor 5 → applied (model-level owner-consistency guards on Capability + RequiredSkill, both tested). Minor 6 → applied (indent fixed). **Pass 6: approved & closed.** 126 passed after minors.

---

# Pass 7 — seed_skills command (Robb request, 2026-09-30)

**Scope:** the feature commit after 7a05b5e. `team/seed_data.py` (DEFAULT_SKILLS derived from catalog.seed_data union), `services.seed_default_skills` (idempotent), thin `seed_skills` command, 6 tests incl. cross-seed row sharing. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest **132 passed** (6 new), ruff, check, no drift; live dev run: both existing users report 22 already present (registry pre-populated by pass-6 backfill — idempotency visible).

**Adjudicate:** derivation not duplication (single source of truth; no invented vocabulary); both seeds converge on shared rows; command = thin wrapper (house pattern).

## Verdict (pass 7)
### Pass 7 verdict — APPROVED

Probes confirm: scope exact (7 files, no models/migrations/templates); gates green (132 passed / ruff / check / no drift); DEFAULT_SKILLS genuinely derived at import (programmatic equality with the 22-name union, zero hardcoded literals); live sqlite: CommandError on unknown user, 22 valid owner-scoped rows first run, 0 on re-run, 0 for other users, and convergence (after seed_catalog the registry stays 22 with all 76 required-skill rows linking to those same pks); write path through the validated get_or_create_skill; design-log records derived-not-duplicated.

```
Verdict: APPROVED
Blocking findings: none. Scope is exact (7 files); all four hermetic gates green on re-run; DEFAULT_SKILLS is genuinely derived at import with zero hardcoded literals; live probe confirms CommandError on unknown user, idempotency, tenancy, and cross-seed convergence; write path goes through get_or_create_skill (validate-before-create) with the command a pure thin wrapper; design-log records the derived-not-duplicated rule.
Minor findings: (1) seed_default_skills issues one extra .exists() query per name to count creations — cosmetic. (2) test_shares_rows_with_catalog_seed spot-checks only 2 shared names rather than the full 22-row count after both seeds. (3) Robb's pre-existing uncommitted templates/dashboard.html edit, untouched.
Rationale: Pass 7 delivers exactly the dispatch scope — a starter registry vocabulary that cannot drift from the catalog draft because it is computed from it, seeded through the single validated get_or_create_skill write path behind an idempotent thin command, with both seed entry points proven to converge on shared registry rows — and every gate, derivation check, and behavioral probe passed on independent re-run by a fresh reviewer.
```

**Builder disposition (2026-09-30):** minor 1 → applied (two COUNT queries bracket the loop instead of per-name `.exists()`). Minor 2 → applied (test now asserts the full invariant: registry stays at exactly the vocabulary size after both seeds). Minor 3 → Robb's, untouched. **Pass 7: approved & closed.** 132 passed after minors.

---

# Pass 8 — slug URLs (Robb decision, 2026-09-30)

**Scope:** the feature commit after 17b91fe. `Service.slug` (unique per owner) + `RequiredSkill.slug` (unique per service), frozen at creation in save(); slugged routes incl. category slug validated canonically; data-preserving migrations 0004/0005; design-log + backlog (team-app follow-up). **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest **132 passed**, ruff, check, no drift; dev Postgres migrated with backfill (0 null slugs); DOM probes: list links all slugged, zero int URLs, edit 200, legacy `/catalog/1/` → 404; rename keeps slug; same-name cross-category gets `-2`.

**Adjudicate:** slug generation in save() (holds from any entry path incl. admin/shell); constraint validation with blank slug only transient pre-save (no blank rows can exist post-save); canonical-category 404; no pk-based routes remain in catalog/urls.py; templates resolve slugs only.

## Verdict (pass 8)
### Pass 8 verdict — APPROVED

Probes confirm: zero int patterns in urls.py, zero pk-based reverses in templates, legacy `/catalog/1/` → 404; fresh-sqlite from zero: 25/25 slugged with 0 blanks, `-2` suffixes, rename-frozen slugs, shell-path saves generate slugs, wrong-category 404, cross-user 404, delete GET 405; both slug constraints present in DB DDL; re-seed idempotent; slug logic only in save(), clean() read-only.

```
Verdict: APPROVED
Blocking findings: none. Scope is exact (11 dispatched files); all four hermetic gates green on re-run; zero int patterns remain in routes or template reverses; fresh-sqlite probes prove slug semantics end-to-end (no blanks, suffixing, freeze-on-rename, canonical-category 404, tenancy 404, POST-only deletes); migrations verified from zero with constraints present and idempotent re-seeding; save()-only slug generation with read-only clean(); decision trail complete.
Minor findings: (1) service_edit retained ~28 lines of unreachable old pk-based body referencing `service` (now the slug string) — latent trap, delete in cleanup. (2) No dedicated slug-semantics tests in the suite — verified live by review; recommend follow-ups. (3) 0005 docstring overstates ("NOT NULL" — columns were already NOT NULL; AlterField is a state restatement). (4) Dev-Postgres backfill verified by sqlite equivalence (sandbox limit, pass-5/6 precedent). (5) Robb's pre-existing dashboard.html edit, untouched.
Rationale: Pass 8 delivers exactly the dispatch scope — owner-scoped Service slugs and service-scoped RequiredSkill slugs frozen at creation in save() (holding from every entry path including raw shell saves, proven live), slug-addressed routes with canonical category validation, and data-preserving migrations independently verified from zero — with every gate, probe, and decision-trail check green on independent re-run.
```

**Builder disposition (2026-09-30):** minor 1 → applied (dead pk-based body deleted). Minor 2 → applied (TestSlugSemantics: freeze-on-rename, `-2` suffix, cross-owner same slug, wrong-category 404 — 4 tests). Minor 3 → trail note only (committed migration, behavior identical). Minor 4 → accepted (precedent). Minor 5 → Robb's, untouched. **Pass 8: approved & closed.** 136 passed after minors.

---

# Pass 9 — team slug URLs (Robb: "why did you not update the team?", 2026-09-30)

**Scope:** the feature commit after 801605c. team/{models,selectors,urls,views}.py + templates/team/: VAProfile.slug (unique per owner) + Capability.slug (unique per owner across holders), frozen at creation; slugged routes; data-preserving migrations team/0004+0005; backlog item resolved; design-log entry. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pytest **139 passed** (3 new slug tests), ruff, check, no drift; dev Postgres migrated (0 null slugs).

**Adjudicate:** same rules as pass 8 (frozen slugs, owner-scoped 404s, canonical lookups); orphan-capability behavior preserved (DB check constraint, not slug generation); no int patterns remain anywhere in the app (team + catalog).

## Verdict (pass 9)
