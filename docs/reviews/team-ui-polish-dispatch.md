# Dispatch — Card 4 addendum: team workspace UI polish (2026-09-30)

**Scope:** commit `187791c` on baseline `95187a8`. **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## What changed

- Reworked `/team/` into a bounded, responsive delivery-setup workspace with a clear page introduction and compact counts for own skills, team members, and delivery mode.
- Added stronger section hierarchy for personal skills and the team roster, while retaining every existing action and all stored-field rendering.
- Moved skill entry into a distinct “Add a skill” panel; the Tasks field is now a multiline textarea and stored line breaks render on both team surfaces.
- Made the roster easier to scan with member initials, emphasized stored rates and availability, honest teal information states, explicit skill counts, and clearer profile links.
- Added purpose-built mobile skill and member cards below the `md` breakpoint instead of forcing wide tables into a narrow viewport.
- Added consistent native select/textarea styling and green-tint focus rings using canonical `--dw-*` tokens; rebuilt committed `static/css/app.css`.
- Extended the existing team-page smoke test to pin the new visible “Add a skill” and “Team roster” information architecture.

## Locked decisions to preserve

1. Green chips remain reserved for verified/accepted; self-reported, active, and rates-not-set states use neutral teal or neutral borders.
2. Gold is not used; amber remains estimate-only; no new colors or fonts were introduced.
3. Rates are displayed only from stored fields with the existing `dw_symbol` formatter; no math or FX conversion was added.
4. The page stays server-rendered Django + Tailwind utilities; no JavaScript or new dependency was introduced.
5. Existing ownership guards, CSRF forms, POST-only mutations, services, and selectors are unchanged.

## Review checklist

1. Confirm the template preserves all existing behaviors: add/delete own skill, open/add team member, stored rate basis and currency rendering, active/inactive state, and empty states.
2. Check responsive behavior at desktop and approximately 390px: desktop tables appear at `md+`; mobile cards appear below `md`; no clipped controls or horizontal page overflow.
3. Check semantics and accessibility: one H1, labelled H2 sections, real tables on desktop, meaningful link/button labels, decorative SVGs hidden from assistive technology, and keyboard-visible native form controls.
4. Check theme discipline: templates use only existing `dw-*` tokens; no hardcoded hex, new font, green status chip, gold decoration, or amber non-estimate state.
5. Check query discipline: the template uses only the prefetched `vas` capabilities and provided querysets; no new selector/view logic or money computation is present.
6. Check the pre-existing textarea/line-break edits included in the commit remain safe: `tasks` stays limited by the existing form/model validation and output remains Django-escaped.

## Gates and recorded builder evidence

1. `.venv/bin/pytest -q` — **79 passed** (37 existing staticfiles warnings).
2. `.venv/bin/ruff check .` — clean.
3. `.venv/bin/python manage.py check` — no issues.
4. `git diff --check` — clean.
5. Live authenticated browser smoke with representative skills and two members — desktop and 390×844 mobile layouts visually verified; temporary test account removed afterwards.

## Required verdict format

```text
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings:
1. ...
Minor findings:
1. ...
Rationale: ...
```

Do not edit files. A blocking finding requires a fix and a fresh reviewer pass. The builder must record the verdict and disposition here before this addendum is closed.
