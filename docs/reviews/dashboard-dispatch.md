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
### Pass 1 verdict — APPROVED

All 7 gates green with real output; discipline claims independently verified (all five demo figures absent from visible text; placeholders honest; only real routes referenced; chip semantics correct; c7cb388 isolated from dashboard files).

```
Verdict: APPROVED
Blocking findings: None.
Minor findings: (1) smoke test omits "Integrations" from asserted sidebar items — disposition: acceptable, verified present in live render; suggest adding when Card 9 rewrites the test. (2) Demo-count absence asserted only for 62%/₱41k — disposition: acceptable, bare digits are unassertable against utility-class names in raw HTML; reviewer verified visible-text absence of all five demo figures independently.
Rationale: All 7 gates pass with real output; the diff (9d65123) matches the dispatch description exactly; mockup demo numbers provably do not render; nav/CTA placeholders are honest (Coming soon, aria-disabled, no fabricated routes — both {% url %} targets resolve); zero hardcoded hex in the new templates; core/views.py contains greeting/date presentation only; the committed smoke test genuinely asserts the discipline claims; adjacent commit c7cb388 touches no dashboard files; all six mockup deviations adjudicated as product-discipline-positive. Card 9 remains the wiring card per plan.
```

**Builder disposition (2026-09-29):** minor 1 → fixed immediately ("Integrations" added to the asserted sidebar items, tests green). Minor 2 → accepted (reviewer's visible-text verification recorded here). **Dashboard shell: approved & closed.** Card 9 wiring deferred per plan.

---

# Pass 2 — mobile hamburger drawer (Robb request, 2026-09-29)

**Scope:** `templates/app-base.html` rework — below `md` the sidebar is replaced by a compact top bar (hamburger + logo); the nav + who-block live in a JS-toggled drop-down drawer (single markup source; `hidden`↔`flex` toggle, `aria-expanded` drives the hamburger↔X swap via `group-aria-expanded` variants; Escape + outside-click close; `<noscript>` forces the drawer statically open so no-JS users keep full navigation). Desktop (md+) rendering unchanged. Test asserts the button + `aria-controls`. **For:** fresh GLM-5.3 reviewer (read-only, gates).

**Visual evidence (builder-verified):** closed `/tmp/dw-drawer-closed2.png`, open `/tmp/dw-drawer-open3.png` (solid dw-900 panel, sections, who-block below nav), desktop unchanged `/tmp/dw-dash-desktop2.png`. Reviewer may substitute DOM checks per pass-1 precedent.

**Gates:** same as pass 1 (pytest 25, ruff, check, CSS reproducible, live smoke, template hygiene incl. the inline script has no business logic, responsive classes: `max-md:absolute`, `group-aria-expanded:*`, `md:flex` on drawer present in compiled CSS).

**Adjudicate:** inline `<script>` + `<noscript>` fallback in the template (progressive-enhancement precedent: OTP boxes); drawer accessible name/aria pattern.

## Verdict (pass 2)
### Pass 2 verdict — CHANGES REQUIRED

Reviewer's pixel-diff of the builder's own desktop screenshots caught what the builder missed: the who-block lost its bottom pinning (drawer lacked `md:flex-1` as the aside's sole flex child), contradicting the card's "desktop unchanged" claim.

```
Verdict: CHANGES REQUIRED
Blocking findings: (1) Desktop who-block regression: the card's scope claim "Desktop (md+) rendering unchanged" is false. #dw-drawer ... lacks md:flex-1, so the nav's md:flex-1 no longer stretches and the who-block (name/email/logout) sits directly under "Settings" instead of pinned to the sidebar bottom. ... Fix is small: stretch the drawer at md (e.g. md:flex-1 ...), rebuild CSS, re-verify desktop + mobile screenshots, then fresh review pass.
Minor findings: (a) Desktop logo row dropped pass 1's md:pb-3 (4px nav offset) — fold into the same fix for exact parity. (b) No-JS: the hamburger button remains visible-but-inert ... consider hiding the button under noscript later. (c) <noscript><style> in <body> is technically non-conforming HTML though universally supported. (d) Escape-close does not return focus to the button — a11y polish. (e) New smoke assertions are markup-string-coupled ... acceptable.
Rationale: Five of six gates pass ... but adjudication item 3 fails against the pass-2 spec baseline ... CHANGES REQUIRED despite otherwise-green gates.
```

**Builder disposition (2026-09-29):** blocking 1 → fixed (`md:flex-1` on drawer; desktop screenshot re-verified — who-block bottom-pinned, mobile drawer unchanged). Minors a–d → fixed in the same commit (md:pb-3 parity; hamburger hidden via noscript; noscript moved to `<head>`; Escape returns focus). Minor e → accepted (smoke tier, per card intent).

## Pass 3 — fresh reviewer on the fix
### Pass 3 verdict — APPROVED

Fix commit verified exact (app-base + app.css only, all four expected changes); desktop stretch chain verifiably unbroken (wrapper min-h-screen → aside md:flex-col → drawer md:flex-1 → nav md:flex-1 → who-block last child); gates green; CSS proven byte-reproducible at the fix commit in a detached worktree (the apparent in-repo drift was Robb's concurrent `max-w-[1200px]` removal, root-caused).

```
Verdict: APPROVED
Blocking findings: None.
Minor findings: (1) Escape handler calls btn.focus() unconditionally — on mobile, pressing Escape anywhere pulls focus to the menu button; a hidden guard would scope it. Harmless — acceptable, suggest folding into a future UI card. (2) Robb's concurrent uncommitted edit (max-w-[1200px] removed from <main>) — app.css will need a rebuild when it lands. (3) Pass-2 minor e remains accepted.
Rationale: Fix commit 7b83759 matches the pass-2 remediation exactly ... [full rationale in review transcript]
```

**Builder disposition (2026-09-29):** minor 1 → accepted (future UI card). Minor 2 → Robb's edit committed verbatim right after this verdict with CSS rebuilt (prunes `max-w-[1200px]`). **Mobile drawer: approved & closed.**

---

# Pass 4 — avatar account menu (Robb request, 2026-09-29)

**Scope:** desktop logout moves out of the sidebar into an avatar dropdown (dashboard.html: `dw-user-btn` + `dw-user-menu` with name/email/Log out); below md the drawer keeps its logout and the desktop avatar degrades to a static badge. Sidebar who-block logout is `md:hidden`. The two menus share one generic JS handler (open-one-closes-other, Escape w/ focus return, outside-click); noscript hides both buttons and forces the who-block logout visible (no-JS users can always sign out at every width). Tests: dashboard smoke asserts user-menu markers + both logout surfaces; MFA flow logout-count 1 → 2. **For:** fresh GLM-5.3 reviewer (gates only).

**Visual evidence (builder-verified):** desktop menu open `/tmp/dw-usermenu-open.png`, mobile drawer with logout `/tmp/dw-drawer-final.png`. DOM checks may substitute per precedent.

**Gates:** pass-1 set + adjudicate: generic handler has no business logic; noscript coverage (drawer open, buttons hidden, who-logout forced) leaves no-JS logout reachable at every width; `{% url %}` targets resolve; zero hex; CSS reproducible.

## Verdict (pass 4)
### Pass 4 verdict — APPROVED

All gates green; commit matches scope exactly (5 files); all six adjudications verified against live DOM. Generalized handler confirmed pure presentation (open-one-closes-other, aria, Escape/focus, outside-click); no-JS logout reachable at every width; logout count genuinely 2; stretch chain unbroken.

```
Verdict: APPROVED
Blocking findings: None.
Minor findings: (1) Desktop no-JS: the .relative.hidden.md:block avatar wrapper stays in flow as an empty box — cosmetic; noscript collapse = future UI card polish. (2) count("Log out") == 2 assertions are markup-coupled — accepted at smoke tier per precedent. (3) Robb's uncommitted landing-mockup edit (□→✓ glyph) — flagged so it isn't lost. (4) Positive: generalized handler incidentally fixes pass-3 minor 1 (Escape no longer focuses a never-open menu's button).
Rationale: All gates pass with real pasted output; all six pass-4 adjudications verified against the live-rendered DOM and template source — logout placement per directive on both breakpoints, generalized handler correct, no-JS logout reachable at every width, logout count genuinely 2, zero hardcoded hex, CSS byte-reproducible, stretch chain unbroken.
```

**Builder disposition (2026-09-29):** minor 1 → accepted (future UI card). Minor 2 → accepted. Minor 3 → offered to Robb: committing the mockup glyph flip syncs it with the live page (already shipped) and partially closes the backlog mockup-sync residual. Minor 4 → noted. **Avatar account menu: approved & closed.**

---

# Pass 5 — identity de-duplication (Robb request, 2026-09-29)

**Scope:** sidebar who-block (`#dw-who`) hidden at md+ (avatar menu covers identity+logout on desktop; it remains the mobile drawer's footer); the mobile static avatar badge removed from the greeting row. Noscript extended: `#dw-who` forced visible so no-JS desktop keeps a logout path. **For:** fresh GLM-5.3 reviewer (gates only).

**Gates:** pass-1 set + confirm: who-block has md:hidden + id dw-who; badge div gone; noscript includes #dw-who rule; stretch chain still intact (drawer md:flex-1 → nav md:flex-1, who-block still drawer's last child); logout count == 2 in HTML (drawer form + avatar-menu form); no hex.

**Visual evidence (builder-verified):** desktop `/tmp/dw-who-desktop.png` (sidebar ends at Settings, avatar top-right), mobile drawer `/tmp/dw-who-mobile.png` (who-block + logout present). DOM checks may substitute.

## Verdict (pass 5)
### Pass 5 verdict — APPROVED

Feature commit `73cbeb9` matches scope exactly (who-block → `#dw-who` + `md:hidden`; badge removed; app.css correctly not in commit — rebuild was a no-op since `md:hidden` was already compiled). Stretch chain verified intact in source, compiled CSS, and live DOM; no-JS logout reachable at every width (noscript ID+important rules provably defeat the class rules); gates all green.

```
Verdict: APPROVED
Blocking findings: None.
Minor findings: (1) md:hidden on #dw-who-logout form itself is now redundant (parent already md:hidden) — one-token cleanup for a future card, zero behavioral impact. (2) app.css absent from commit — correct, recorded to preempt confusion. (3) Screenshots exist; DOM checks substituted (model limitation). (4) Robb's landing-mockup glyph edit still pending (re-flagged).
Rationale: All gates pass with real pasted output ... Robb's de-duplication directive is implemented as specified on both breakpoints.
```

**Builder disposition (2026-09-29):** minor 1 → accepted (future-card cleanup). Minors 2–3 → noted. Minor 4 → with Robb. **Pass 5: approved & closed.**
