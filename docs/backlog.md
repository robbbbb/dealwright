# Dealwright — backlog & open items

Registry of deferred work and open items. Status lines updated as items move. Design-stage residuals recorded 2026-09-28 at project creation.

## Pre-launch checklist (before first paying user)

- [ ] **Domain: buy `dealwright.io`** (available as of 2026-09-28; `.com`/`.app` parked — revisit later). Status: open.
- [ ] **Trademark check** — IPOPHL classes 9/35/42 at DTI/SEC business registration; USPTO only if international. Status: open.
- [ ] **Railway region selection** — closest to PH; decided at Card 11 deploy. Status: open.
- [ ] **Verify Railway Postgres backup policy per plan** — if insufficient, the n8n off-site pg_dump flow (system-design §9b) becomes mandatory, not stopgap. Status: open.
- [ ] **Pricing page + checkout** — tiers set (₱399/₱899/₱1,990, Q10 in design log); page mockup and billing integration are post-MVP. Status: deferred.

## Post-pilot / deferred product work

- Quality-mode toggle (Fast = Flash-writes ₱0.10 vs Premium = GLM-5.3 ₱0.52) — decide from pilot usage data. Status: deferred.
- Prompt caching of static blocks (catalog digest, guardrails) — −80% writer input cost. Status: deferred.
- Background worker service (huey/redis) for extraction + PDF — trigger: visible queueing or RAM >70%. Seam designed (system-design §6). Status: deferred.
- USD pricing tiers ($8/$18/$39) + currency-per-account when going international. Status: deferred.
- i18n: EN-only for MVP; PH bilingual catalog revisit. Status: deferred.
- Django-build pricing (catalog cat. 7) unvalidated — pilot before posting fixed prices, else "custom quote only". Status: open.
- Map each catalog service to a default n8n workflow template. Status: deferred.
- Solo provider public profile page (lead-gen) — parked. Status: out of MVP scope.
- n8n-hosted backup orchestration flow (nightly pg_dump push off-site + failure alert). Status: deferred (stopgap runbook in Card 11).

## Out of scope (per handoff; do not build)

Live call transcription · automated interviews · marketplace payments · public job board · mobile apps · complex AI ranking / autonomous hiring · multi-agent workflows · automatic proposal sending without human review · advanced analytics · billing/subscriptions in MVP.
