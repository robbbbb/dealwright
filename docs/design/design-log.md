# Dealwright — Design Log

Name locked: **Dealwright** (`/home/robbb/dealwright`, repo `robbbbb/dealwright`). Stage: **design complete — build not started** (design stage 2026-09-28).

## Decisions locked

| Date | Decision |
|------|----------|
| 2026-09-28 | Single-user MVP per install; tenancy-ready `owner` FK on all top-level models. No multi-tenant auth in MVP. |
| 2026-09-28 | No code until design stage completes. (Design completed same day; build follows `mvp-build-plan.md`.) |
| 2026-09-28 | Name: **Dealwright** — collision-checked, `dealwright.io` available; trademark check at business registration (see backlog). |
| 2026-09-28 | LLM vendor: z.ai (GLM-5.3-Flash extraction + GLM-5.3 writing, config-driven routing — Q11). PDF: WeasyPrint. |

Resolved: project name, repo location, LLM vendor, PDF library. Remaining open items live in `docs/backlog.md`.

## Market scan (2026-09-28)

**Adjacent tooling that exists:**

- Transcript/notes → proposal generators: InkDraft, Wonit.ai, Sembly, Ourix, Scalaro; established proposal tools (PandaDoc, Proposify, Qwilr, Prospero, GetAccept, Storydoc, Nusii). InkDraft's differentiator is traceability — every proposal line links back to the call transcript.
- ROI calculators: exist mostly as enterprise content/lead magnets (frameworks, blog calculators), not as an integrated product feature with editable assumptions.
- VA sourcing/vetting (PH): VA Masters (6-stage vetting, dedicated n8n specialists, $6.50–15/hr, ~2-day matching), Somewhere.com (vetted automation specialists), OnlineJobs.ph (large but unvetted job board), VirtualStaff.ph, HireTalent.ph.
- n8n VA market rate: ~$6.50–15/hr (PHP ~370–870/hr).

**Gaps → positioning:**

1. Nobody combines discovery → deterministic ROI → catalog-driven service matching → own-bench VA matching → proposal in one tool sold to the *provider*. The real competition is the DIY stack: ChatGPT + spreadsheet + PandaDoc.
2. Notes→proposal alone is commoditized. The defensible parts are the transparent deterministic ROI engine and the provider-owned VA bench.
3. Traceability is worth copying: every AI-extracted fact should carry a pointer to the source snippet in the notes. Makes "LLM must not invent" auditable.
4. VA matching is bench management ("who on my team can run this"), not a marketplace. Bench will be 2–10 VAs at first: expect ties; reasons/gaps matter more than scores.
5. Pastor-case pricing sanity check: PHP 3,000–6,000/month at PH VA rates is consistent with a "VA monitors and operates, specialist builds once" model. Keep as hypotheses to test.

## Competitor map (verified 2026-09-28)

**Direct competitor (full pipeline: discovery → deterministic ROI → catalog matching → VA bench → proposal): none found.**

Partial overlaps, by proximity:

| Who | What they overlap | Where they stop |
|-----|-------------------|-----------------|
| **InkDraft** | Closest on flow: post-call transcript → proposal, term traceability | ROI is narrative "framing" in templates, not a deterministic engine; no catalog, no bench |
| **Qwilr** | Interactive ROI calculator blocks inside proposals (since 2021) | Seller hand-builds the calculator per proposal; no discovery-driven engine, no assumptions audit, no scenarios from a catalog |
| **Wonit, Sembly, Ourix, Scalaro, Artiweave** | AI notes/transcript → branded proposal | No ROI engine, no service-catalog matching, no VA bench |
| **PandaDoc, Proposify, Prospero, GetAccept, Storydoc** | Proposal documents + tracking | Content tools; value story left to the seller |
| **UiPath Process Mining (~$53/user/mo), Celonis** | Measured automation ROI from process data | Enterprise tools sold to the end company; needs data integration — not a freelancer's discovery-call tool. Conceptual validation, different market |
| **VA Masters, Somewhere, OnlineJobs.ph** | VA vetting/matching | Services/marketplaces, not software; potential sourcing channels for users' benches, not rivals |

**Consequences for positioning:**

1. "ROI appears in a proposal" is not unique (Qwilr). Our claim must be: *audit-ready, assumption-transparent, scenario-based estimates computed deterministically from the discovery session* — not a hand-built widget.
2. No single feature is a moat. The moat is the pipeline plus provider-owned data (own bench, own catalog, and eventually own outcome data feeding back into assumption defaults).
3. The daily competitor is the DIY stack: ChatGPT + spreadsheet + PandaDoc/Qwilr.
4. Medium-term threat: an incumbent proposal tool adding an AI discovery/ROI module. Speed to pilot + outcome data accumulation is the defense.

## UI posture (proposed 2026-09-28)

Verdict: the product is a **forms-and-tables workflow app, not a UI-heavy product**.

- Architecture: server-rendered Django templates + HTMX for the few partial updates (scenario toggle, formset add/remove). No SPA, no frontend build pipeline, no npm dependency graph. Tailwind or plain CSS.
- Django admin covers internal config in MVP: service catalog, VA capability admin. Hand-built UI only for the working flows.
- Proposal editor = structured form over fixed sections (per handoff spec) rendering to a styled template shared with PDF export. NOT a block/drag-and-drop builder.
- No chart library in MVP; numbers and tables only (advanced analytics already out of scope).
- Estimate: ~12–14 templates, most plain CRUD. Effort split roughly backend 60–65% / UI 35–40%.
- Fits test-coverage tiers: logic lives in views/forms/ROI engine (unit-testable); UI gets light smoke tests only.

Two temptation zones with guardrails: extraction review stays an editable grouped form with source-snippet chips (not a live-annotated transcript editor); ROI recomputes on save, not per keystroke.

## Design insights from the LF personal-assistant example (2026-09-28)

Input: raw job-post-style client want (messier and more personal than the pastor case). Mockups: `personal-assistant-result-mockup.html` (internal pipeline screens), `proposal-output-mockup.html` (final client proposal, team/agency provider), and `proposal-solo-va-mockup.html` (same want, solo VA provider with automation + social skills — demonstrates guardrail-driven output adaptation: "About me" section, no team language, solo pricing, social media as optional add-on).

1. **Real inputs are raw wants, not tidy discovery notes.** Extraction must handle job-post text with emoji, humor, and bullet lists. Source-snippet traceability still works fine on it.
2. **Second ROI mode required: delegation.** Automation mode (labor savings on a workflow) doesn't fit staffing cases. Delegation mode: `net = client_hours_delegaged × client_time_value − VA_cost`, plus payback vs setup. Engine picks mode per case; both share the scenario and editable-assumptions machinery. Non-financial benefits listed separately — often the real buying reason.
3. **Protected-characteristic handling is product-visible.** "FEMALE" in the request → compliance flag shown, excluded from matching, follow-up suggested (clarify the underlying need). This must be a first-class, visible feature — not a silent filter.
4. **Missing-info engine is a core selling moment.** This input yields 7 follow-up questions (hours, budget, timezone, physical-vs-remote errands, tools, confidentiality, start date). "Errands physical or remote?" decides the whole delivery model.
5. **Catalog gap:** needs a personal-productivity angle (calendar/reminder automation, task & document hub, booking link) — tagged under existing categories or a new "Personal productivity ops" category (Q8).
6. **Hybrid sell pattern:** VA service is the deliverable; light automations stretch the VA's hours. Proposal prices VA hours + setup fees; automation reduces cost-to-serve.

## Verified per-report LLM cost (2026-09-28)

Pipeline = 2 calls: extraction (GLM-5.3-Flash: $0.15/M in, $0.50/M out) + proposal writing (GLM-5.3: $1.40/M in, $4.40/M out). At ~3,000 in / 700 out (extraction) + ~2,500 in / 1,100 out (writing): **≈ $0.009 ≈ PHP 0.52 per full result**. Budget mode (Flash writes the proposal too): **≈ PHP 0.10**. Both inside the handoff's PHP 0.10–1.50 band; the PHP 3–5 reserve covers ~6–30× retries. Caching the static prompt parts (catalog digest, guardrails) cuts input cost further. Business implication: at ₱4,800/mo deal size the LLM cost is ~0.01% of first-month revenue — tier report limits are segmentation, not cost protection.

## Build plan (2026-09-28)

Full MVP card breakdown: `mvp-build-plan.md` — 12 cards (0–11), one per fresh session, TDD anchors per card, reviewer pass per card, dependencies ordered. Still design stage: no code until Robb says go. Open before Card 0: working name (`dealwright` proposed), Postgres instance choice → **resolved: Railway** (see below).

**System design (2026-09-28):** `system-design.md` — Railway deployment (Robb on Hobby $5). Key findings: Railway meters CPU/RAM usage, not requests; request volume is a non-issue for this app (<10% of one worker at 1k-user peak); real caps are RAM, LLM-wait worker starvation, PDF spikes — all config/queue fixes. Hobby covers to ~1k users ($8–13/mo usage), Pro natural at 1k+. App-sleeping opt-in, keep OFF on prod. n8n stays local, talks via token webhooks.

## Open design questions

- Q1 Entry mode: form-first vs notes-first. Recommendation: hybrid — paste notes → AI extraction → review as editable grouped form with source snippets and missing-field follow-ups.
- Q2 Scenario ranges (conservative/expected/optimistic): derive from service-catalog reduction ranges (low/mid/high), user-overridable, always displayed.
- Q3 Currency: store amount + currency per estimate (PHP default); no FX conversion in MVP.
- Q4 LLM vendor + model split (cheap extractor / strong writer). Cost ceiling per report per handoff: ~PHP 3–5 reserved.
- Q5 Proposal versioning: immutable once sent; edits create a new version.
- Q6 Service↔problem mapping: deterministic catalog tags; LLM may only suggest; user confirms.
- Q7 ROI engine modes: automation (labor savings) vs delegation (reclaimed client time). Both share scenarios + editable assumptions; mode chosen per case, maybe per workflow.
- Q8 Catalog scope: **resolved (draft)** — added "Personal productivity ops" as category 8. Full draft: `service-catalog-draft.md` (8 categories, ~26 services, PHP hypothesis pricing, ROI-parameter rules).
- Q11 **LLM integration layer (resolved 2026-09-28): no framework.** No LangChain — our surface is two fixed call types (extraction, proposal writing) against one provider; no agents/RAG in scope. Stack: `httpx`/`openai`-SDK → z.ai, Pydantic schemas for extraction validation, own `llm/` module with versioned prompt templates + usage logging + guardrail validators (guardrails must be our code regardless). Optional later: `instructor` for structured-output retries; `litellm` only if multi-provider. Revisit only if a genuinely agent/RAG-shaped feature arrives.
  - **Model routing ≠ multi-agent:** Flash-extraction + GLM-5.3-writing is config-driven routing (`EXTRACTION_MODEL`/`WRITER_MODEL` settings), plain code, no framework. Tiered = ₱0.52/proposal vs ₱0.90 all-flagship vs ₱0.10 all-Flash (budget mode). Real savings levers in order: quality-mode toggle (Fast/Premium per proposal — pilot decides), prompt caching of static blocks (−80% writer input cost), output caps. Tiering also buys speed on the interactive step (extraction) and quality where the client sees it (narrative).
- Q13 **Auth (locked 2026-09-28): django-allauth** — email/password + Google social login; email verification required before proposals can send/share (anti-abuse on public share links); TOTP MFA + one-time recovery codes via allauth MFA app — optional for solo (offered after first proposal send), required for Agency tier. Forgot-password copy is anti-enumeration (same message whether account exists); reset link single-use, 24h expiry, invalidates other sessions. Screens: `docs/mockups/auth-mockup.html` (7 frames mapped to allauth templates: login, signup, verify-email, password_reset, password_reset_from_key, mfa/authenticate, mfa/setup+recovery_codes).
- Q12 **Theme (locked 2026-09-28): "money green".** Deep jade/emerald family + restrained gold accent; system fonts, no webfonts. Canonical tokens in `docs/mockups/theme.html` (CSS variables): green-950→50 scale (`#04241B`…`#EFF8F3`, primary action `#116E4F`, links `#15825D`), gold-600 `#B79121` (premium only), amber = estimate (always), red `#C0392B` = gaps/errors, teal `#0E7490` = info, canvas `#F6F8F7`, ink `#16241D`. Semantic unity: green doubles as "verified/accepted", matching the brand story. Gradient `#0E5941→#0B3D2E` for hero/sidebar. Logo mark: gold ₱ square. First themed screen: `dashboard-mockup.html`. The three earlier proposal mockups predate the theme (blue/violet) — restyle when proposal UI is mocked for real.
  - **Mark evolution (2026-09-28, Robb feedback):** v1 bare ₱ glyph → v2 "DW" + peso bars (rejected: ugly) → **v3 final: elegant monogram — flat gold square, white "DW" at weight 300 with wide tracking (3px/64-box, +1.5px optical x-shift), no bars, no depth edge, no ornaments.** Luxury-badge style; favicon uses the same treatment tuned for 16px legibility. Production refinement replaced the font-dependent DW with custom monoline vector paths, preserving the light, widely spaced letterforms while making the mark deterministic across platforms; the favicon uses a sturdier stroke. Applied to all four brand SVGs; `brand-preview.html` references files via `<img>` (single source of truth). The horizontal wordmark remains live text on the approved system stack and should be outlined only for self-contained print masters.
- Q10 **SaaS pricing (draft, 2026-09-28)** — PH-launch prices anchored under global tools (PandaDoc $19≈₱1,083, Qwilr $35≈₱1,995): Starter ₱399/mo (10 proposals, watermark), Professional ₱899/mo (40 proposals, own branding, integrations), Agency ₱1,990/mo (unlimited fair-use, 5 seats, white-label). Annual = 2 months free. 14-day full trial, no permanent free tier at MVP. Founding-20 offer ₱299/mo for outcome data + testimonials. USD versions ($8/$18/$39) when going international; currency stored per account (Q3). Unit economics: worst-case API ₱16-21/mo per heavy user → 90%+ gross margin at every tier.
- Q9 **Provider personas / delivery modes (resolved in design)** — same want must generate different results for solo VA vs team. Provider Profile (`delivery_mode: solo|team`, persona, own capabilities reusing the VA model) + output adaptation matrix + guardrails: `generation-guardrails.md`. Solo flip: matching engine becomes deal self-qualification (skill gaps → train/partner/refer). Guardrails = deterministic-only zones, AI narrative slots, hard gates (assumptions before estimates, human approval before send, banned-phrase filter, traceable-figures-only), versioned as data + audit-logged.

## Design roadmap (order)

1. **D1 — Provider happy path & screens** (start here)
2. **D2 — Domain model**: fields, relations, statuses for the 12 models + `owner` FK
3. **D3 — ROI engine spec**: formulas, scenarios, multi-workflow rollup, worked examples (incl. pastor case)
4. **D4 — Matching rules spec**: hard filters vs soft scoring, verified-vs-claimed weighting, explanation strings
5. **D5 — LLM contracts**: extraction JSON schema, validation, human-confirmation UX, token/cost limits
6. **D6 — Proposal content model**: sections, packages, disclaimers, editing, PDF export
7. **D7 — API & n8n boundary**: what Django exposes, webhook auth, which flows live in n8n
8. **D8 — Commercial tiers & pilot pricing**

## D1 draft — provider happy path (v0, for critique)

1. Dashboard → **New discovery session** (pick existing client or create prospect inline).
2. Session screen: paste call notes/transcript *or* fill structured forms manually → Run extraction.
3. Extraction review: facts as editable form grouped by client info / workflows / problems / goals; each field shows source snippet; missing fields listed as suggested follow-up questions.
4. Workflows captured as ROI input rows: employees, hours/week, hourly cost, current tools, error/delay notes.
5. ROI estimate computed per workflow + rolled up; conservative/expected/optimistic toggle; editable assumptions table shown everywhere.
6. Service recommendations: catalog matches with reasons; prices come only from the catalog; LLM explains, never prices.
7. VA match: rule-based shortlist from the provider's bench with per-skill met/missing, verified vs claimed, rate, availability, timezone, language.
8. Proposal draft: AI writes narrative strictly from validated data; Starter/Growth/Custom packages prefilled from catalog; disclaimers baked in.
9. Human review gate → edit in-app → export PDF. Nothing sends without explicit human action.
10. Proposal tracking: draft/sent/viewed/accepted/declined; outcome feeds back to the session.

## Sources

- [VA Masters](https://vamasters.com) / [n8n Virtual Assistants](https://vamasters.com/n8n-virtual-assistants)
- [Somewhere.com AI automation specialists](https://somewhere.com)
- [Agentra enterprise AI ROI calculator](https://www.agentra.io)
- [EngineerUp AI project ROI framework](https://www.engineerup.com)
