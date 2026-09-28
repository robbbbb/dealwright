# Dealwright — backlog & open items

Registry of deferred work and open items. Status lines updated as items move. Design-stage residuals recorded 2026-09-28 at project creation.

## Pre-launch checklist (before first paying user)

- [ ] **Domain: buy `dealwright.io`** (available as of 2026-09-28; `.com`/`.app` parked — revisit later). Status: open.
- [ ] **Trademark check** — IPOPHL classes 9/35/42 at DTI/SEC business registration; USPTO only if international. Status: open.
- [ ] **Railway region selection** — closest to PH; decided at Card 11 deploy. Status: open.
- [ ] **Verify Railway Postgres backup policy per plan** — if insufficient, the n8n off-site pg_dump flow (system-design §9b) becomes mandatory, not stopgap. Status: open.
- [ ] **Pricing page + checkout** — tiers set (₱399/₱899/₱1,990, Q10 in design log); page mockup and billing integration are post-MVP. Status: deferred.

## Card 0 residuals (2026-09-28)

- **whitenoise + gunicorn added** beyond the locked minimal-dep list — required for Railway static serving + prod WSGI; confirm/replace at Card 11 deploy. Status: open.
- **Transactional email/SMTP provider** — production sets `ACCOUNT_EMAIL_VERIFICATION=mandatory` (Q13); provider choice + env keys needed before email-dependent flows go live. Status: open.
- **Google OAuth credentials not provisioned** — social login is dormant until `GOOGLE_OAUTH_CLIENT_ID`/`GOOGLE_OAUTH_SECRET` env keys exist (allauth settings-APP form, no DB rows). Status: open.
- **Postgres-backed pytest verification pending** — no Docker daemon in the Card 0 build environment; tests used the sqlite fallback (`DATABASE_URL` honored when set). Run `docker compose up -d db` + `pytest` locally to close. Status: open.
- **Production `Site` row** — set the real domain (Sites framework) when the Railway URL exists (Card 11). Status: open.

- **Remote push pending** — `origin` set to `github.com/robbbbb/dealwright` but push failed: git credential helper references `/usr/bin/gh` (not installed) and repo returns "not found". Fix `gh` install/auth or create repo, then `git push -u origin main`. Status: open.

- **Tailwind CLI pinned v4.1.13** (scripts/build_css.sh + Dockerfile ADD) — bump deliberately, verify visual smoke after bumps. Status: open (hygiene).
- **Committed generated `static/css/app.css`** — chosen so clone-and-run works with zero tooling; Docker rebuilds fresh at image build. Revisit if it causes noisy diffs. Status: note.
- **`docker compose up --build` not yet exercised end-to-end** — no Docker daemon in build environment; web service + Tailwind stage verified by construction only. Run locally to close (same as Postgres item above). Status: open.

## Concurrency incident (2026-09-28, note for review)

- A parallel session committed `aa67d42` while the builder session had uncommitted Tailwind work; that commit mixed the builder's files (Dockerfile css stage, compose web, templates, scripts, generated css) under a `docs(system-design)` message. Content is intact; history not rewritten (nothing pushed, other session may be live). **Rule reminder: one card per fresh session — one writer session per repo at a time; never `git add -A` in a shared tree.** Status: recorded.
- **Docs/code mismatch from `aa67d42`:** system-design.md now says Card 0 deploys `gunicorn -k uvicorn.workers.UvicornWorker`, but Dockerfile/railway.toml still run the plain sync WSGI worker and `uvicorn` is not a dependency. Decide at Card 11: either add uvicorn + flip the worker, or revert the doc line. Status: open.

## Post-pilot / deferred product work

- Quality-mode toggle (Fast = Flash-writes ₱0.10 vs Premium = GLM-5.3 ₱0.52) — decide from pilot usage data. Status: deferred.
- Prompt caching of static blocks (catalog digest, guardrails) — −80% writer input cost. Status: deferred.
- Background worker service (huey/redis) for extraction + PDF — trigger: visible queueing or RAM >70%. Seam designed (system-design §6). Status: deferred.
- USD pricing tiers ($8/$18/$39) + currency-per-account when going international. Status: deferred.
- i18n: EN-only for MVP; PH bilingual catalog revisit. Status: deferred.
- Django-build pricing (catalog cat. 7) unvalidated — pilot before posting fixed prices, else "custom quote only". Status: open.
- Map each catalog service to a default n8n workflow template. Status: deferred.
- Solo provider public profile page (lead-gen) — parked. Status: out of MVP scope.
- n8n-hosted backup orchestration flow (nightly pg_dump push off-site + failure alert). Status: deferred (stopgap runbook in Card 11).

## Out of scope (per handoff; do not build)

Live call transcription · automated interviews · marketplace payments · public job board · mobile apps · complex AI ranking / autonomous hiring · multi-agent workflows · automatic proposal sending without human review · advanced analytics · billing/subscriptions in MVP.
