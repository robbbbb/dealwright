# Dealwright — Django style guide

Adapted from the [HackSoft Django Styleguide](https://github.com/HacksoftBG/Django-Styleguide) and its reference implementation ([Styleguide-Example](https://github.com/HackSoftware/Django-Styleguide-Example/)), tuned for Dealwright: server-rendered templates + HTMX (no DRF), Railway deploy, coverage tiers per `AGENTS.md`. Adopted at Card 0 (2026-09-28). Deviations require a design-log entry.

## Project structure

```
manage.py
config/                # project package (not an app) — renamed from `dealwright/` per Robb, 2026-09-28
  settings/            # base | development | testing | production — env-driven
  urls.py  wsgi.py  asgi.py
core/                  # home + shared surfaces
templates/             # project-level templates (base.html, account/, …)
static/
  css/src/input.css    # Tailwind v4 input — money-green tokens as @theme colors
  css/app.css          # generated (committed so clone-and-run works without the CLI)
scripts/build_css.sh   # Tailwind standalone CLI — NO npm/node (design-log lock)
```

- Settings are split per environment; the active module is chosen explicitly (manage.py → development, pytest → testing, wsgi/asgi → production). Secrets come from env vars only — never committed, never pasted in chat.
- New domain logic gets a feature app when a card needs it (catalog, matching, proposals…), one app per bounded area — not one app per model.

## Inside an app

| File | Holds |
|---|---|
| `models.py` | Data + light state logic (properties, simple helpers). No business flows. |
| `services.py` | Business logic — plain functions, explicit keyword-only args, `full_clean()` before save, `transaction.atomic` around multi-write flows. |
| `selectors.py` | Data access / queries (reads). Views never filter querysets inline. |
| `forms.py` | Input validation only. No DB writes, no side effects. |
| `views.py` | Thin: parse request → validate with form → call service/selectors → render or redirect. HTMX endpoints return partial templates. |
| `tests/` | `test_<module>.py` mirroring the module under test; through public APIs only. |
| `admin.py` | Registration + list tuning; admin is acceptable UI in MVP. |

## Core rules

1. **Business logic lives in services** — never in views, forms, model save hooks, or signals. Signals may not carry business logic (money, matching, proposals).
2. **Selectors for every non-trivial query**; templates never query, template tags only format — never compute money.
3. **Models validate shape, services validate meaning.** Services call `instance.full_clean()` before persisting so constraints hold from any entry path (app, admin, shell, n8n).
4. **Money math only in the ROI engine** (pure Python, 95–100% covered). The LLM extracts and narrates; it never prices, computes, or claims skills. Banned-phrase filter always on.
5. **Type hints everywhere**; `_`-prefix for internal helpers; naming: `create_*/update_*` for write services, `get_*/list_*` for selectors.
6. **Tenancy-ready:** every top-level model carries `owner` FK (Q: single-user MVP, design log 2026-09-28). Protected personal characteristics do not exist in the schema.
7. **Estimates are labelled estimates** in every rendered surface.

## Testing (tiered per AGENTS.md)

- ROI engine / matching / LLM validation → **95–100%**
- Catalog & profile management → **80–85%**
- Templates & UI → **40–50% smoke** (view tests through public APIs, factory data, no live LLM)
- Smallest test that proves one behavior; delete implementation-coupled tests; fast and order-independent.

## Frontend posture

- **Tailwind CSS v4 via standalone CLI** (no npm, no node_modules — respects the no-frontend-build-pipeline lock; CLI pinned in `scripts/build_css.sh` and the Dockerfile `css` stage).
- Theme tokens (Q12 money green) live once, in `static/css/src/input.css` `@theme` — use utilities (`bg-dw-700`, `text-dw-muted`), never hardcoded hexes in templates.
- `static/css/app.css` is generated but committed: prod rebuilds it in Docker; dev can run `scripts/build_css.sh --watch`.
- Reusable small patterns go in `@layer components` (`.card`, `.btn-primary`, …); pages compose utilities. No page-specific CSS files.
- HTMX (Card 7) returns partial templates — same Tailwind rules apply.

## Settings & config

- All values env-driven via `django-environ`; `.env.example` documents keys; production settings fail fast on missing required env.
- No logic in settings files beyond composition.
- Dep additions beyond the locked minimal list get a backlog entry and Card 11 review.
