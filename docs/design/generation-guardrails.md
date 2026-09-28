# Provider Profile & Generation Guardrails — Design v1

Answers two design questions (2026-09-28):
1. The same client want must generate **different results for different providers** — a solo VA's proposal must not contain a "matched assistant" card.
2. Generation must be governed by **rules, not vibes** — exact outputs need a provider profile for context and guardrails for constraints.

## Part 1 — Provider Profile (set at onboarding, editable)

| Field | Values / shape | Drives |
|---|---|---|
| `delivery_mode` | `solo` \| `team` | Section 4 rendering, matching behavior |
| `persona` | VA · automation freelancer · agency · dev agency · consultant | Catalog defaults, proposal tone, package templates |
| `capabilities` | same skill + level + evidence model as VAs (reuse VACapability) | Solo: "About me" card + deal qualification. Team: owner skills irrelevant |
| `bench` | 0..n VA profiles (team mode) | Matching engine |
| `catalog` | default seed + overrides | Prices, services, timelines in output |
| `packages` | which tiers offered (Starter/Growth/Custom defaults) | Pricing section |
| `branding` | name, tagline, accent color (MVP: name only) | Proposal cover |
| `safety prefs` | approval-before-send (default ON), disclaimer block (always ON) | Send gate |

**Key symmetry:** a solo provider's own profile *is* a capability profile. One model powers both "About me" (solo) and bench matching (team). No duplicate systems.

## Part 2 — How output adapts by provider type

| Generated section | Solo VA | Solo freelancer/consultant | Team/agency |
|---|---|---|---|
| 1. What you told us | same | same | same |
| 2. Recommended solution | services + **I deliver them** | services + I build, recommend ongoing ops | services + team delivery |
| 3. Estimates | same engine (mode per case) | same | same |
| 4. Assistant/specialist | **"About me" — my verified skills, rate, hours**; or omitted for pure-automation deals | "Specialist" = me (build) | Matched VA card from bench |
| 5. Packages | my hours + setup fees | project fees + retainer | full menu |
| 6. Match engine use | **Deal qualification:** do *my* skills cover this want? → gaps = train / partner / refer out | same (qualification) | shortlist bench VAs with reasons |
| 7. Timeline | my calendar | my pipeline | team capacity |

**Solo flip — matching becomes self-qualification.** Same rules engine, pointed at one profile: client want → required skills → check *my* capabilities → verdict + gap list. Gaps are actionable: "learn podcast admin (2 weeks)", "partner with a Django dev", or "decline / refer and earn trust". This is a selling feature for solo users, not a missing feature.

## Part 3 — Generation guardrails (the "rules md", enforced in code)

**Deterministic-only zones — AI never writes these, ever:**
- Prices (from catalog only)
- ROI math (Python engine only)
- Skill levels & verification claims (from profile evidence only)
- Timelines (from catalog)
- Assumptions (recorded, displayed, versioned)

**AI-permitted zones — narrative inside slots:**
- Restating client goals in their own words
- Explaining what the numbers mean in plain language
- Solution story, package descriptions, next-step wording
Always fed validated structured data; never a source of figures.

**Hard gates (block generation/sending):**
1. No estimate renders without its assumptions recorded.
2. No proposal sends without human approval click (never auto-send).
3. Protected characteristics never appear in matching, copy, or pricing logic.
4. Missing critical info → follow-up questions generated, not guessed values.
5. Banned-phrase filter on AI output: "guaranteed", "100%", "risk-free", "be assured of savings", superlatives about outcomes. Fail → regenerate with flag, log it.
6. Every money/time figure in AI text must cross-reference a structured field (extraction validates; untraceable numbers are stripped).

**Persona adaptation rules:**
- `delivery_mode=solo` → section 4 renders "About me" or is omitted; bench language ("your assistant", "our team") banned from copy.
- `delivery_mode=team` with empty bench → section 4 omitted with a nudge to onboard VAs.
- Persona sets tone/taxonomy of the catalog subset offered.

**Where this lives at build time:** guardrails as versioned data (YAML/JSON ruleset) + Django validators + prompt templates with the same constraints embedded; every generated proposal logs which guardrail version produced it (audit trail). During design, this document is the source of truth.

## Open items
- Solo VA + client wants skills they lack: how aggressive should the upsell/training suggestion be in client-facing copy? (Lean: gap noted neutrally as "coordinated with a specialist partner".)
- Should solo providers get a public profile page later (lead-gen)? Out of MVP scope, park it.
