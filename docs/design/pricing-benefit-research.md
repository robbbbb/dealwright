# Pricing & benefit research — the "generic calculator" question

*Research note (Robb request, 2026-09-30): "the calculation — the app should create it. As a VA I don't know how to calculate. If we add it per catalog it's very hard for me. Should we create a generic calculator?" — research + lists only; nothing coded.*

The problem: `service-catalog-draft.md` ships hypothesis numbers, but a provider customizing their own catalog faces blank ROI fields (reduction %? revenue effect? setup range?) they can't compute. The fix under consideration: the app **suggests** numbers from a small set of things a VA *does* know (own rate, build hours, operate hours) + a maintained **benchmark table** — never invents, always editable, always labelled estimate.

---

## A. How VA/automation services are actually priced (models + PH market bands)

| # | Model | How it works | When used | PH/market band (2025-26, external) |
|---|---|---|---|---|
| 1 | **Hourly** | rate × hours, billed monthly | general VA work | ₱100–120/hr employer-reported (PayScale, low end); **$4–7/hr ≈ ₱230–410 offshore-typical**; specialized (n8n/automation) **₱370–870/hr** (design-log anchor) |
| 2 | **Monthly retainer (hours package)** | e.g. 20/40/80 hrs per month, cheaper per hour | ongoing support | ₱8k–40k/mo for 20–40 hrs depending on skill |
| 3 | **Two-part: setup + monthly** | one-time build fee + operating/maintenance monthly | automations, pipelines | setup ₱5k–80k by complexity; monthly ₱1.5k–10k (draft's own rows sit inside this) |
| 4 | **Per-project fixed** | scoped deliverable price | portals, dashboards | ₱25k–80k+ (matches draft cat 7) |
| 5 | **Value-based** | % of quantified client benefit (10–30% of first-year value is the common agency heuristic) | consultancies; rare for VAs | n/a — Dealwright's ROI engine makes this *possible* for VAs, which is the differentiator |
| 6 | **Outcome/commission** | paid per recovered lead / closed sale | lead-gen | rare, trust-heavy |

**Where Dealwright already stands:** catalog = model 3 (two-part) + model 4 for custom builds; hourly rate lives on the VA profile; the ROI engine (Card 3) is what makes model 5 accessible. No conflict — two-part pricing is the VA-native default; value-based becomes the *sales story* (via ROI), not necessarily the *price basis*.

**Tool cost note (from research):** self-hosted n8n ≈ $3–15/mo VPS; workflow platforms bill per-task (n8n/Make/Zapier differ wildly at 10k–50k runs/mo). Operating costs should be a *passthrough line* in monthly pricing, not absorbed.

## B. What benefits automation actually delivers the client (benchmark levers)

Every row = a lever the catalog already has a field for. Ranges are **widely-cited industry benchmarks** (external, sourced where marked), to be shipped as *versioned benchmark data* — the app never invents numbers, it selects conservative/mid/optimistic band ends. **All remain estimates, never guarantees** (claims discipline).

### B1. Money levers (revenue side)

| Lever | Typical benchmark | Catalog field | Source quality |
|---|---|---|---|
| Speed-to-lead → conversion | responding <5 min vs 30 min: up to **21× more likely to convert/qualify**; **78% of customers buy from the first responder** | `conversion_uplift_pct` (draft band 10–20% is *conservative* vs the hype — keep conservative) | widely-cited sales-stats compilations (2025-26); directionally solid, magnitudes vary by industry |
| Missed-lead recovery | **~50% of leads never get a second contact attempt**; scattered inquiries lose 10–30% (draft band) | `recover_leads_pct` 10–30 | draft hypothesis + common CRM-cleanup lore; verify per pilot |
| Follow-up persistence | **80% of sales need 5+ follow-ups; ~44% of reps give up after one** | feeds `conversion_uplift_pct` rationale | classic Invesp/Marketing-Donut stats, still cited 2025 |
| No-show recovery | no-show rates typically 15–30%; reminder systems cut them **~30–50%** | `revenue` via session math (slots × value) — mechanism only in catalog | healthcare reminder meta-analyses (SMS), directionally strong |
| Faster cash (DSO) | automated AR reminders: **DSO down ~5–15 days** commonly reported | `dso_days` 5–15 | AR-automation vendor case studies; self-interested source, band kept wide |

### B2. Time levers (labor side → automation + delegation modes)

| Lever | Typical benchmark | Catalog field |
|---|---|---|
| Task-time reduction (automation) | rule-based flows: **40–80% of the task's time** (draft rows: 40–70 support triage, 50–80 data entry, 60–75 podcast/calendar) | `reduction` % pair |
| Hours removed (delegation/ops) | **1–8 hrs/week** depending on cadence (draft rows span this) | `hours_saved` pair |
| Response time | hours → minutes (speed-to-lead above) | ⚠️ no catalog field yet — Card 3 units decision (backlogged) |

### B3. Qualitative (honest, non-financial) — already flagged in catalog
professionalism/consistency, audience growth, reputation protection, retention, "better decisions", single point of contact. These appear in the proposal's non-financial benefits section, never in math.

## C. The generic calculator (concept — NOT built yet)

**Principle:** the VA enters what they *know*; the app derives catalog ranges from formulas + the benchmark table above (versioned data, like guardrails); everything stays editable; every derived figure is labelled an estimate.

### C1. Inputs (things a VA actually knows)

1. **My hourly rate** — already on the VA/profile side (₱250 default band).
2. **Build hours** — "how long does this take me to set up once?" (e.g. 20–40 hrs).
3. **Operate hours/month** — "how many hours/month to babysit it?" (e.g. 4–8 hrs).
4. **Problem type** — pick from the catalog category (maps to a benchmark lever band).
5. *(optional)* Tool costs — ₱/month passthrough (e.g. n8n VPS ₱170–850).

### C2. Formulas (deriving the catalog fields)

| Catalog field | Formula |
|---|---|
| `setup_low/high` | build_hours × rate × **[1.0, 1.5]** (round to clean ₱500s) |
| `monthly_low/high` | (operate_hours × rate × **[1.0, 1.4]** ) + tool_cost |
| `reduction` % / `hours_saved` | from the benchmark band of the chosen problem type (B2) — provider never types a % |
| `revenue_effect` | from lever type + client-side session data (Card 3 computes value; catalog stores only type + band) |
| `delivery_days` | ceil(build_hours / 20)–ceil(build_hours / 12) (solo capacity ≈ 12–20 productive hrs/wk) |

### C3. Worked example — does it reproduce the draft's anchors? (sanity check)

Podcast distribution pipeline, rate ₱400/hr, build 30 hrs, operate 6 hrs/mo:
- setup = 30 × 400 × [1.0, 1.5] = **₱12,000–18,000** → draft says **12–20k** ✓ (overlaps)
- monthly = 6 × 400 × [1.0, 1.4] = **₱2,400–3,360** → draft says **3–6k** (draft adds margin for human-in-loop editing; formula's low end is below draft — margin band could go [1.2, 1.8] for editorial services) ~✓
- reduction = benchmark band for content pipelines = **60–75%** → draft: **60–75%** ✓
- delivery = ceil(30/20)=2 – ceil(30/12)=3 wks → draft: **2–3 wks** ✓

Pastor case cross-check (design-log): 12h/mo × 75% = 9h × ₱300 = ₱2,700/mo labor value → monthly 3–6k = 2.2–4.4× the *client's* saving… ⚠️ actually **below**: client saves ₱2,700/mo and pays ₱3–6k/mo → the honest story there is *consistency + repurposing value*, not labor savings alone. **Flag: draft's pastor pricing only makes sense with the consistency/quality benefit or a lower price band — pilot should test this.** (This is exactly the kind of honesty the value-check in C4 forces.)

### C4. The value check (the guardrail)

After computing, the calculator shows the *client's* side: "at these prices, the client pays ₱X/mo and the estimate says they gain ₱Y/mo (range)" — using the same engine the proposal will use. If price ≥ estimated benefit, the app warns (amber): either the price is too high, the lever is wrong, or the service is genuinely qualitative → switch it to qualitative_value. **The provider never has to trust a number they can't see the origin of.**

### C5. Where it would live (product fit, for later decision)

- "Suggest numbers" helper when adding/editing a catalog Service (admin now; catalog UI later) — pre-fills fields, provider can override any of them.
- Benchmarks table = versioned seed data in git (Tier 2, like the catalog) — `BenchmarkBand(lever_type, low, mid, high, source_note)`.
- No new math in the LLM ever; calculator is pure Python like Card 3.

## D. Decisions needed (the checklist Robb asked to review)

- [ ] **D1:** Add the benchmark table as real data (versioned, git-shipped) — yes/no?
- [ ] **D2:** Margin multipliers: setup [1.0, 1.5] and monthly [1.0, 1.4] default; editorial/human-in-loop services [1.2, 1.8]? Or flat %?
- [ ] **D3:** Response-time lever (hrs→minutes): add catalog field in Card 3, or fold into conversion story? (backlogged)
- [ ] **D4:** Value check threshold: warn when price > 100% of estimated monthly benefit? warn at >80%?
- [ ] **D5:** Calculator scope: catalog-suggestion only (MVP) vs standalone "what should I charge?" page (later)?
- [ ] **D6:** Pastor-case pricing tension (C3 flag): retest price band or lean on consistency story in pilot?
- [ ] **D7:** Tool costs: explicit passthrough line in proposals (transparent) vs absorbed into monthly?

## Sources

- Live search (2026-09-30, DuckDuckGo snippets): PH VA rate guides 2025-26 ($4–7/hr ≈ ₱230–410 offshore-typical; PayScale ₱100–120 employer-reported low end); n8n/Zapier freelancer economics ($50/hr+ billing threshold, $3–15/mo VPS); speed-to-lead stat compilations (21× within 5 min; 78% buy from first responder).
- Repo design-stage research (design-log "Sources"): VA Masters / n8n VAs / Somewhere.com rate pages (₱370–870/hr anchor), Agentra + EngineerUp ROI frameworks.
- `docs/design/service-catalog-draft.md` hypothesis bands (8 categories × levers).
- Classic industry stats from general knowledge (follow-ups 5+, 44% give-up, no-show reminder cuts, DSO bands) — **cited-check before any client-facing use**; internal benchmark bands only.

*Nothing in this doc is a guarantee; every figure is a labelled estimate pending pilot data (claims discipline).*

## E. Worked case: "I want only my churchmates to listen" (Robb, 2026-09-30)

Private-audience podcast (pastor case variant): audience capped by design → **every revenue lever switches off**; ROI = time reclaimed only (12 h/mo × 60–75% = 7–9 h/mo ≈ ₱2,100–2,700 at ₱300/hr) + qualitative (consistency, pastor capacity, accessibility). The app must never project reach/leads/conversion for a private audience.

Implications:
1. **Session intake needs audience intent** (public growth vs private community) — gates which levers the ROI engine may use (Card 3/6 design note).
2. **Private variant is less work → lower band**: no clip engine/captions/SEO/distribution matrix; just edit → private feed/group → congregational email. Tentative: setup ₱8–12k, monthly ₱1.5–2.5k (vs public pipeline 12–20k / 3–6k). Catalog variant or scope toggle — decide with D-checklist.
3. **Value check validation:** public-pipeline pricing (₱3–6k/mo) vs ₱2,700/mo benefit → amber flag (D6 tension again); private-variant ₱2k/mo passes cleanly.
