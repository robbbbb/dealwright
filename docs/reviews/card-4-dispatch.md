# Dispatch — Card 4: provider skills & VA bench (Robb-directed order, 2026-09-29)

**Scope:** commits `4ddf92e` (models), `e950270` (services/selectors/forms/views/urls), `648985a` (templates + wiring), `8d845ca` (tests). **For:** fresh GLM-5.3 reviewer (read-only, run gates). Seed with repo root `/home/robbb/dealwright`.

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

## Verdict (reviewer)

*(pending — fresh GLM-5.3 reviewer pass)*
