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

### Pass 2 (scope: `86cac97`, fix verification) — APPROVED

```
Verdict: APPROVED
Blocking findings: none
Minor findings: none new — pass-1 minors carry recorded dispositions (two accepted/no-action, one actioned in docs/backlog.md pre-launch checklist); staticfiles UserWarning remains as accepted pre-existing noise
Rationale: Gate 4 now passes byte-exactly (rebuild of scripts/build_css.sh against HEAD is zero-diff), the fix commit 86cac97 contains only the CSS artifact rebuild with a byte-identical utilities layer, and all other gates (pytest 4/4, ruff, manage.py check, amber utilities + footer disclaimer in committed artifacts) hold on HEAD with dispositions consistent between card and backlog.
```

Reviewer independently verified: fix commit touches only the CSS artifact; utilities layer byte-identical (13,266 B both blobs); rebuild against HEAD zero-diff; pytest 4/4 with expected test IDs; ruff and `manage.py check` clean; amber token values and footer estimate disclaimer present in committed artifacts; card↔backlog dispositions consistent.

**Final disposition: APPROVED — merge gate satisfied. Review loop closed 2026-09-29.**

---

# Rebuild — landing v2 (Robb's mockup rewrite, 2026-09-29) — pass 1

**Scope:** commits `71ea1f6` (Robb's v2 mockup — the spec baseline, his own rewrite) and `a75e11c` (landing.html rebuild + brand SVGs to static/brand/ + smoke-test update). **For:** fresh GLM-5.3 reviewer (read-only, run gates). Seed with repo root `/home/robbb/dealwright`.

**Spec baseline:** `docs/mockups/landing-mockup.html` **at `71ea1f6`** (Robb's v2 — NOT the v1 reviewed in passes 1–2 above; v1 sections — old/new comparison, textarea demo, ₱0.52 stat — are intentionally gone). Theme rules: `AGENTS.md` design system + `docs/mockups/theme.html` (chip semantics; tokens only). Robb's directive: "update the landing page… refer in the landing page mockup. make it responsive to all media size."

**Gates:**
1. `.venv/bin/python -m pytest` — expect **25 passed** (landing test updated for v2 headline + pricing markers)
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — clean
4. `bash scripts/build_css.sh` + `git diff --stat static/css/app.css` — reproducible
5. Live smoke: `/` → 200 with "From messy call notes", "One input. Four decisions", "Why clients trust", "MOST CHOSEN", "Founding 20", "Fair questions", amber/red chip classes present, "Protected preference excluded" twice (note + chip); `/static/brand/logo-horizontal.svg` + `-light.svg` → 200
6. Template hygiene: zero hardcoded hex in `templates/landing.html`; tokens only; no business logic
7. Responsiveness audit: every mockup breakpoint (1050/760/470) has a Tailwind counterpart — nav links hidden <md; hero/pipeline/trust/plans stack; pipeline arrow rotates on mobile; outputs 2-col mobile; workflow arrows at lg+; 44px touch targets

**Checklist:**
- [ ] Section-for-section fidelity to the v2 mockup (nav, hero+pipeline, value strip, workflow, trust/paper, mid CTA, pricing+Founding-20, FAQ, footer disclaimer)
- [ ] Chip semantics: amber = estimate only, red = protected-preference exclusion/errors, green = verified/client-ready, teal = source refs
- [ ] Estimate discipline: ₱8,700 labelled estimate everywhere it appears; pricing figures are Dealwright's own (Q10); footer disclaimer present
- [ ] No hardcoded hexes; brand SVGs served from static/brand/
- [ ] Tests smoke-tier through public APIs, updated for v2 markers

**Known deviations to adjudicate:**
1. "View example proposal" CTA points to signup (no public proposal surface — same as v1 deviation 3).
2. Privacy/Terms footer links remain `#` (pre-launch, unchanged from v1).
3. Investment box on the proposal paper stays visible at ≤470px (mockup hides it) — it flows below the summary instead; estimate chip still present. Builder judges hiding the price worse than the mockup's space saving.
4. "Win one client and it's paid for the year" headline retained (mockup-baseline; already on the pre-launch marketing-copy review line in backlog).
5. Workflow arrows appear only at lg+ (mockup shows them ≤1050 except card 2) — simplification, no content loss.

## Verdict (pass 1)
### Pass 1 verdict — APPROVED

All 7 gates green with evidence (25 passed, ruff/check clean, CSS byte-reproducible, full live smoke incl. Protected-preference ×2 + both brand SVGs, zero hexes, every breakpoint class verified in committed app.css). Section-for-section faithful to the v2 mockup; all 5 deviations adjudicated acceptable.

```
Verdict: APPROVED
Blocking findings: none
Minor findings: hero CTAs wrap instead of stacking full-width at ≤470px (mockup stacks); desktop workflow arrow between cards 1–2 absent vs mockup's three arrows; 760px mockup breakpoint maps to sm(640)/md(768) steps (640–768px band: plans 3-col, nav links from 768px) — all cosmetic, no estimate-discipline, chip-semantics, or token impact
Rationale: All 7 gates pass with pasted evidence (pytest 25/25, ruff and manage.py check clean, byte-reproducible CSS rebuild, full live-smoke markers incl. Protected-preference ×2 and both brand SVGs, zero hardcoded hexes, every mockup breakpoint verified present in the committed CSS), the page is section-for-section faithful to the 71ea1f6 v2 mockup, and all 5 deviations are adjudicated acceptable with backlog backing.
```

**Builder disposition (2026-09-29):** minors 1–2 → fixed in the follow-up commit (hero CTAs stack at ≤470px; 1→2 arrow restored at lg). Minor 3 → accepted (standard Tailwind steps; exact arbitrary variants used where the mockup demanded 420/470). **Landing v2: approved & closed.**

---

# Pass 2 — pipeline declutter (Robb visual feedback, 2026-09-29)

**Trigger:** Robb reviewed the live render (headless-Chromium screenshots at 390/768/1440, which the builder can now capture and view) and judged the hero pipeline cards too small and cluttered — the v2 mockup's 4-across print miniature with 8–9px type reads as noise on real screens; the ROI card's "Assumptions shown" chip overlapped its list.

**Scope:** commit `4daccff` — hero pipeline only: outputs 2×2 at ≥440px (1-col below), type up one to two steps throughout the notes + output cards, padding/min-height fixes. Plus `docs/backlog.md` residual recording the mockup/live divergence. **Evidence screenshots (pre-fix):** `/tmp/dw-desktop.png`, `/tmp/dw-mobile.png`. **Post-fix:** `/tmp/dw-desktop2.png`, `/tmp/dw-mobile2.png` — reviewer should view these image files (read tool supports PNG).

**Gates:** same 7 as pass 1 (pytest 25, ruff, check, CSS reproducible, live smoke, template hygiene, responsive classes). **Checklist:** pass-1 checklist still holds; additionally confirm no regression outside the hero pipeline and that estimate/chip discipline survived the type-size changes.

**Deviation to adjudicate:** outputs grid no longer matches the v2 mockup (mockup: 4-across micro; live: 2×2 legible). Mockup sync recorded as backlog residual — treat live page as canonical for the hero.

## Verdict (pass 2)
