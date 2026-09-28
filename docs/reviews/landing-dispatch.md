# Review dispatch — Post-Card-0 addition: public landing page

**For:** fresh GLM-5.3 reviewer (read-only — run gates, edit nothing). Seed a fresh session with this file + repo root `/home/robbb/dealwright`.
**Builder:** builder session 2026-09-29 (pi coding session, Robb-directed). **Scope:** commit `d54f79b` ("feat: public landing page at / for anonymous visitors") on `main`. Commit `7225005` (compose file rename) is mechanical — verify only that it is content-identical (`git show 7225005 --stat` → 100% rename) and skip deeper review.

## Scope summary

`docs/mockups/landing-mockup.html` (committed design) translated into the Django app: `templates/landing.html`; `core.views.home` now renders the landing for anonymous visitors (was: redirect to login) and keeps `home.html` for signed-in users; canonical amber chip tokens (`dw-amber` `#9A6B13`, `dw-amber-bg` `#FDF3E2`) added to `static/css/src/input.css` `@theme`; `static/css/app.css` rebuilt; home-view smoke tests moved from `test_smoke.py` to new `core/tests/test_views.py`; residuals recorded in `docs/backlog.md` ("Post-Card-0 additions").

## Spec baseline

- `docs/mockups/landing-mockup.html` — content/structure source of truth for the page
- `docs/mockups/theme.html` — canonical tokens; chip semantics are product rules (green = verified/accepted, amber = "estimate" always, gold = premium only, red = gaps/errors)
- `AGENTS.md` + `~/.zcode/AGENTS.md` — rules of engagement, estimate discipline, review loop
- `docs/styleguide.md` — thin views, presentation-only templates, Tailwind v4 utilities + `@layer components`, smoke-tier UI tests
- `docs/design/design-log.md` — Q10 pricing tiers (₱399/₱899/₱1,990), rule 5: every client-facing figure traces to a stored field; estimates labelled estimates

## Gates (run all; paste real output into findings)

1. `.venv/bin/python -m pytest` — expect **4 passed** (`test_login_page_renders`, `test_settings_read_env`, `test_landing_renders_for_anonymous`, `test_signed_in_users_get_app_home`)
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — no issues
4. `scripts/build_css.sh` then `git diff --stat static/css/app.css` — rebuild is reproducible (no diff)
5. Live smoke (anonymous): `runserver` → GET `/` → 200 containing "Turn discovery calls into" and the footer disclaimer "estimates derived from stated assumptions"; GET `/accounts/login/` → 200; GET `/static/css/app.css` → 200
6. Rendered-HTML check: `/` contains links to `/accounts/signup/` and `/accounts/login/`; amber estimate chips present (`bg-dw-amber-bg`)
7. Template hygiene: `templates/landing.html` contains no hardcoded hex colors (token classes only) and no business logic; `core/views.py` home stays thin
8. Secret scan: no real secret values committed

## Checklist (adjudicate each)

- [ ] Page structure faithful to `landing-mockup.html` (hero + demo card, stats, old-vs-new, how-it-works, features, pricing, founding-20 banner, FAQ, compliance footer)
- [ ] Chip semantics respected: amber only for estimate/follow-up chips; green checkmarks; no gold on body text; no red misuse
- [ ] Estimate discipline: every money figure is either labelled ("≈ ₱8,700/mo **est**"), Dealwright's own pricing (₱399/₱899/₱1,990, ₱299 founding), a platform cost stat (₱0.52 AI cost), or covered by the footer estimate disclaimer — is any figure an unlabeled client-outcome claim?
- [ ] Landing copy makes no guaranteed-outcome claims ("guarantee" appears only inside FAQ answers that disclaim it)
- [ ] All CTAs resolve to real routes (no `docs/` mockup links, no dead marketing routes besides adjudicated `#` placeholders below)
- [ ] Tests: through public APIs only, smoke tier (40–50%), obsolete redirect test removed, no implementation-coupled assertions
- [ ] `@source` coverage: new template classes present in committed `app.css`
- [ ] Backlog residuals recorded ("Post-Card-0 additions" section)

## Known deviations to adjudicate (each intentional; backlog has the section)

1. **Between-card work** — built outside the card registry at Robb's direct request, between Card 0 review and Card 1; smoke-tier tests only; this dispatch substitutes for a per-card review.
2. Privacy/Terms footer links are `#` placeholders (pre-launch pages, no card owns them).
3. "See a real proposal →" hero CTA points to signup (no public sample-proposal surface exists; mockup linked to a docs file, wrong for prod).
4. Hero accent uses `text-dw-100` instead of the mockup's `#7FD8AC` (non-canonical hex avoided; tokens only).
5. Founding-20 banner text is `text-dw-ink` instead of the mockup's dark-gold body text (theme rule: gold is premium accent, never body text).
6. Demo textarea shows the raw LF "FEMALE PERSONAL ASSISTANT" sample — client input illustration; protected-characteristic compliance flags are an in-app pipeline feature (design log), not a landing feature. Acceptable?

## Verdict format

```
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings: <list or none>
Minor findings: <list or none>
Rationale: <one line>
```

Record the verdict below under **Verdict (reviewer)** and mirror the disposition in `docs/backlog.md` ("Post-Card-0 additions"). Blocking findings → builder fixes → fresh reviewer pass.

---

## Verdict (reviewer)

### Pass 1 (scope: `d54f79b`) — CHANGES REQUIRED

```
Verdict: CHANGES REQUIRED
Blocking findings: Gate 4 — committed static/css/app.css (f766f19d, 24811 B) is not reproducible from committed sources (deterministic rebuild yields f378ad0, 24355 B; ~456 B of stale unused theme vars from an intermediate template state). Fix: run scripts/build_css.sh and commit the refreshed artifact, then fresh reviewer pass on that commit.
Minor findings: demo-card secondary proposal link dropped vs mockup (consistent with deviation 3); "won deal pays for the year" implied-outcome copy (figure-free, mockup-baseline — revisit at pre-launch copy review); benign staticfiles UserWarning in test runs.
Rationale: All functional gates and checklist items pass and the page is faithful, disciplined, and token-clean — but the CSS-rebuild reproducibility gate fails as specified, and the committed generated artifact must match its sources.
```

All 8 checklist items passed; all 6 deviations adjudicated acceptable; gates 1–3, 5–8 passed.

**Builder disposition (2026-09-29):**
- Blocking finding → fixed in `86cac97` (`scripts/build_css.sh` from committed sources; utilities layer class-for-class identical; rebuild against HEAD now zero-diff; pytest 4/4, ruff, `manage.py check` re-run green).
- Minor: demo-card secondary link dropped → **accepted**, consistent with adjudicated deviation 3 (no public proposal surface; no `docs/` links in prod). No action.
- Minor: "won deal pays for the year" implied-outcome copy → **actioned**: pre-launch checklist line added to `docs/backlog.md` (marketing copy review before launch). Copy unchanged now (mockup baseline, figure-free).
- Minor: staticfiles UserWarning → **accepted**, pre-existing since Card 0 (no `collectstatic` in dev/test trees). No action.
- Fresh reviewer pass 2 on `86cac97` follows below.

### Pass 2 (scope: `86cac97`, fix verification)

_Pending — fresh reviewer pass in flight._
