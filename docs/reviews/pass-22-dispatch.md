# Dispatch — pass 22: ROI engine fixes from pass 21 review (2026-10-01)

**Scope:** commits `d28eba1` (Card 3 core, re-reviewed for the corrected evidence) + the fix commit on top (see `git log d14f540..HEAD`; reachability double-checked — **no amends after dispatch this time**). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## Why this pass exists

Pass 21 returned CHANGES REQUIRED: (1) false evidence in the dispatch card (a backlog line claimed but never written — a piped pytest masked a failure and short-circuited the chain; an amend orphaned the referenced hash), (2) negative paths of the 95–100%-tier engine untested, (3) design-log/backlog decision records bypassed. This pass fixes all three blockers and all six minors. The pass-21 verdict + disposition are recorded at the bottom of `docs/reviews/pass-21-dispatch.md`, including the card corrections (coverage was 96.4%, not ≈100%; the LF cost anchor is ₱4,152, not ₱4,160 — the mockup tables were internally inconsistent and are now corrected to engine output).

## What changed since d28eba1

**Engine (`core/roi/engine.py`):**
- `band_from` now also catches `decimal.InvalidOperation` → non-numeric band values raise the intended `ValueError("Malformed benchmark band")` (minor 2).
- Dead untested `ModeEstimate.rollup()` method **deleted** (minor: "test it or delete it").
- `rollup()` gains a **mixed-currency guard** — `ValueError` on multi-currency input sets (minor 3; no-FX/no-blending discipline).

**Tests (`core/tests/test_roi_engine.py`, now 39):**
- Payback **None** asserted in all three named cases: no setup, zero net (zero-benefit band), negative net (build-plan edge "zero benefit → payback = None, no ÷0").
- Compute-path missing-data raises asserted (automation + delegation with None hours/cost); `monthly_hours is None` branch asserted.
- Negative `va_hourly_rate` raise asserted; non-numeric band value raises `ValueError`.
- Mixed-currency rollup rejection asserted.
- Tautological `test_never_reaches_automation_net` **replaced** with a structural quarantine test (ModeEstimate/ScenarioLine carry no revenue field).
- Minor refactor: `_pastor_input()` helper; all prior assertions unchanged.

**Sidebar test (`core/tests/test_views.py`):** now also asserts `"ROI estimates" not in content` (minor 4).

**Mockups:** both `personal-assistant-result-mockup.html` and `proposal-solo-va-mockup.html` corrected to engine-true figures — optimistic value **₱13,840** (was 13,860) and cost **₱4,152** (was 4,160); nets ₱7,280/8,736/9,688 unchanged (now internally consistent: 13,840 − 4,152 = 9,688).

**Records (blocking 3):**
- `docs/backlog.md`: the pytest-cov tooling residual **actually added this time** (verified in diff); the "ROI lever source must be decided before Card 3" item marked **Resolved 2026-10-01** with the settings-config decision.
- `docs/design/design-log.md` new entry: settings-config benchmarks (superseding §C5 BenchmarkBand-table direction), dynamic modes + benefit profiles + performed_by, quantize-before-money rule with both anchors, sidebar removal rationale, engine purity/zero-FX/rollup-currency contract.

**Not in scope:** everything else in `d14f540..HEAD` (mockup regeneration, confirmation gates, passes 13–19) is closed work.

## Locked decisions (unchanged from pass 21)

1. No LLM/DB/Django in the engine; Decimal; 1dp-hours-before-money; 2dp money at the edge.
2. Currency passthrough; no FX; modes exclusive; revenue quarantined.
3. Benchmarks = settings config; providers never touch; estimates snapshot version + values.
4. Nothing invented: qualitative + reasons; payback None; zero-employee error.

## Review checklist

1. **Verify every pass-21 blocker is actually fixed in the diff** — including that the backlog line exists in a committed file this time (`git log -p d14f540..HEAD -- docs/backlog.md`).
2. **Re-measure engine coverage yourself** (your own harness); confirm the negative paths are now exercised (payback-None ×3, missing-data raises, negative-rate, non-numeric band, mixed-currency rollup, monthly_hours None). Confirm the dead method is gone.
3. **Anchor re-check:** pastor + LF rows digit-for-digit; mockup tables now consistent (13,840 − 4,152 = 9,688; 12,480 − 3,744 = 8,736; 10,400 − 3,120 = 7,280).
4. **Records:** design-log entry present and accurate; backlog decision item closed; confirm card-vs-diff accuracy (this card's claims must match the actual diff).
5. Gates rerun; 39 engine tests + full suite (~250) green; ruff clean; manage.py check; git diff --check.
6. Judge whether the tautology→structural swap and the new guard tests are meaningful.

## Gates and recorded builder evidence (honest, re-verified)

1. `.venv/bin/python -m pytest -q` — **250 passed** (108 pre-existing warnings). *(Exact number to be confirmed by your run — report what you see.)*
2. `.venv/bin/python -m ruff check .` — clean.
3. `.venv/bin/python manage.py check` — no issues.
4. `git diff --check` — clean; scope commits reachable from HEAD (no amends after this dispatch).

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

## Verdict — pass 22 (recorded 2026-10-01)

```text
Verdict: APPROVED
Blocking findings:
None.
Minor findings:
1. docs/mockups/proposal-output-mockup.html:182-184 still shows the stale, internally inconsistent LF row (13,860 − 4,160 = 9,700 ≠ 9,688 displayed) — the third of the three LF-case mockups; the pass-22 card names only the other two (accurate), and pass-21's accepted disposition deferred regeneration to Cards 7/8, but the design-log entry's "Mockup tables corrected to engine output" overstates scope, and the deferred residual is not recorded in docs/backlog.md (only in the pass-21 review card). Disposition: add a backlog line or regenerate the table at the next docs/templating touch or at Cards 7–8; not approval-blocking.
Rationale: All four gates pass with numbers I reproduced independently (250 passed / 108 warnings; ruff clean; manage.py check clean; git diff --check clean; all scope commits reachable, no post-dispatch amend). All three pass-21 blockers are genuinely fixed: the backlog pytest-cov line exists in a committed file, the pass-21 card corrections are recorded, and this dispatch card's evidence claims match the actual diff exactly. My own settrace/AST harness measures core/roi/engine.py at 112/112 statements (100.0%) with every named negative path exercised by an exact-assertion test (payback None ×3, missing-data raises ×2, monthly_hours None, negative VA rate, non-numeric band, mixed-currency rollup), the dead ModeEstimate.rollup() is deleted, and the design-log entry accurately records the settings-config decision superseding §C5's BenchmarkBand-table direction along with the quantize rule, both engine-true anchors, and the sidebar removal. Both design-doc anchors reproduce digit-for-digit and both corrected mockup tables are internally consistent. The tautology→structural quarantine swap is a meaningful tripwire. One minor residual: the third LF mockup still carries the stale inconsistent row and is absent from the backlog ledger — recorded above with disposition; it does not break any gate or evidence claim.
```

**Builder disposition (2026-10-01):** APPROVED. Minor 1 resolved immediately rather than deferred — `proposal-output-mockup.html:182–183` corrected to the engine-true figures (₱13,840 / ₱4,152), making the design-log sentence true across all three LF mockups; no backlog entry needed since no residual remains. Card 3 core is closed at this verdict.
