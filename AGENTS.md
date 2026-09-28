# Dealwright — project instructions

Read the user defaults at `~/.zcode/AGENTS.md` first; this file narrows them for this repository.

## What this project is

Dealwright: Django SaaS that turns discovery-call notes into ROI estimates, service recommendations, VA matches, and client-ready proposals. Working name locked 2026-09-28; repo `robbbbb/dealwright`. Design complete; build follows `docs/design/mvp-build-plan.md` card by card.

## Rules of engagement

1. **Read `docs/design/design-log.md` before changing anything.** Every load-bearing decision is recorded there with rationale. Do not relitigate locked decisions mid-card; challenge them between cards if new evidence appears.
2. **One card per fresh session**, sized per the build plan. Hand off only at card boundaries using a committed handoff block. The harness's context auto-compaction is the backstop, not scheduled handoffs.
3. **The builder never approves their own work.** Each card ends: tests green → typed review-dispatch card committed → fresh GLM reviewer subagent (read-only, runs gates) → verdict + disposition recorded in the spec/task registry. CHANGES REQUIRED = fix + fresh pass. If no subagent can be spawned, leave the dispatch card for Robb.
4. **Coverage tiers:** ROI engine / matching / LLM validation 95–100%; catalog & profile management 80–85%; templates & UI 40–50% smoke only.
5. **Financial and claim discipline is the product.** Python computes all money; the LLM extracts and narrates only; every client-facing figure traces to a stored field; banned-phrase filter always on; estimates are labelled estimates. Protected personal characteristics do not exist in the schema.
6. **Secrets** live in env vars / Railway config. Never paste tokens into chat, never echo values.

## Design system (canonical)

**Entry point for ALL design work:** open `docs/brand/brand-preview.html` — `file:///home/robbb/dealwright/docs/brand/brand-preview.html` — logo assets, core palette, usage principles, and links to everything else.

- **Tokens & components:** `docs/mockups/theme.html` is the full reference. Use its `--dw-*` CSS variables verbatim; never hardcode new colors or fonts.
- **Screens:** `docs/mockups/index.html` is the gallery of every mocked screen.
- **Logo files** (`docs/brand/`): `logo-mark.svg` (thin tracked "DW" on flat gold #B79121), `logo-horizontal.svg` (ink wordmark, light surfaces), `logo-horizontal-light.svg` (white wordmark, dark surfaces), `favicon.svg`. Glyphs are system-font `<text>` — outline to paths before production PDF use.
- **Chip semantics are product rules, not styling:** green = verified/accepted, amber = "estimate" (always), gold = premium only, red = gaps/errors, teal = neutral info. Never violate these mappings in UI work.
- Theme decisions live in `docs/design/design-log.md` (Q12); challenge them between cards, not mid-card.

## Style guide

HackSoft Django Styleguide, adapted for Dealwright — see `docs/styleguide.md` (read before first code change in any domain app): business logic in `services.py`, queries in `selectors.py`, thin views, forms validate input only, `full_clean()` in services before save, `transaction.atomic` around multi-write services, no signals for business logic, templates presentation-only, type hints everywhere. Deviations need a design-log entry.

## Conventions

- Django + Postgres + HTMX; templates server-rendered; Django admin acceptable for catalog/bench management in MVP.
- TDD: smallest test that proves one behavior through public APIs; delete implementation-coupled tests.
- Commits: conventional style, one logical change; card completion requires the standard delivery report (change summary, task number, test plan with real evidence, affected pages, success verification, docs updated, branch/PR link — no `[TODO]` fields).
- `docs/backlog.md` records discovered residuals — never leave them only in chat.
