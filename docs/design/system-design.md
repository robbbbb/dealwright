# System Design — Railway deployment & capacity (2026-09-28)

Deployment target moved from "VPS" to **Railway** (Robb on Hobby, $5/mo). Research + capacity math below. Dev stays local on the 16 GiB machine; prod on Railway.

## 1. Railway plan facts (researched 2026-09-28)

| | Hobby | Pro |
|---|---|---|
| Price | $5/mo, includes $5 usage | $20/mo/seat, includes $20 usage |
| Billing beyond credit | metered pay-as-you-go | metered pay-as-you-go |
| Max per service | up to 8 vCPU / 8 GB RAM | no practical cap |
| App sleeping | **opt-in** ("Serverless"), never automatic | same |
| Team features, autoscaling, metrics | no | yes |

Metered rates (third-party reported, self-consistent): **vCPU ≈ $20/vCPU-month** (billed per minute of actual use), **RAM ≈ $10/GB-month**, egress ≈ $0.05–0.15/GB, volumes ≈ $0.25/GB-mo. Railway meters actual CPU utilization + RAM used — an idle app costs RAM only.

**Railway does not bill or limit per request.** Request capacity is a function of the service size we run, so we derive it below.

## 2. Our app's request profile (why we're cheap to host)

- Server-rendered Django + HTMX: every page is ~50–150 ms CPU. No SPA, no websocket, no file streaming.
- Only two "heavy" operations: LLM extraction (2–10 s **wall-time, near-zero CPU** — the worker just waits on z.ai) and WeasyPrint PDF (1–5 s CPU, memory spike).
- Traffic is work-session based, not consumer-facing: short bursts when a provider prepares a proposal.

## 2b. Traffic character: read-heavy (~85/15) with bursty writes (2026-09-28)

- Reads: provider working sessions + **proposal share links (biggest read surface — unauthenticated client/forwarding views, 5–20 views per proposal)**.
- Writes: rare bursts — one proposal generation ≈ 100–200 rows (facts+snippets, estimate+assumptions, matches, version, audit, LLM usage); ~250 bursts/day at 1k users ≈ 50k rows/day peak. Audit/usage logging is deliberate write amplification for trust; volume stays trivial.
- Consequences: no cache layer (no Redis/materialized counters); index share-token lookup + owner-scoped lists; share-link views get select_related + cache headers + light rate limit (only stranger-facing path); nightly pg_dump trivial (DB ≈ 100–500 MB/yr at 1k users). Confirms small-Railway-Postgres sizing.



## 3. Traffic model at 1,000 users

| Assumption | Value |
|---|---|
| Registered users | 1,000 |
| Daily active (10–20% typical B2B SaaS) | 100–200 |
| Requests per active session (pages + HTMX partials) | 30–60 |
| **Requests/day** | **~6,000–12,000** (avg ~0.1 req/s) |
| Evening peak (PH hours) | ~1–3 req/s |
| LLM extractions | ~5 per user/mo → ~5,000/mo (~1 every 10 min average, clustered) |
| PDFs | ~1 per proposal → ~5,000/mo |

## 4. Request capacity per configuration (not per plan)

One Gunicorn sync worker handles ~10–20 light requests/sec. A 3-worker Django service (~0.5 vCPU, 512 MB):

- **Burst capacity ≈ 30–60 req/s ≈ 2–4M requests/day theoretical.**
- Our 1k-user peak (~3 req/s) uses **<10% of one worker**.
- Conclusion: **request volume cannot be the reason to upgrade plans before ~10k+ active users.** The real caps are (a) RAM footprint, (b) workers blocked during LLM waits, (c) PDF memory spikes — all config/queue problems, not plan-size problems.

## 5. Topology

```
Railway project "dealwright"
├── web        Django + Gunicorn (2–3 sync workers, 60 s timeout)
│              + Whitenoise (static from image, no CDN needed)
│              + Railway volume (/data: generated PDFs)  [volume ≈ $0.25/GB-mo, tiny]
├── postgres   Railway Postgres plugin (start small; single instance)
└── (later)    worker service — huey/redis for extraction+PDF queue
               NOT in MVP; seam designed now (see §6)

n8n stays where it lives now (local). It talks to web via token-auth webhooks only.
```

Config rules: `restart` on crash automatic (Railway restart policy); **do NOT enable Serverless/app-sleeping on prod web** (cold start on a client-facing proposal link kills trust); fine on staging. `--max-requests 1000 --max-requests-jitter 100` on Gunicorn to curb slow leaks. `CONN_MAX_AGE=60`. Secrets only via Railway env vars.

## 6. The one real bottleneck: LLM waits inside request workers

MVP choice: extraction runs **synchronously** in-request with HTMX spinner (3 workers ≈ 3 concurrent extractions; at 1k users the odds of overlap are low). The code seam: extraction + PDF live behind a service-layer function (`run_extraction(session)`) so swapping to a background worker later is one small card, not a refactor.

Upgrade trigger: when concurrent extraction waits visibly queue other users (watch p95 on session pages) → add worker service (+$5–8/mo usage).

## 6b. Latency budget (2026-09-28)

| Class | p95 target | Notes |
|---|---|---|
| HTMX partials | < 200 ms | must feel instant |
| Working pages / saves | < 500 ms–1 s | kill N+1 on dashboard lists (>3 s = bug, not infra) |
| Matching run | < 500 ms | pure Python |
| PDF export | < 5 s | WeasyPrint, spinner |
| LLM extraction | 10–20 s OK, 30 s timeout | ~700 out tokens ≈ 12–18 s at Flash speeds — physics; requires progress UI with expectation-setting copy |
| Proposal writing | 15–35 s OK, 60 s timeout | ~1,100 out tokens ≈ 18–30 s |
| **Share-link (client-facing)** | **< 1.5 s, ceiling 2 s** | the product's storefront; drives region choice + no app-sleeping |

Non-negotiables: app-sleeping stays OFF (cold start = 5–10 s on a client's click reads as broken); every AI wait shows labeled progress ("usually ~15 s" buys patience; silent hang gets 3 s); Gunicorn `--timeout 65`. Fixed latency floor = Railway region RTT from PH (~200 ms us-west / ~300 ms us-east) on every request — choose closest region at Card 11. LLM calls dominate all other latency combined; the background-worker seam exists so their UX budget never changes, only robustness improves.



## 7. Cost projection (usage-metered, USD)

| Stage | Web | Postgres | Total/mo | Plan |
|---|---|---|---|---|
| Pilot, <50 users | $3–4 (2 workers, ~300 MB) | $1.5–2.5 | **$5–7** | Hobby (credit covers most) |
| 100–1,000 users | $5–8 | $3–5 | **$8–13** | Hobby w/ small overage, or Pro for headroom |
| 1k+ with worker svc | $5–8 + $5–8 | $5–8 | **$15–24** | Pro natural home |

Worst-case check: even 2× these estimates ≈ ₱700–1,400/mo against 1,000 × ₱399 potential MRR (₱399k). Infra ≈ 0.3% of revenue at scale. **Never a blocker.**

## 8. Upgrade triggers (when to move, decided by data not fear)

1. Hobby → add worker service: extraction queuing visible or PDF spikes push RAM > 70% of limit.
2. → Pro ($20): monthly usage consistently > ~$15, or need for team seats/metrics, or DB approaching ~1 GB / connection pressure.
3. → Managed Postgres off-Railway: only if backup/retention needs outgrow plugin (verify current backup policy per plan — open item below).

## 9b. Durability: what we can never lose (2026-09-28)

**Principle: protect records, not derivations.** The deterministic design (math/rendering/rules never own data) makes artifacts re-derivable, shrinking the true backup surface.

- **Tier 0 (never lose):** accounts, provider profiles + custom catalogs, client records, **raw discovery notes**, **ProposalVersion snapshots** (edited narrative + frozen as-shown figures + package + template/guardrail version — deliberately denormalized; quotes freeze prices), proposal outcomes (the assumptions moat), VA verification records.
- **Tier 1 (painful, reconstructible):** extracted facts (re-run extraction ₱0.05 + re-confirm), drafts, LLM usage logs.
- **Tier 2 (regenerable by design — no backup):** PDF/HTML renders (cache of a ProposalVersion), match results, estimates, seed catalog (git). Rationale: human edits are irreproducible and the writer model is nondeterministic → only the snapshot preserves what the client saw; the render never does. Optional first-month debug flag: log raw LLM responses for validation forensics.

Backup = 3-2-1: live Postgres (1) → nightly `pg_dump` to volume via scheduled job (2) → **off-site push (3, the one that matters)** — object storage or Drive, n8n flow is a natural fit with failure alerts. Retention 7d/4w/6m. **Monthly restore test into staging** (untested backup = hope, not backup). Keep Postgres durability defaults on. In-app protections: soft-delete/archive only for clients/VAs/proposals (no hard deletes of business records); sent proposals immutable. Meta: 2FA on Railway/z.ai/domain registrar — losing access = losing data.



## 9. Risks & open items

- **Backup policy on Railway Postgres per plan** — verify retention before pilot; stopgap: nightly `pg_dump` to volume + weekly manual download (documented runbook).
- WeasyPrint memory spikes: cap proposal length; if RAM issues appear, move PDF to worker service (same seam as §6).
- Single-region latency for PH users: fine (Railway regions include close options); measure in pilot.
- z.ai API is external dependency: timeouts + 1 retry + graceful "try again" state in UI (designed in Card 6).

## 10. Changes to the build plan

- Card 0: Postgres = Railway plugin (local dev: local Postgres or Railway via env); Dockerfile + railway.toml in repo from day one; `ALLOWED_HOSTS` + Railway domain.
- Card 11: pilot deploy = Railway Hobby project, not a VPS; runbook includes backup stopgap.
