# Dispatch — pass 21: ROI engine core + settings-config benchmarks (2026-10-01)

**Scope:** commit `7977f24` on baseline `d14f540` (`git show 7977f24`). Commits between pass 20 and this baseline are closed work, NOT under review. **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

## What changed

This is the **Card 3 core** (pure engine + config). No DB models yet — `Estimate`/`WorkflowActivity` persistence lands with the Card 1 dependency in the next session; this commit is deliberately UI-free and migration-free.

1. **`config/roi.py` (new)** — ROI benchmarks as **settings config** (Robb decision 2026-10-01: settings config, not DB rows, not a doc): `ROI_BENCHMARKS_VERSION = "2026.10"` + `ROI_BENCHMARK_BANDS` (task_time_reduction 40/60/80%, handoff_share 75/90/100%, scenario_spread ×1.0/1.2/1.33, revenue levers speed_to_lead_uplift / missed_lead_recovery / dso_days, each with unit + source note). Platform-level: superuser edits the file in the repo (git = access control); providers never see it; every future Estimate snapshots version + values used.
2. **`config/settings/base.py`** — re-exports `ROI_BENCHMARKS_VERSION` / `ROI_BENCHMARK_BANDS` from `config.roi` (F401 noqa'd, deliberate).
3. **`core/roi/engine.py` (new)** — pure module: no Django, no DB, no LLM. Dataclasses in/out; `Decimal` money; 2dp ROUND_HALF_UP at the output edge; currency passthrough (Q3: no FX).
   - `Band` (+ `band_from` config dict, `band_point` degenerate) — validates 0 ≤ low ≤ mid ≤ high, Decimal-only.
   - `WorkflowInput` — performed_by ∈ {client, employee, nobody, outsourced}; negative-value and unknown-choice rejection; `monthly_hours = hours_per_week × 4.33` (2dp).
   - **`automation_estimate`** — hours_saved = monthly_hours × reduction% × employees; labor value = × time value. **Pastor anchor:** 12h/mo @ 75%, ₱300 → 9.0h, ₱2,700.
   - **`delegation_estimate`** — hours = monthly × handoff share; net = value − VA cost (stored rate, never estimated). **LF anchor:** 8 hrs/wk @ ₱400, share 75/90/100%, ₱120/hr → 26.0/31.2/34.6h → nets **₱7,280 / 8,736 / 9,688**.
   - **Hours are quantized to 1dp BEFORE money math** — traceable-figures discipline: the displayed hours are exactly the hours computed with.
   - `_payback` — setup ÷ net, **None when no setup or net ≤ 0** (no ÷0, no negative nonsense).
   - `revenue_gain` — quarantined: reported per scenario, **never folded into labor net or payback**; negative lead inputs rejected.
   - `select_mode` — ("qualitative", reason) when performed_by = nobody or data incomplete (follow-up questions), else ("computed", …).
   - `rollup` — sums net per scenario across workflow estimates.
   - **Zero-employees rejection** (error, never silently-zero labor savings); nobody+data still refuses to compute.
4. **Tests** — `core/tests/test_roi_engine.py`: 31 tests across bands, input validation, both design-doc TDD anchors, payback, revenue quarantine, mode selection, rollup, and settings wiring (`override_settings` proof). Coverage of `engine.py` ≈ **100% of lines** (measured with a stdlib `settrace` harness because pytest-cov isn't installed — backlogged).
5. **`templates/app-base.html`** — sidebar placeholder "ROI estimates" **removed** (Robb: ROI is a settings config + engine embedded in sessions/proposals, not a provider-facing page). Discovery sessions / Proposals placeholders remain.
6. **`core/tests/test_views.py`** — sidebar item list updated to match (comment records why).
7. **`docs/backlog.md`** — one line: pytest-cov not installed; add at next deps-touching card. (Per Robb: no planning-doc updates this pass.)

## Locked decisions to preserve

1. **No LLM, no DB, no Django imports in `core/roi/engine.py`** — pure deterministic math only.
2. **Money = Decimal; hours quantized to 1dp before money math** (displayed == computed); 2dp money at the edge.
3. **Currency passthrough, no FX** — engine carries a label, never converts.
4. **Modes exclusive per estimate line; revenue gain quarantined** (separate lines, excluded from payback).
5. **Benchmarks = settings config, platform-level** — providers never read-write them; estimates snapshot version + values.
6. **Nothing invented:** missing data → qualitative + reason (follow-up questions upstream); zero-benefit → payback None; zero employees → error, not silent zero.

## Review checklist

1. **Anchor fidelity:** rerun both worked examples and compare to the design-doc numbers (pastor: 9.0h / ₱2,700; LF: 26.0/31.2/34.6h, values ₱10,400/12,480/13,840, costs ₱3,120/3,744/4,160, nets ₱7,280/8,736/9,688). Check the quantize-hours-before-money rule reproduces them exactly.
2. **Purity:** grep `core/roi/engine.py` for django/db/requests imports — must be none; verify no I/O; verify pure-function determinism (same in → same out).
3. **Edge discipline:** payback None cases; zero employees raises; nobody raises even with data; malformed band raises; negative inputs raise; revenue quarantine (nets untouched by revenue_gain).
4. **Config discipline:** settings wiring real (`settings.ROI_*` via base.py import); override_settings test proves engine picks up changes; bands monotonic (low ≤ mid ≤ high) test present; no provider-facing surface reads/writes ROI config (grep templates/views).
5. **Sidebar removal:** "ROI estimates" gone from app-base; remaining placeholders (Discovery sessions, Proposals) intact; dashboard copy untouched; updated sidebar test still asserts all remaining items.
6. **Tests:** all 31 meaningful (no tautologies); anchors asserted exactly, not loosely; ruff clean; full suite green (242).

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **242 passed** (108 pre-existing warnings).
2. `.venv/bin/python -m ruff check .` — clean.
3. `.venv/bin/python manage.py check` — no issues.
4. `git diff --check` — clean.
5. Engine line coverage ≈ **100%** via stdlib settrace harness (pytest-cov absent — backlogged); no migrations in scope; `git show --stat 7977f24` = 6 files (config, engine, tests, template, backlog).

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
