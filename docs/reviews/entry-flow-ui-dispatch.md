# Dispatch — entry-flow UI cohesion: landing → auth → dashboard (2026-09-30)

**Scope:** commit `049fa5d` on baseline `74de0f8`. **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## Objective

Make the public landing page, account handoff, signed-in shell, and empty-state dashboard feel like one coherent Dealwright experience without inventing product data or implementing unfinished cards.

## What changed

- **Landing (`/`)**: retained the reviewed content structure while refining the hero width, depth, CTA contrast, focus navigation, and anchored scrolling. “View example proposal” now scrolls to the real proposal preview instead of incorrectly opening signup. Placeholder Privacy/Terms links are no longer fake `#` links.
- **Authentication (`/accounts/*`)**: replaced the isolated centered card on desktop with a branded split layout that carries Dealwright’s traceability promise through login, signup, recovery, verification, social-account, and MFA templates. Mobile retains a compact single-card version with the real logo asset.
- **App shell**: introduced a consistent desktop utility bar and account menu on every signed-in page, changed the sidebar to the canonical jade gradient, replaced mixed emoji navigation with monochrome inline SVGs, and rendered unfinished destinations as honest disabled items instead of fake links. Mobile drawer behavior and no-JS logout fallback remain intact.
- **Dashboard**: replaced the flat empty-box emphasis with an honest three-stage deal path, a live link to the available skills/team setup, an explicit setup panel, compact zero-value metrics, and stronger empty states for sessions and proposals. No fabricated data or future routes were added.
- **Accessibility/polish**: added a skip link, labelled dashboard regions, global keyboard focus treatment, smooth anchored scrolling with reduced-motion fallback, and responsive layouts at desktop and 390px.
- **Tests**: extended public view smoke coverage for the real preview CTA, branded auth bridge, dashboard pipeline/setup information architecture, and live team-setup link.

## Locked decisions to preserve

1. Canonical `dw-*` tokens only; no new fonts or hardcoded template colors.
2. Green chip semantics remain verified/accepted; amber remains estimate-only; teal carries neutral information.
3. All dashboard counts remain honest zeros/`—`; future actions remain visibly disabled with no fabricated routes.
4. The only new live dashboard destination is existing `/team/`; all other future-product destinations remain non-interactive.
5. Auth behavior, allauth forms, MFA/social flows, security settings, ownership logic, services, and selectors are unchanged.
6. Server-rendered Django + Tailwind standalone remains the entire frontend stack; no dependency or JavaScript business logic was added.

## Review checklist

1. Verify anonymous `/` still exposes signup/login, pricing, estimate disclaimers, all reviewed landing sections, and that the example-proposal CTA targets `#features`.
2. Verify login, signup, password-reset, verification, MFA, and social-account pages still render their existing form content within the new auth base at desktop and mobile widths.
3. Verify signed-in app shell: desktop sidebar + utility account dropdown; mobile hamburger drawer; Escape/outside-click behavior; two reachable logout surfaces; no-JS fallback.
4. Verify `/` signed-in shows the greeting, all five honest metrics, pipeline/setup content, existing `/team/` links, empty states, and estimate disclaimer; mockup demo figures remain absent.
5. Check semantic discipline and copy: no green informational chips, no amber outside estimates/warnings, no invented capabilities or financial claims, no fake links for unfinished screens.
6. Check accessibility: one H1 per surface, labelled H2 sections, decorative SVGs hidden, visible keyboard focus, skip link, and reduced-motion handling.
7. Check responsive behavior around 390px, `md`, and desktop: no horizontal page overflow, drawer overlays correctly, dashboard stages stack, auth left panel hides on mobile, landing CTAs remain usable.

## Gates and builder evidence

1. `.venv/bin/pytest -q` — **79 passed** (37 existing staticfiles warnings).
2. `.venv/bin/ruff check .` — clean.
3. `.venv/bin/python manage.py check` — no issues.
4. `.venv/bin/python manage.py makemigrations --check --dry-run` — no changes detected.
5. `scripts/build_css.sh` — successful; committed CSS rebuilt from the updated sources.
6. `git diff --check` — clean.
7. Live browser QA completed at 1440×900 and 390×844 for landing, login, dashboard, and the open mobile drawer. A temporary local test account was removed afterwards.

## Required verdict format

```text
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings:
1. ...
Minor findings:
1. ...
Rationale: ...
```

Do not edit files. A blocking finding requires a fix and a fresh reviewer pass. Record the verdict and builder disposition below before closing this UI addendum.

## Verdict

Pending fresh GLM review.
