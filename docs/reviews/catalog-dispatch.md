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
