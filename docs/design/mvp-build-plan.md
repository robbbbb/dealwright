# MVP Build Plan — card breakdown v1 (2026-09-28)

Design stage deliverable: the implementation plan, not the code. Built from the handoff build order + all design decisions in `design-log.md`. When the repo is created, this file moves in as the spec/task registry (Status lines per card) with `docs/backlog.md` beside it.

## Fixed ground rules (already decided — do not relitigate mid-build)

- Django + PostgreSQL, server-rendered templates + HTMX, no SPA, no npm. Minimal deps: `django`, `psycopg`, `django-environ`, `htmx` (static), `weasyprint`, `pytest`, `pytest-django`, `factory-boy` (or plain fixtures), `ruff`.
- Single-user MVP per install; `owner` FK on all top-level models (tenancy-ready).
- Financial/core logic (ROI engine, matching, LLM validation) → **95–100% coverage**; catalog/profile management → **80–85%**; templates/UI → **40–50%** smoke only.
- LLM: GLM-5.3-Flash extraction + GLM-5.3 writing; guardrails as versioned data; usage & cost logged per request; AI never emits prices/math/skill claims.
- Every card ends: tests green → typed review-dispatch card → fresh GLM reviewer subagent (read-only) → verdict recorded → merge gate. Builder never approves own work.
- Working repo name (placeholder, change anytime): **dealwright** → `/home/robbb/dealwright`, GitHub `robbbbb/dealwright`.

## Card 0 — Scaffold
**Goal:** runnable skeleton with auth, Postgres, and the registries.
Tasks: project + `core` app; env-based settings (secrets from env/file, never chat); login/logout; base template + minimal CSS; `docs/backlog.md` + copy of design docs; git init, initial commit; pytest wired with one smoke test; **Dockerfile + railway.toml from day one** (deploy target = Railway per `system-design.md`; Postgres = Railway plugin in prod, local Postgres in dev).
TDD anchor: `test_login_page_renders` + `test_settings_read_env`.
Done when: `pytest` green locally, login works, Postgres connected, registry files committed.
Deps: name decision (above).

## Card 1 — Core domain models
**Goal:** the discovery side of the data model.
Models: `Client` (owner FK, industry, contact), `DiscoverySession` (client FK, raw notes, status), `WorkflowActivity` (employees, hours/week, hourly cost, tools, error/delay notes), `BusinessProblem` (description, severity, tags). Admin registered; migrations; factories.
TDD anchor: `test_client_requires_owner`; constraint tests (non-negative hours, decimal money).
Done when: models + admin + tests at 80–85%.
Deps: Card 0.

## Card 2 — Service catalog + seed
**Goal:** catalog as the deterministic source of prices and ROI parameters.
Model: `Service` (category, name, problems-solved tags, reduction range low/high, revenue-effect params or `qualitative-value` flag, setup price range, monthly range, required VA skills + min level, delivery days). Seed fixture from `service-catalog-draft.md` (8 categories, 26 services). Quantifier rule enforced: reduction range or revenue effect or qualitative flag — validation test.
TDD anchor: `test_service_must_declare_roi_parameter_or_qualitative`.
Done when: seed loads idempotently; admin CRUD; catalog tests 80–85%.
Deps: Card 0 (1 helpful).

## Card 3 — ROI engine (pure Python, TDD, 95–100%)
**Goal:** all money math, zero LLM, zero UI.
Module `core/roi/`: automation mode (monthly_hours × reduction, labor savings, revenue gain, payback), delegation mode (hours freed × client value − cost), scenarios derived from range low/mid/high, assumption records (versioned), currency field passthrough (no FX). Worked-example fixtures: pastor case (12h/mo, 75%, ₱300/hr → 9h, ₱2,700) and LF case (26/31.2/34.6h rows → ₱7,280/8,736/9,688). Edge cases: zero benefit (payback = None, no ÷0), zero employees, empty ranges.
TDD anchor: `test_pastor_case_expected_numbers`.
Done when: 95–100% coverage incl. negatives; `Estimate` model persists inputs + outputs + assumptions.
Deps: Card 1 (uses WorkflowActivity), Card 2 (uses reduction ranges).

## Card 4 — Provider & VA profiles
**Goal:** who delivers.
Models: `ProviderProfile` (delivery_mode solo|team, persona, branding name), `Capability` shared model (skill, level enum Beginner→Verified, evidence type, verification status) attached to provider (solo) or `VAProfile` (team bench: rate, availability hours, timezone, languages, industry experience). Protected-characteristic fields simply do not exist in the schema (test: no such column/matching input).
TDD anchor: `test_capability_distinguishes_claimed_from_verified`.
Done when: profile CRUD (admin + minimal forms), 80–85%.
Deps: Card 0–1.

## Card 5 — Rule-based matching engine (pure Python, 95–100%)
**Goal:** explainable shortlists + solo qualification.
Hard filters: rate ≤ budget, availability ≥ required hours, timezone, language. Skill coverage: required vs capability with verified > evidenced > claimed weighting; reason strings generated per criterion ("✓ Calendar mgmt — Verified (completed project)"). Team mode: ranked shortlist with gaps. Solo mode: qualification verdict (covered/partial/gap → train/partner/refer). Ties broken transparently (more verified wins; no hidden scores).
TDD anchor: `test_verified_beats_claimed_at_same_skill`; LF bench fixture → Maria first, Jen flagged on rate.
Done when: engines tested with fixture benches; 95–100%.
Deps: Cards 2, 4.

## Card 6 — LLM extraction + guardrails v1 (mocked tests, 95–100% on validation)
**Goal:** notes → validated structured facts, nothing invented.
Client wrapper (GLM API via env key): extraction call (notes + schema + catalog digest → JSON), retry once, usage/cost logged per request. Validation layer: field whitelist, source-snippet required per extracted fact (untraceable → dropped), prices/numbers rejected from AI fields, banned-phrase list, missing-info → follow-up questions. Guardrail ruleset as versioned data; every result logs ruleset version.
TDD anchor: `test_extraction_drops_untraceable_fact`; `test_banned_phrase_regenerates_or_strips`.
Done when: mocked-LLM suite green; one live-key smoke behind env flag; audit rows recorded.
Deps: Cards 1, 2 (schema references).

## Card 7 — Discovery session UI
**Goal:** the provider's working flow (the internal screens mockup).
HTMX flow: new session → paste notes → run extraction → review form grouped client/workflows/problems/goals, each field with source-snippet chip → edit/confirm → follow-up questions panel → estimate view (scenario toggle, assumptions table, edit assumptions → recompute on save).
TDD anchor: view tests — `test_session_flow_paste_to_estimate` (factory data, no live LLM).
Done when: 40–50% smoke via view tests; demo-able with the LF input.
Deps: Cards 3, 6.

## Card 8 — Proposal generation + PDF
**Goal:** the sellable artifact.
Deterministic composition (sections from spec, prices/estimates/skills from DB only) → writer model for narrative slots under guardrails → persona adaptation (solo: "About me", no team language; team: match card or omit if empty bench) → in-app editor (structured fields, not block builder) → versioning (immutable once sent) → WeasyPrint PDF from the same template → disclaimers block always present → human approval gate before export/send.
TDD anchor: `test_proposal_numbers_all_traceable_to_structured_fields`; `test_solo_mode_has_no_team_language` (banned-phrase scan on rendered text).
Done when: LF input → proposal matching `proposal-solo-va-mockup.html` shape; PDF renders; approval gate enforced.
Deps: Cards 3, 5, 6 (7 helpful).

## Card 9 — Dashboard + proposal tracking
**Goal:** the home screen + outcome loop.
Dashboard: lists + counters (clients, sessions, estimates, proposals, VAs, matches). Proposal statuses: draft → sent → viewed → accepted/declined; outcome note on close (feeds future assumption defaults; store now, learn later).
TDD anchor: `test_proposal_status_transitions`.
Done when: 80% on status logic, smoke on views.
Deps: Cards 1–8 (thin; mostly wiring).

## Card 10 — n8n boundary
**Goal:** integration surface without giving up source-of-truth.
Token-authenticated API: proposal events (created/sent/viewed/accepted) via webhook endpoints; documentation for n8n flows (email follow-up, CRM update). No inbound writes to financial fields from n8n.
TDD anchor: `test_webhook_requires_token`; `test_n8n_cannot_write_estimate_fields`.
Done when: endpoints tested; one example n8n flow JSON committed (adapt existing podcast workflow pattern).
Deps: Card 9.

## Card 11 — Pilot prep
**Goal:** one real workflow end to end.
Seed pastor-podcast case through the whole pipeline (session → estimate ₱2,700 case → services → proposal → PDF); demo dataset; **deployment to Railway Hobby per `system-design.md`** (web + Postgres plugin + PDF volume; Serverless/app-sleeping OFF on prod; backup stopgap = nightly pg_dump runbook); go/no-go checklist against the handoff's 7-point MVP success definition.
TDD anchor: integration test — pastor fixtures produce the documented numbers.
Done when: Railway URL + pastor proposal PDF generated from real app; success checklist all ✅.
Deps: all.

## Order & sizing

```
0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11
          (3 & 4 parallelizable; 5 after both)
```

One card per fresh session; each sized to finish inside ~half a context window including its review pass. Cards 3, 5, 6 are pure logic — the fast, deeply-tested ones. Cards 7, 8 are the UI weight. Card 11 is the pilot gate.

## What is deliberately NOT in MVP
Billing/subscriptions (post-pilot, once pricing is validated) · live transcription · automated sending · AI ranking · marketplace · mobile · white-label UI (model-ready via `owner`, but no UI) · multi-currency FX.

## Open before Card 0 starts
1. ~~Confirm working name~~ → **resolved 2026-09-28: Dealwright** (`/home/robbb/dealwright`, repo `robbbbb/dealwright`).
2. ~~Confirm PostgreSQL instance~~ → **resolved 2026-09-28: Railway Postgres plugin in prod** (per `system-design.md`), local Postgres in dev.

**Card 0 is unblocked. Start it in a fresh session opened at `/home/robbb/dealwright`.**
