# Dispatch — Card 4: provider skills & VA bench (Robb-directed order, 2026-09-29)

**Scope:** commits `0282fa9` (models), `a8b8c45` (services/selectors/forms/views/urls), `4fc60b0` (templates + wiring), `d07529f` (tests). **For:** fresh GLM-5.3 reviewer (read-only, run gates). Seed with repo root `/home/robbb/dealwright`.

**What was built:** the supply side of the pipeline — freelancer profile + VA roster + skills — as app `bench`:

- **Models** (`bench/models.py`): `ProviderProfile` (OneToOne owner; delivery_mode solo|team, default solo; branding_name; persona), `VAProfile` (owner FK; display_name unique-per-owner; is_active; rate_basis hourly|project with `rate_per_hour`/`project_rate`; currency PHP; availability; timezone Asia/Manila; languages; industry_experience), `Capability` (exactly-one-holder check constraint across nullable FKs to profile/VA; skill unique per holder (partial unique constraints); proficiency level beginner/intermediate/advanced with `trust_rank`; free-text `tasks`). PH-anchored defaults. No protected-characteristic fields exist (asserted by test).
- **Services** (`bench/services.py`): `get_provider_profile` (solo-by-default create-on-first-need), `create/update_va_profile`, `add/update/delete_capability` — every write `full_clean()`ed; `@transaction.atomic` on capability writes.
- **Selectors** (`bench/selectors.py`): ownership-filtered reads (`get_va_for_owner`, `get_capability_for_owner` via Q across both holder FKs; `list_vas` prefetches capabilities; `list_holder_capabilities` documented no-join rationale).
- **UI**: `/bench/` (own skills + roster table), `/bench/add/`, `/bench/<pk>/` (profile edit + per-VA skills) — theme-consistent (`card`, dw tokens, table utilities); proficiency chips neutral by design (**green is reserved for real verification** per theme chip rules); sidebar "My skills & bench" placeholder is now live with active-state highlighting. PRG + flash messages; forms render via shared `_form_fields.html` partial.
- **Tests** (`bench/tests/`): 50 new — ladder ranks (superseding TDD anchor per design log 2026-09-29), holder integrity (orphan/both-holder/DB constraint), negative money/hours at DB level, name uniqueness per owner, PH defaults, no-protected-fields schema test, service write/reject paths (invalid claims never save), view smoke incl. cross-tenant 404s.

**Deliberately out of scope:** admin registration (UI covers CRUD; deviation recorded in design log), matching logic (Card 5), prices (Card 2 catalog).

**Gates:**
1. `.venv/bin/python -m pytest` — expect **73 passed**
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — clean
4. `.venv/bin/python manage.py makemigrations bench --check --dry-run` — no changes pending
5. Live smoke: GET `/bench/` anonymous → 302 to login; authenticated behavior covered by the view tests (or throwaway `django.test.Client` script: force_login → GET `/bench/` assert "My skills", "Bench", "Add bench member"; POST a skill → assert chip + row render)
6. Product discipline: no money math outside the ROI engine (rates stored, never computed/converted); rate bases never compared cross-basis; no protected-characteristic columns on any of the three models; tenancy guards (selector ownership filters + view 404 tests); all writes through services with `full_clean`
7. Template hygiene: no hardcoded hex in `templates/bench/*` (tokens only); `{% url %}` targets all resolve; no business logic in views beyond form→service→redirect

**Deviations to adjudicate (all recorded in `docs/design/design-log.md`, "Card 4 build decisions", 2026-09-29):**
1. **Run order:** Card 4 before Card 1 — Robb-directed between cards; no Card 1 model dependency exists; Card 1 remains next.
2. **Skill model supersession:** the build plan's claimed/verified evidence ladder + TDD anchor replaced by proficiency ladder + `tasks` description (Robb decision — more proposal-suitable: the tasks line is what proposals narrate). Matching will weight advanced highest (Card 5). Green chip reserved.
3. **App label `bench`** while models keep Q9 "Provider" names — vocabulary split is intentional (docs/design say "provider"; the daily word for the roster is "bench").
4. **`rate_basis` addition** beyond the build-plan field list — required to represent per-project bench members honestly; never converted across bases.
5. **Admin registration deferred** to the real UI (AGENTS.md permits admin for bench; UI chosen).
6. **`bench.0001` regenerated twice pre-commit** (schema in flux, nothing deployed); Robb's dev DB was reset via `migrate bench zero` + re-apply. Post-deploy rule noted: migrations append-only.

## Verdict (pass 1)
### Pass 1 verdict — CHANGES REQUIRED

Gates 1–5 + 7 green with real output; all six adjudicated deviations accepted (verified against the design-log entry, not the card's prose); money/tenancy/template discipline holds. One blocking security/correctness defect on a shipped write path:

```
Verdict: CHANGES REQUIRED
Blocking findings:
1. bench/views.py::skill_delete mutates on GET (live-proven: GET → 302, capability deleted) —
   CSRF-exempt mutation; violates the card's PRG claim. Add @require_POST to skill_delete,
   va_skill_add, skill_update + tests (GET → 405, no state change).
Minor findings:
1. Sidebar active-state never fires (resolver_match.namespaces empty — no app_name); card claims it works.
2. Dispatch card says 50 bench tests, actual 48; @transaction.atomic claimed on capability writes
   but only add_capability decorated (single-statement writes unaffected).
3. Hardcoded ₱ in bench.html despite stored va.currency field.
4. "Active" chip uses green primary family — chip semantics reserve green for verified/accepted.
5. Uncommitted docs/mockups/landing-mockup.html change in tree at card boundary — commit or discard before Card 1.
Rationale: All six recorded deviations are properly adjudicated and match the code; gates 1–5 pass with
real evidence; product/money/tenancy/template discipline holds. The single blocking security/correctness
defect (state-changing, CSRF-exempt GET on the delete path) violates the card's own PRG guarantee —
fix and re-dispatch for a fresh pass.
```

**Builder disposition (2026-09-29):**
- **Blocking 1 → fixed** in `e5fd21f`: `@require_POST` on `skill_delete`/`va_skill_add`/`skill_update`; tests assert GET → 405 with no state change (3 new tests). Suite now **77 passed**.
- **Minor 1 → fixed** in same commit: `app_name = "bench"` + namespaced includes/reverses everywhere (templates, views, tests); sidebar active state now fires.
- **Minor 2 → corrected:** bench test count was 48 at pass 1, **52 after the fix commit** (card prose updated here); `@transaction.atomic` claim narrowed to `add_capability` only (update/delete are single-statement writes — no correctness impact).
- **Minor 3 → fixed:** new `bench/templatetags/dw_money.py` (`dw_symbol` filter — formatting only, no math); rate column renders the symbol from the stored `va.currency` (USD test included).
- **Minor 4 → fixed:** Active chip re-mapped to teal (`dw-teal-bg`/`dw-teal` = neutral info per theme.html); green stays reserved for verified/accepted.
- **Minor 5 → with Robb** (his uncommitted landing-mockup glyph edit — per the one-writer-per-file convention, not the builder's to commit).

---

# Pass 2 — fresh reviewer on the fix

**Scope:** commit `e5fd21f` only (bench/views.py, bench/urls.py, bench/templatetags/, bench/tests/test_views.py, templates/bench/*, templates/app-base.html). **For:** fresh GLM-5.3 reviewer (read-only, gates).

**Gates:**
1. `.venv/bin/python -m pytest` — expect **77 passed**
2. `.venv/bin/python -m ruff check .` — clean
3. `.venv/bin/python manage.py check` — clean
4. `.venv/bin/python manage.py makemigrations bench --check --dry-run` — no changes
5. Live smoke via throwaway Client: GET `skill_delete`/`skill_update`/`va_skill_add` → 405 and no state change; POST delete still works; USD bench member renders `$40` and no `₱40`

**Adjudicate:**
1. Blocking fix complete: all three mutation endpoints reject GET with 405 before any logic runs (`require_POST` decorator order with `login_required` acceptable — both return 40x without mutating).
2. Namespace fix complete and consistent: every reverse (templates, views, tests) namespaced; sidebar active-state now verifiably fires on `/bench/*` pages.
3. `dw_symbol` filter is formatting-only (no math, no conversion — money discipline intact).
4. Teal Active chip consistent with theme chip semantics (green = verified/accepted, teal = neutral info).
5. Pass-1 minors 2 (card prose) and 5 (Robb's working-tree file) dispositioned above — confirm handling.

## Verdict (reviewer pass 2)
### Pass 2 verdict — APPROVED

```
Verdict: APPROVED
Blocking findings: (none)
Minor findings:
  1. docs/mockups/landing-mockup.html still uncommitted in the working tree (Robb's own edit,
     dispositioned per one-writer-per-file) — must be committed or discarded before Card 1 begins.
  2. bench:skill_update endpoint has no UI affordance yet (no template posts to it); pre-existing,
     now POST-only and tested — add a backlog line for the edit-level UI.
Rationale: All four gates pass with real output (77 passed; ruff/check/migrations clean) and the
live hermetic smoke proves the blocking defect is fixed: all three mutation endpoints return 405
on GET with zero state change (including cross-tenant), POST delete still works, the bench
namespace + sidebar active state fire, USD renders "$40" from the stored currency via a
formatting-only filter, and the Active chip uses canonical teal tokens with no green-family or
hardcoded values. Commit e5fd21f is tightly scoped to the four fixes. Both carry-over minors are
recorded with dispositions and do not block.
```

**Builder disposition (2026-09-29):** minors 1–2 → moved to `docs/backlog.md` ("Card 4 residuals") with owners: minor 1 = Robb (his working-tree file); minor 2 = future UI card. **Card 4: approved & closed.** Card 1 (core domain models) is next.

---

# Addendum — team restructure (Robb-directed, 2026-09-29, after card close)

**Scope:** `6da8e2b` (bench → team rename), `a0dd712` (design-log adjudications), `5771163` (design item A: slim member forms + Rates & availability card), `55df0c7` (review hardening). **Reviewed via in-session GLM-5.3 subagent passes (architectural design pass, then implementation pass) — both APPROVED; full transcripts in the builder session log, verdicts summarized here.**

**Architectural design pass — APPROVED.** Adjudications (recorded in `docs/design/design-log.md`, "Card 4 build decisions"): engagement fields stay in `VAProfile` (extraction triggers: per-client rates / rate history / per-proposal overrides); Card 5 must exclude engagement-incomplete members with an explicit reason (TDD anchor `test_incomplete_engagement_member_excluded_with_reason`); solo provider rate = shared abstract `EngagementTermsMixin` on ProviderProfile + VAProfile, small card before Card 5, bundled with provider-profile edit UI; Card 8 delivery source governed by `delivery_mode` (team-mode self-delivery would need a recorded Q9 supersession — not in MVP); delivery-cost math stays in `core/roi/`.

**Item A implementation pass — APPROVED.** Gates: 78→79 passed, ruff/check/migrations clean. Verified: identity-only creation (pinned `full_clean` test), "Rates & availability" card on member detail (own endpoint, cross-tenant 404 proven), roster teal "Rates not set" replacing ₱0 (zero `₱0` occurrences while states coexist), no money math, POST-only mutation guarantees intact.

**Builder disposition:** design minors 1–2 → fixed in `a0dd712` (design-log entry, backlog reference). Implementation minor 1 → fixed immediately in `55df0c7` (`@require_POST` on `member_engagement` + 405 test; suite **79 passed**). Minor 2 (currency picker PHP/USD at widget layer) → accepted, presentation-only per Q3. landing.html "bench" marketing copy → with Robb (backlog). **Team restructure: approved & closed.**
