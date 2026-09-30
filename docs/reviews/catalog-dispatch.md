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
