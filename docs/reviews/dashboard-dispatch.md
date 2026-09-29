# Dispatch — Dashboard shell (Robb-directed between cards, 2026-09-29)

**Scope:** commit `9d65123` (+ Robb's landing-caption revert `c7cb388` committed adjacent — out of scope except noting it doesn't touch dashboard files). **For:** fresh GLM-5.3 reviewer (read-only, run gates). Seed with repo root `/home/robbb/dealwright`.

**What was built:** signed-in app shell + dashboard per `docs/mockups/dashboard-mockup.html` — `templates/app-base.html` (sidebar: Work/Setup sections, active state via `request.resolver_match.url_name`, who-block with logout), `templates/dashboard.html` (time-based greeting + first name + date, disabled CTAs, 5 stat cards, panels with empty states, estimate-discipline footer), `templates/home.html` removed, `core.views.home` renders the dashboard with greeting context, smoke test rewritten (`test_signed_in_users_get_dashboard`).

**Product-discipline intent (adjudicate):** counts are honest zeros/`—`; mockup demo numbers (12/5/8/62%/₱41k) must NOT appear — the test asserts their absence; nav items + "New client"/"New discovery session" are disabled placeholders (`title="Coming soon"`, no fabricated routes); no "View all" links until list pages exist; solo-mode footer sentence deferred (no persona data yet). Card 9 stays the wiring card — no models touched.

**Gates:**
1. `.venv/bin/python -m pytest` — expect **25 passed**
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — clean
4. `bash scripts/build_css.sh` + `git diff --stat static/css/app.css` — empty
5. Live smoke: `/` anonymous → landing 200; signed-in content via the tests (or a throwaway `django.test.Client` script: force_login → GET `/` → assert "Good ", "Robb", "No discovery sessions yet", "never guarantees", logout URL; assert "62%" and "₱41k" absent)
6. Template hygiene: zero hardcoded hex in `templates/app-base.html` + `templates/dashboard.html`; no business logic in view beyond greeting/date presentation
7. Responsive classes present in compiled CSS: `md:flex-row` (shell), `overflow-x-auto` (mobile nav strip), `lg:flex-row` + `lg:max-w-[340px]` (columns)

**Visual evidence:** builder verified screenshots at 1440px (`/tmp/dw-dash.png`) and 390px (`/tmp/dw-dash-m.png`) — sidebar/greeting/stats/panels match the mockup; reviewer may substitute DOM/content checks per the pass-2 precedent if its model cannot render images.

**Deviations from mockup to adjudicate:** counts omitted-vs-badge (no `cnt` pills), no "View all" links, CTAs disabled with tooltips, who-block shows name+email (no plan line), logout added (mockup lacks it), caption-free hero on landing per Robb's revert.

## Verdict (pass 1)
