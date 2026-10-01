# Dispatch — pass 14: delivery mode off settings; friendly negative-value validation (2026-10-01)

**Scope:** single commit `837102d` on baseline `72dae70` (pass 13, APPROVED). **For:** fresh GLM reviewer (read-only; run gates and report only). Repo root: `/home/robbb/dealwright`.

**Still out of scope (uncommitted, do not review):** Robb's hand edits — `templates/dashboard.html`, `templates/team/member_detail.html`, `static/css/app.css`.

## What changed (Robb-directed, design-log entry 2026-10-01)

1. **Delivery_mode removed from the settings page.** `ProviderProfileForm` drops the field + widget; settings POSTs no longer carry it. Rationale: the solo-vs-team choice happens in the proposal/LLM flow (Card 7/8 scope — backlog note added). `ProviderProfile.delivery_mode` **stays** as the stored field (solo default) that guardrails and Cards 5/8 read — model unchanged. Pass 13's view test asserting a POSTed delivery_mode was rewritten to omit it; the invalid-POST test likewise.
2. **Negative money/hours now fail validation, not the DB.** `MinValueValidator(0)` on the three mixin fields (`rate_per_hour`, `project_rate`, `availability_hours_per_week`) → `full_clean()` (every service write) raises a friendly field `ValidationError`; forms render it inline. Previously a negative POST passed form + full_clean and died on the CHECK constraint as a 500 — the reported bug, on both the provider settings page and the member engagement form (shared fields). DB CHECK constraints unchanged as backstop. **Migration `team.0009`**: validator-state AlterFields only — schema no-op on both tables.
3. **New tests:** model-level negative rejection via `full_clean` for all three fields on ProviderProfile + one VA-side proof (mixin inheritance); view-level: settings POST **without** delivery_mode saves; negative `project_rate` POST → 200 re-render with `project_rate` in form errors, zero writes.
4. **Docs:** design-log 2026-10-01 entry (both decisions); backlog — Card 7/8 delivery-mode-choice note, catalog `Service` price fields flagged with the same hole (setup_low/high, monthly_low/high have no validators — residual for next catalog card), settings-surface section updated.

## Locked decisions to preserve

1. **No-FX (Q3)** untouched; **delivery_mode stays a stored model field** — only its settings-page entry point moved; nothing reads it differently yet.
2. Validator = friendly first line; **CHECK constraints remain the enforcement backstop** (both layers tested).
3. Money/claims discipline: no pricing/matching/chip changes; the validators only reject impossible inputs earlier.
4. Styleguide: form validates input only; service still owns `full_clean` before save; thin view; tokens-only UI.

## Review checklist

1. Form no longer exposes delivery_mode anywhere in settings UI; POST without it persists all other fields; no template/form/code path can set delivery_mode from the settings route.
2. Negative values: `full_clean` rejection verified for all three fields on **both** models; DB CHECK still enforces at the backend (existing `objects.create()` tests); no 500 path remains on either settings or member-engagement form for negative input.
3. Migration 0009 is validator-state only (no schema change); `makemigrations --check` clean.
4. Docs accuracy: design-log entry matches the shipped behavior; backlog residuals present (Card 7/8 choice UI; catalog validators).
5. Styleguide + locked decisions 1–4.
6. Gates: rerun yourself; compare to evidence below.

## Gates and recorded builder evidence

1. `.venv/bin/python -m pytest -q` — **188 passed** (87 pre-existing warnings).
2. **Clean-HEAD worktree** at `837102d`: `pytest -q` → **188 passed**; `ruff check .` → clean.
3. `.venv/bin/ruff check .` — clean; `manage.py makemigrations --check --dry-run` — no changes; `git diff --check` — clean.

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

## Verdict — pass 14 (recorded 2026-10-01)

Fresh GLM-5.3 reviewer (read-only, independent session) reran all six gates matching recorded evidence (188 passed in-tree and in a clean worktree at `837102d` — proving no committed test depends on Robb's uncommitted hand edits; ruff clean; `makemigrations --check` clean; `git diff --check` clean; `sqlmigrate team 0009` shows every op as a no-op). Checklist adjudicated against the actual diff: delivery_mode unreachable from the settings route while remaining a stored solo-default field; negative money/hours fail `full_clean` on all three fields on both models (including an independent VA-side live probe) with DB CHECK backstops still tested; docs and backlog residuals accurate; locked decisions 1–4 hold.

```text
Verdict: APPROVED
Blocking findings:
1. None.
Minor findings:
1. No committed view test pins the member-engagement route's negative-POST behavior (PRG + zero writes); covered today via shared mixin validators and verified live by this reviewer — add a route-level test next time team/ is open.
2. VA-side full_clean test covers only rate_per_hour (provider side is parametrized over all three fields); inherited behavior confirmed independently — parametrize for symmetry.
Rationale: All six gates rerun and match the card's evidence exactly (188 passed in-tree and in a clean worktree at 837102d, proving no test depends on Robb's uncommitted hand edits; ruff clean; makemigrations --check clean; git diff --check clean). Every checklist item adjudicated against the actual diff: delivery_mode is unreachable from the settings route while remaining a stored solo-default field (locked decision 1); negative money/hours fail full_clean with friendly field errors on all three fields on both models (verified, including independent VA-side probe) with DB CHECK backstops still tested and live; migration 0009 is a verified schema no-op; docs and backlog residuals are accurate; styleguide and locked decisions 1–4 hold. No estimate, guardrail, token, secrets, or test-coupling violations found.
```

**Disposition of minors — applied directly (3779f98, gates rerun green: 191 passed, ruff clean):**
1. Route-level engagement negative-POST test committed (`test_member_engagement_negative_rate_writes_nothing` — PRG, zero writes).
2. VA-side `full_clean` test now parametrized over all three fields (symmetry with the provider side).

**Pass closed.** Scope commits `837102d`, `3779f98` stand as reviewed.
