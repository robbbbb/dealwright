# Service Catalog — Draft v1 (design stage)

The catalog is the platform's engine room: problems map to services deterministically, services carry the ROI parameters and prices (never AI-generated), and required VA skills feed matching. This is the default seed catalog shipped with the platform; providers edit it to their own offerings.

All prices are **hypotheses in PHP** to test in pilots (anchored on: pastor case PHP 12–20k setup / 3–6k monthly; PH n8n-capable VA market ≈ PHP 370–870/hr).

## Catalog design rules

1. **Quantifier rule.** Every service declares machine-readable ROI parameters: a `reduction_range` (time) and/or a `revenue_effect` (leads recovered, conversion uplift, avg sale, days-sales-outstanding). Services that can't be quantified honestly are tagged `qualitative-value` — they appear in the proposal's non-financial benefits section, never in the math.
2. **Two-part pricing.** Setup (one-time build) + monthly retainer (VA operates/monitors). `Custom quote` allowed. *("Monthly" = retainer — Robb vocabulary decision, 2026-09-30.)*
3. **Skills tag.** Each service lists required VA skills + minimum level (e.g., Django = Verified only) → feeds rule-based matching.
4. **Claims discipline.** Every money figure is "estimated"; ranges not points; three scenarios derive from the range ends.
5. **Delivery estimate** per service (sets timeline section of proposals).

## The two levers (how clients get value)

**Money — 4 types:**
- **Cut cost** — labor hours × hourly rate
- **Recover revenue** — leads/no-shows/quotes currently being lost
- **Grow revenue** — faster response, more follow-up touches, better conversion
- **Speed cash** — invoices paid sooner (DSO down)

**Time — 3 types:**
- Hours per week removed
- % reduction per task/episode
- Response time (hours → minutes)

---

## 1. Lead capture & CRM automation
*Promise: stop losing inquiries that already paid to reach you.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Lead centralization funnel (FB/IG/WhatsApp/web → CRM) | Inquiries scattered; leads lost in DMs | −3–6 hrs/wk | Recover est. 10–30% of missed leads | 8–15k / 2–4k | 1–2 wks |
| Speed-to-lead auto-response + booking link | Slow replies lose hot buyers | Response: hrs → minutes | Consult conversion +est. 10–20% | 5–10k / 1.5–3k | 1 wk |
| CRM pipeline setup & cleanup | Spreadsheet chaos, dropped follow-ups | −2–4 hrs/wk | Fewer dropped deals | 6–12k / 1.5–3k | 1–2 wks |

VA skills: CRM management (GHL/Zoho/HubSpot), form builders, n8n monitoring.

## 2. Automated follow-ups (email/SMS/Messenger)
*Promise: most sales need 5+ touches — nobody does them by hand.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Follow-up sequences (5–9 touches, multi-channel) | Leads go cold after 1 message | −2–5 hrs/wk | Recover cold leads → sales | 7–14k / 2–4k | 1–2 wks |
| Appointment reminders & confirmations | No-shows waste paid slots | −1–2 hrs/wk | Recovered slots × avg value | 4–8k / 1.5–3k | 1 wk |
| Quote & proposal chase flow | Unsigned quotes, awkward chasing | −1–2 hrs/wk | Faster closes | 5–9k / 1.5–3k | 1 wk |

VA skills: email marketing, Messenger/WhatsApp tools, copy review.

## 3. Customer support & onboarding
*Promise: answer the same question once, forever.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| FAQ triage inbox + auto-responder | Same questions answered daily | −40–70% support hrs | VA hours reallocated to revenue work | 6–12k / 2–4k | 1–2 wks |
| Client onboarding workflow (docs, welcome, kickoff) | First-30-day churn, doc chaos | −3–5 hrs/client | Retention (qualitative + churn cost) | 8–15k / 2–4k | 2 wks |
| Review & feedback collection | Silent unhappy clients, no social proof | −1 hr/wk | Retention + reputation (qualitative) | 4–8k / 1–2k | 1 wk |

VA skills: customer support, helpdesk tools, empathy-tone review.

## 4. Reporting, invoices, dashboards & data entry
*Promise: stop paying people to move data between systems.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Invoice + payment reminder automation | Late payments, awkward chasing | −2–3 hrs/wk | DSO down est. 5–15 days (cash) | 6–12k / 1.5–3k | 1 wk |
| Weekly auto-reports (sales/pipeline/content) | Copy-paste spreadsheet hours | −3–8 hrs/wk | Labor savings | 8–18k / 2–4k | 1–2 wks |
| Data sync & entry automation (form → system) | Rekeying same data in 3 places | −50–80% entry time | Labor + fewer costly errors | 6–14k / 1.5–3k | 1–2 wks |

VA skills: spreadsheets, basic bookkeeping, n8n monitoring.

## 5. Podcast & content distribution
*Promise: publish once, be everywhere — with human approval.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Podcast distribution pipeline (episode → email/captions/questions → approval → channels) | Hours of repurposing per episode; inconsistent delivery | −60–75% per episode | Labor value + consistency (consistency = qualitative) | 12–20k / 3–6k | 2–3 wks |
| Content repurposing engine (1 long video → clips/quotes/blog) | Content dies after one post | −50–70% repurposing time | Labor savings | 10–18k / 3–5k | 2 wks |
| Newsletter production automation | Irregular, manual sends | −2–4 hrs/issue | Audience retention (qualitative) | 6–12k / 2–4k | 1–2 wks |

VA skills: podcast admin, AI content review, email marketing, sensitive-content care.

## 6. Social media management & scheduling
*Promise: consistent presence without daily drain.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Batch scheduling + content calendar (VA-operated) | Daily posting drain, on-and-off presence | −3–6 hrs/wk | Audience growth (qualitative) | 5–10k / 2.5–5k | 1 wk |
| DM & comment triage (VA + auto-routes) | Unanswered DMs = lost sales chats | −2–4 hrs/wk | DM → sale conversion | 5–9k / 2–4k | 1 wk |
| Mention & keyword alerts | Missed complaints/opportunities | −1 hr/wk | Reputation protection (qualitative) | 4–7k / 1–2k | 1 wk |

VA skills: social management, community engagement, copy.

## 7. Custom Django dashboards, portals & internal tools
*Promise: one place for the numbers, files, and approvals.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Client portal (files, invoices, status) | "Where's my file?" email chains | −2–4 hrs/wk both sides | Labor + professionalism (qualitative) | 30–60k / 3–6k | 3–5 wks |
| Ops dashboard (single live view of the business) | Flying blind; ad-hoc report requests | −2–5 hrs/wk | Better decisions (qualitative) | 25–50k / 2–4k | 3–4 wks |
| Internal tool / approval workflow (custom) | Manual approval chains, spreadsheet "systems" | −50–70% process time | Labor + error cost | 30–80k custom | 3–6 wks |

VA/dev skills: Django/full-stack — **Verified level only**; delivery by the specialist, not the VA.

## 8. Personal productivity ops *(new — from the LF case)*
*Promise: one reliable person + quiet automation behind them.*

| Service | Solves | Time lever | Money lever | Setup / Monthly | Delivers |
|---|---|---|---|---|---|
| Calendar & reminder system (n8n + Google Calendar) | Missed deadlines, mental load | −60–75% reminder busywork | Client's reclaimed time × their rate | 6–9k / 1–2k | 1 wk |
| Task & document hub (structured Drive/Notion) | Scattered lists and files | −2–4 hrs/wk | Reclaimed time | 4–7k / 1–2k | 1 wk |
| Self-service booking link + confirmations | Back-and-forth scheduling | −2–3 hrs/wk | Reclaimed time | 3–5k / 1k | 1 wk |
| Personal assistant service (staffing) | Chaos; no single point of contact | Client hours freed (delegation ROI) | Delegation net = freed time value − VA cost | — / by hrs | immediate |

VA skills: calendar management, task systems, calls & bookings, discretion.

---

## Coverage check — every client problem lands somewhere

- "We lose leads" → Cat 1 + 2 (recover + grow)
- "We're slow to answer" → Cat 1, 3 (response time)
- "Admin eats our week" → Cat 4, 8 (hours)
- "Clients churn / complain quietly" → Cat 3 (retention)
- "Payments come late" → Cat 4 (cash speed)
- "Our content dies after one post" → Cat 5, 6
- "We have no single view / files everywhere" → Cat 7
- "My personal life is chaos" → Cat 8 (delegation)

## Open items

- Should the seed catalog ship bilingual (EN/PH) or EN-only for MVP? → lean EN-only.
- Category 7 (Django builds) pricing is the least tested — pilot first or mark "custom quote only" initially?
- Map each service to a default n8n workflow template (later, after pilot).
