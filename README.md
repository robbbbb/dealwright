# Dealwright

> Discovery calls, crafted into deals.

Django SaaS for automation freelancers, VAs, and small agencies: paste what the client said → get structured facts, transparent ROI estimates, service recommendations from the catalog, a rule-based VA match, and a guardrailed, client-ready proposal with PDF export.

**Stage: Card 0 (scaffold) implemented — in review.** All design decisions live in `docs/design/`.

## Repository map

| Path | What |
|---|---|
| `docs/design/design-log.md` | Master decision log — read this first |
| `docs/design/mvp-build-plan.md` | Card-by-card build plan (Cards 0–11), TDD anchors, review gates |
| `docs/design/system-design.md` | Railway deployment, capacity, latency, durability |
| `docs/design/service-catalog-draft.md` | Seed catalog: 8 categories, ~26 services, PHP hypothesis pricing |
| `docs/design/generation-guardrails.md` | Provider profile + generation rules (deterministic zones, AI slots, hard gates) |
| `docs/mockups/` | HTML mockups: internal pipeline screens, agency proposal, solo-VA proposal, podcast workflow |
| `docs/integrations/` | n8n workflow JSON (pastor podcast case) |
| `docs/backlog.md` | Deferred work and open items registry |

## Locked stack (do not relitigate mid-build)

Django + PostgreSQL · server-rendered templates + HTMX (no SPA, no npm) · WeasyPrint PDF · pytest · z.ai LLM via thin client (GLM-5.3-Flash extraction, GLM-5.3 writing; **no LangChain**) · guardrails as versioned data · deployed on Railway (Hobby to ~1k users) · single-user MVP with tenancy-ready `owner` FK · AI never emits a number.

## Run it (dev)

```bash
python3 -m uv sync            # deps into .venv
cp .env.example .env          # then fill in values (never commit .env)
docker compose up -d db       # local Postgres (optional; sqlite fallback without it)
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Tests / lint: `.venv/bin/python -m pytest` · `.venv/bin/python -m ruff check .`

## Building

One card per fresh session, per `docs/design/mvp-build-plan.md`. Cards end with tests green → review-dispatch → fresh reviewer subagent → verdict recorded. Start sessions in this directory.
