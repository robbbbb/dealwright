# Review dispatch — Card 0: Scaffold

**For:** fresh GLM-5.3 reviewer (read-only — run gates, edit nothing). Seed a fresh session with this file + repo root `/home/robbb/dealwright`.
**Builder:** builder session 2026-09-28 (GLM-5.3 Flash). **Scope:** everything between commit `895d0e6` ("Add integration spec for z.ai GLM models and n8n workflow" — pre-card baseline) and the review-request commit on `main`.

## Spec baseline

- `docs/design/mvp-build-plan.md` → Card 0 definition (goal, tasks, TDD anchors, done-when)
- `AGENTS.md` (+ `~/.zcode/AGENTS.md` defaults) — rules of engagement, delivery discipline
- `docs/styleguide.md` — HackSoft adaptation, adopted this card
- `docs/design/system-design.md` — Railway deploy posture

## Gates (run all; paste real output into findings)

1. `python3 -m uv sync --frozen` — lockfile installs clean
2. `.venv/bin/python -m pytest` — expect **3 passed** (anchors: `test_login_page_renders`, `test_settings_read_env`, plus `test_home_redirects_anonymous_to_login`)
3. `.venv/bin/python manage.py check` — no issues
4. `.venv/bin/python manage.py migrate` — no pending migrations (sqlite fallback OK if no Docker)
5. `.venv/bin/python -m ruff check .` — clean
6. Live smoke: `runserver` → GET `/` → 302 → `/accounts/login/`; GET `/accounts/login/` → 200 containing "Sign in"
7. Secret scan: no real secret values in any committed file; `.env` gitignored; only `.env.example` present

## Card 0 checklist (adjudicate each)

- [ ] Project + `core` app, HackSoft-style split settings (`base/development/testing/production`), env-driven
- [ ] Login/logout functional via django-allauth (Q13: email method, no usernames; Google dormant without env keys)
- [ ] Base template + minimal CSS using canonical money-green tokens (`docs/mockups/theme.html`)
- [ ] `docs/backlog.md` + design docs committed (registry intact)
- [ ] pytest wired, both TDD anchors present and meaningful
- [ ] **Dockerfile + railway.toml from day one**; local Postgres via `compose.yaml`
- [ ] Conventional commits, one logical change each

## Known deviations to adjudicate (each has a backlog entry)

1. `whitenoise` + `gunicorn` added beyond the locked minimal-dep list (static serving + prod WSGI on Railway).
2. Tests fall back to in-memory sqlite when `DATABASE_URL` is unset (no Docker daemon in builder env) — Postgres-backed run still pending on Robb's machine.
3. Django 6.1 `MAILERS` form used instead of deprecated `EMAIL_*` settings.
4. `TIME_ZONE = "Asia/Manila"` (PH-anchored product) — not previously locked.
5. Production `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` vs base/dev `"optional"` (Q13 gate implemented at env level; send/share gating still lands with proposal cards).

5. Project package is `config/` (settings/urls/wsgi/asgi) — renamed from `dealwright/` at Robb's request to flatten the double-folder nesting; equally mainstream (cookiecutter-django style), deviation noted for the record.

5. Project package is `config/` (settings/urls/wsgi/asgi) — renamed from `dealwright/` at Robb's request to flatten the double-folder nesting; equally mainstream (cookiecutter-django style), deviation noted for the record.
6. Tailwind CSS v4 via standalone CLI (no npm), added at Robb's request: `static/css/src/input.css` with Q12 theme tokens, generated `app.css` committed, CSS build stage in Dockerfile, dev `web` service in compose.yaml.

## Verdict format

```
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings: <list or none>
Minor findings: <list or none>
Rationale: <one line>
```

Record the verdict below under **Verdict (reviewer)** and mirror the disposition in `docs/design/mvp-build-plan.md` (Card 0 status). Blocking findings → builder fixes → fresh reviewer pass. Merge gate applies.

---

## Verdict (reviewer)

_Pending — no reviewer subagent available in builder session; committed for Robb to run in a fresh session._
