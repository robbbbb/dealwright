# Dealwright — backlog & open items

Registry of deferred work and open items. Status lines updated as items move. Design-stage residuals recorded 2026-09-28 at project creation.

## Pre-launch checklist (before first paying user)

- [ ] **Domain: buy `dealwright.io`** (available as of 2026-09-28; `.com`/`.app` parked — revisit later). Status: open.
- [ ] **Trademark check** — IPOPHL classes 9/35/42 at DTI/SEC business registration; USPTO only if international. Status: open.
- [ ] **Railway region selection** — closest to PH; decided at Card 11 deploy. Status: open.
- [ ] **Verify Railway Postgres backup policy per plan** — if insufficient, the n8n off-site pg_dump flow (system-design §9b) becomes mandatory, not stopgap. Status: open.
- [ ] **Pricing page + checkout** — tiers set (₱399/₱899/₱1,990, Q10 in design log); page mockup and billing integration are post-MVP. Status: deferred.
- [ ] **Marketing copy review** — implied-outcome lines need a copy/legal pass before launch, e.g. landing stats strip "1 client — won deal pays for the year" (figure-free but outcome-adjacent; flagged in landing review pass 1). Status: open.

## Card 0 residuals (2026-09-28)

- **whitenoise + gunicorn added** beyond the locked minimal-dep list — required for Railway static serving + prod WSGI; confirm/replace at Card 11 deploy. Status: open.
- **Transactional email/SMTP provider** — production sets `ACCOUNT_EMAIL_VERIFICATION=mandatory` (Q13); provider choice + env keys needed before email-dependent flows go live. Status: open.
- **Google OAuth credentials not provisioned** — social login is dormant until `GOOGLE_OAUTH_CLIENT_ID`/`GOOGLE_OAUTH_SECRET` env keys exist (allauth settings-APP form, no DB rows). Status: open.
- **Postgres-backed pytest verification pending** — no Docker daemon in the Card 0 build environment; tests used the sqlite fallback (`DATABASE_URL` honored when set). Run `docker compose up -d db` + `pytest` locally to close. Status: open.
- **Production `Site` row** — set the real domain (Sites framework) when the Railway URL exists (Card 11). Status: open.

- **Remote push pending** — `origin` set to `github.com/robbbbb/dealwright` but push failed: git credential helper references `/usr/bin/gh` (not installed) and repo returns "not found". Fix `gh` install/auth or create repo, then `git push -u origin main`. **Before first push:** reword the transposed commit subjects `5be13dc`↔`66affc8` (found in Card 0 review — each commit's message describes the other's content; content intact, repo unpushed so a rebase reword is safe while no other session is live). Status: open.
- **`production.py` env-source hygiene** (Card 0 review, minor) — ALLOWED_HOSTS/CSRF read via base `env` (.env-reading) alongside the strict `_prod_env`; functionally safe on Railway (`.dockerignore` excludes `.env`) but worth harmonizing to strict-only reads opportunistically. Status: open (hygiene).

- **Tailwind CLI pinned v4.1.13** (scripts/build_css.sh + Dockerfile ADD) — bump deliberately, verify visual smoke after bumps. Status: open (hygiene).
- **Committed generated `static/css/app.css`** — chosen so clone-and-run works with zero tooling; Docker rebuilds fresh at image build. Revisit if it causes noisy diffs. Status: note.
- **`docker compose up --build` not yet exercised end-to-end** — no Docker daemon in build environment; web service + Tailwind stage verified by construction only. Run locally to close (same as Postgres item above). Status: open.

## Auth implementation residuals (2026-09-29, Robb-directed between cards)

`docs/mockups/auth-mockup.html` implemented across allauth (login, signup, verify-email states, password reset, TOTP MFA + one-time recovery codes). Commits `9b89a06` / `d2c2e9b` / `3e37fee` / `c4fe1ed`, review fixes `4e6a81d`; dispatch + verdicts at `docs/reviews/auth-dispatch.md` (pass 1 CHANGES REQUIRED → blocking finding fixed → pass 2 pending). Residuals:

- **`django-allauth[mfa]` dep addition** — confirmed required as-is: `qrcode` renders the TOTP QR SVG and `fido2` is hard-imported by `allauth.mfa.stages` on the login path even with WebAuthn disabled (removing it breaks boot — verified 2026-09-29; `pyproject.toml` carries a warning comment). Confirm versions at Card 11 dep review. Status: resolved (documented); Card 11 review pending.
- **Google provider app now conditionally installed** with the credentials env keys — fixes a Card 0 gap: the provider was never registered without it, so social login could not have resolved even with credentials set. Status: fixed in `9b89a06`.
- **Verification-mode tension (adjudicate at next between-card window):** production sets `ACCOUNT_EMAIL_VERIFICATION=mandatory` (Card 0 backlog line) → unverified users cannot log in at all; the mockup frame-3 note says "providers can browse, but proposals can't send until verified", which implies `optional` + a `@verified_email_required` gate on send/share views (Card 8). No code changed mid-card; flag at Card 1 close. Status: open (decision needed).
- **Frame 3 deviation — no logged-out email change:** the mockup's "Wrong address? [input]" for signed-out users is intentionally not implemented (changing an account's email pre-verification is a classic account-takeover vector). Wrong-address copy routes back to signup; logged-in users use the styled email-manage page. Status: recorded (security-first deviation).
- **Resend-confirmation endpoint** is a new project surface (`POST /accounts/resend-confirmation/`): anti-enumeration copy, sends capped at 5/hour/address via Django cache (LocMem in dev — swap to a shared cache in prod if multi-process). Status: open (prod cache check at Card 11).
- **OTP 6-box presentation** is a dependency-free JS progressive enhancement over allauth's single `code` field; without JS the plain input remains fully functional. Untested by automation (smoke tier). Status: note.
- **MFA triggers not wired** (by design): "offered after first proposal send" (solo) and "required for Agency tier" enforcement belong to Cards 8–9. Status: deferred.
- **Non-branded edge pages** intentionally left on allauth's default layouts: reauthenticate (account + MFA), trust-device, social login error/cancel, signup-closed, password-set, login-by-code, email-confirm-code. Self-contained but not themed; style if pilots hit them. Status: deferred.
- **Google "G" button SVG** uses Google's own brand colors verbatim (third-party asset, not Dealwright tokens) — extracted to `templates/account/snippets/google_button.html`; recorded as a deliberate tokens-only exception. Status: recorded (accepted, review pass 1 minor).
- **Password-strength bars are decorative** (mockup shows a demo state; no live scoring) — post-MVP polish if wanted. Status: note (accepted, review pass 1 minor).
- **`ACCOUNT_RATE_LIMITS` untouched** — allauth defaults apply (login attempts, confirm-email cooldown). Revisit if pilot abuse appears. Status: note.

## Post-Card-0 additions (2026-09-28, between-card work at Robb's request)

- **Public landing page built** (`templates/landing.html` from `docs/mockups/landing-mockup.html`; `/` now serves it to anonymous visitors instead of redirecting to login). Canonical amber tokens added to `static/css/src/input.css` `@theme` (`dw-amber`, `dw-amber-bg` — theme.html values). Residuals:
  - Privacy/Terms footer links are `#` placeholders — real pages are pre-launch items, not in any card. Status: open.
  - "See a real proposal →" hero CTA points to signup until a public sample proposal surface exists. Status: open.
  - Pricing tiers displayed are the Q10 hypotheses (₱399/₱899/₱1,990 + Founding-20 banner); checkout/billing stays deferred per the pre-launch checklist line above. Status: note.
  - Built outside the card registry (user-directed between Card 0 review and Card 1) — smoke tests only, per the templates/UI tier. Review loop applied 2026-09-29 via `docs/reviews/landing-dispatch.md`: pass 1 CHANGES REQUIRED (generated CSS not reproducible from committed sources) → fixed in `86cac97` → pass 2 APPROVED (two fresh GLM-5.3 reviewer subagent passes). Status: approved & recorded.

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
