---
name: opportunity-assessment
description: "Assess a product opportunity with Wardley mapping, market sizing, a North-Star metric, and RICE-ranked bets. Use when: assess product opportunity, wardley map value chain, size market tam sam som, define north star metric, apply heart framework, rice prioritization of bets, write opportunity brief."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/product/opportunity-assessment.skill.md"
  tags: "product, strategy, prioritization"
  core: "false"
  context_cost: "medium"
---
# Opportunity Assessment

## Goal
Evaluate whether a product opportunity is worth pursuing and which specific bets to make first. The skill
combines four lenses: a **Wardley map** to understand where value sits and how mature each component is,
**market sizing** to bound the prize, a **North-Star metric plus HEART** to define what success means, and
**RICE** to rank candidate bets. The output is an opportunity brief that an investment-minded reader can
act on — honest about assumptions, because every number here is a modeled estimate, not a measured fact.

## Steps
1. **Map the value chain (Wardley).**
   - Place user-visible needs at the top of the value chain and trace the components they depend on
     downward (the anchor-to-component structure).
   - Position each component along the evolution axis: Genesis → Custom-built → Product/rental → Commodity.
     This reveals where to build (novel, defensible) versus buy (commodity), and where the strategic
     opportunity actually lives.
2. **Size the market (TAM/SAM/SOM).**
   - **TAM** (total addressable market): the whole demand if you captured 100%.
   - **SAM** (serviceable addressable market): the slice your model can actually serve.
   - **SOM** (serviceable obtainable market): the share you can realistically win near-term.
   - State each as a range with its core assumptions; sizing is a triangulation of imperfect inputs, so
     show top-down and bottom-up estimates where possible and reconcile the gap.
3. **Define success — North-Star metric + HEART.**
   - Choose one **North-Star metric** that captures the core value delivered to users (a leading indicator
     of durable growth), not a vanity count.
   - Use **HEART** — Happiness, Engagement, Adoption, Retention, Task success — to derive the supporting
     signals and their Goals-Signals-Metrics so the North-Star is not measured in isolation.
4. **Enumerate and rank bets (RICE).**
   - List candidate bets, then score each: **Reach** (how many affected per period), **Impact** (effect
     size per user), **Confidence** (how sure you are, in %), **Effort** (person-time). Score = (Reach ×
     Impact × Confidence) ÷ Effort.
   - Confidence is the honesty dial: low-evidence bets MUST take a low confidence multiplier so speculation
     cannot outrank validated work.
5. **Assemble the brief.**
   - Synthesize map, sizing, success definition, and ranked bets into a single brief with an explicit
     recommendation and the assumptions it stands on.

## Constraints
- TAM/SAM/SOM figures are modeled estimates with error bars, never commitments; the agent MUST state the
  assumptions and show ranges rather than single confident numbers.
- RICE Confidence MUST honestly reflect evidence strength; the agent MUST NOT inflate Confidence to push a
  favored bet up the ranking, and flags any score resting on untested assumptions.
- The North-Star metric must measure delivered user value, not a vanity or gameable count; reject metrics
  that rise while users are worse off.
- A Wardley map is a hypothesis about the landscape, not ground truth; label uncertain component positions
  as such.

## Output Format
Produce an opportunity brief containing:
- A Wardley map description: the value chain with each component's evolution stage and the build/buy
  implication.
- TAM/SAM/SOM as ranges with their key assumptions and the top-down vs bottom-up reconciliation.
- The North-Star metric plus the HEART supporting signals (Goals-Signals-Metrics).
- A RICE-ranked table of candidate bets with each factor shown, the score, and a confidence note.
- A clear recommendation (pursue / pursue-with-conditions / decline) with the assumptions it depends on.

## Limits and safety
- Keep every sizing assumption and RICE weight visible; give ranges, not one headline number.
- Every figure traces to a named input; otherwise label it "assumption to validate".
- The brief is a decision input: it needs human sign-off, and commitment goes through a financial gate such as `financial-governance.skill`.
- Mark a brief that uses internal financials or non-public data as confidential and scrub it before sharing.
