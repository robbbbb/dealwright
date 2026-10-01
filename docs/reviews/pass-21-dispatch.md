# Dispatch — pass 21: provider settings UI refinement (2026-10-01)

**Scope:** commit `18043ea` on baseline `d14f540`. **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## What changed

- Reworked `/team/settings/` from one long form into three clear areas: Business identity, Commercial defaults, and Security.
- Added a wider responsive shell: commercial fields form a two-column grid from the small breakpoint, while Security moves into a 320px sticky side card at the extra-large breakpoint.
- Strengthened page hierarchy with the workspace eyebrow, larger title, section summaries, restrained token-based icons, and a distinct save footer.
- Replaced technical helper copy (writer-model/Q3 wording) with plain provider-facing guidance without changing field definitions or validation.
- Restyled account-security actions as compact outlined controls; MFA-on remains green/verified, MFA-off remains neutral, and the recommendation uses the canonical teal information treatment.
- Added semantic labelled sections and a form-level accessible name; decorative SVGs are hidden from assistive technology.
- Added one UI smoke test for the visible section information architecture and ARIA labelling; rebuilt committed `static/css/app.css`.

## Locked decisions to preserve

1. This pass is UI-only: no model, form, view, selector, service, URL, migration, or business-rule changes.
2. Every existing settings input remains present and posts under the same field name; allauth email/password/MFA destinations remain unchanged.
3. Canonical `dw-*` tokens only. Green means brand/verified, teal means neutral information, amber remains estimate-only, and gold remains premium-only.
4. Server-rendered Django + Tailwind utilities only; no new JavaScript or dependency.
5. Settings keep their existing ownership, CSRF, validation, and PRG behavior.

## Review checklist

1. Compare `d14f540..18043ea`; confirm the scope is limited to the settings template, its UI smoke test, and generated CSS.
2. Verify every `ProviderProfileForm` field is rendered exactly once with its label, current value, help copy, and errors: branding_name, persona, rate_basis, rate_per_hour, project_rate, currency, availability_hours_per_week, timezone, languages.
3. Verify invalid-form rendering preserves field and non-field errors, and all three `min="0"` browser guards remain present.
4. Verify account-security links and Google-auth adaptation remain intact: email manage, change/set password, MFA manage/setup.
5. Check responsive behavior at approximately 390px, 690px, and 1440px: no horizontal overflow; commercial fields collapse cleanly below `sm`; Security stacks below the form until `xl`, then becomes a sticky side card.
6. Check semantics and accessibility: one H1, labelled sections/aside, form accessible name, native labels and controls, decorative SVGs hidden, visible keyboard focus inherited from the shared theme.
7. Check theme discipline: no hardcoded colors/fonts, green/teal usage matches semantics, no amber or gold misuse.
8. Re-run the gates below and report only; do not edit files.

## Gates and recorded builder evidence

1. `.venv/bin/pytest -q` — **211 passed** (108 existing staticfiles warnings).
2. `.venv/bin/ruff check .` — clean.
3. `git diff --check` — clean.
4. Live authenticated browser smoke at the active 690px-wide viewport — visual hierarchy, two-column commercial grid, native controls, and accessibility tree verified.
5. Tailwind build `./scripts/build_css.sh` — successful; committed CSS contains the `sm` and `xl` responsive rules used by the template.

## Required verdict format

```text
Verdict: APPROVED | CHANGES REQUIRED
Blocking findings:
1. ...
Minor findings:
1. ...
Rationale: ...
```

Do not edit files. A blocking finding requires a fix and a fresh reviewer pass. The builder must record the verdict and disposition here before this pass is closed.

---

## Verdict — pass 21

Pending fresh GLM reviewer. The required GLM reviewer is not available in this session; leave this dispatch for Robb to run in a fresh reviewer session.
