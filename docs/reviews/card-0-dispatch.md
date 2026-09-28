# Review dispatch — Card 0: Scaffold

**For:** fresh GLM-5.3 reviewer (read-only — run gates, edit nothing). Seed a fresh session with this file + repo root `/home/robbb/dealwright`.
**Builder:** builder session 2026-09-28 (GLM-5.3 Flash). **Scope:** everything between commit `d1376c8` (effective baseline in this repo — the originally cited `895d0e6` is from the design-stage repo and does not resolve here; corrected at verdict recording per reviewer finding) and the review-request commit `b8ff974` on `main`; adjudicated against HEAD with documented supersessions (`docs/reviews/landing-dispatch.md` APPROVED; `config/` flatten `854c700`; mechanical compose rename `7225005`).

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

### Card 0 review (run 2026-09-29, fresh GLM-5.3 reviewer subagent at HEAD `63ef3f3`) — APPROVED

All 7 gates passed with real output (incl. live end-to-end login→logout flow on a throwaway DB); all 7 checklist items PASS; all 7 listed deviations + the uvicorn deferral adjudicated acceptable. Full evidence in the reviewer session log; highlights: `uv sync --frozen` exit 0 with lockfile untouched; pytest exactly the 4 superseded test IDs; migrate clean; byte-size match on the landing-pass-2-verified CSS artifact; secret scan clean (`POSTGRES_PASSWORD: dealwright` is the documented local-only compose placeholder).

```
Verdict: APPROVED
Blocking findings: none
Minor findings: (1) commit subjects transposed between 5be13dc and 66affc8 — reword before first push; (2) dispatch card cites baseline 895d0e6 which is absent from repo history (effective baseline d1376c8) — fix line when recording verdict; (3) production.py mixes strict _prod_env and .env-reading base env for ALLOWED_HOSTS/CSRF — harmonize opportunistically; (4) uvicorn docs/code mismatch deferral to Card 11 acceptable — add "(planned, not yet in Dockerfile)" qualifier until then; (5) staticfiles UserWarning in tests — pre-existing, accepted; Postgres-backed test run + compose --build still to be closed on Robb's machine per backlog
Rationale: All 7 gates pass with real output at HEAD under the documented supersessions; scaffold matches spec baseline (env-driven split settings, working allauth email login, verbatim Q12 tokens, registries committed, Dockerfile/railway/compose from day one, both TDD anchors); all 7 deviations and the uvicorn deferral are recorded, verified, and acceptable.
```

**Builder dispositions (2026-09-29):**
1. Transposed commit subjects `5be13dc`/`66affc8` → **deferred to pre-push**: history reword is safe only while unpushed; the concurrency incident note (backlog) says another session may be live, so reword rides the already-open "Remote push pending" item, recorded there. No rewrite now.
2. Baseline hash → **actioned now**: scope line corrected above.
3. `production.py` env mixing → **actioned now**: backlog hygiene line added (opportunistic fix).
4. uvicorn qualifier → **actioned now**: "(planned, not yet in Dockerfile)" added to the system-design ladder line.
5. staticfiles UserWarning → **accepted**, pre-existing (also dispositioned in landing review pass 1); disappears with a dev `collectstatic`.
6. (Trivia riders) `importlib.reload` in the settings test and absent teal `@theme` tokens → **accepted**; teal gets added when the first teal chip lands on a built screen.

**Merge gate satisfied. Card 0 review loop closed 2026-09-29 — Card 1 unblocked.**
