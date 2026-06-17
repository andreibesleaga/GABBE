---
name: financial-governance
description: Govern product spend with budget tracking, cost showback, unit economics, and cloud cost guardrails.
triggers: [track product budget, cost allocation and showback, calculate cac and ltv, gross margin and unit economics, return on investment analysis, cloud cost guardrails, financial governance summary]
tags: [product, finance, governance]
core: false
context_cost: medium
---
# Financial Governance

## Goal
Give a product or platform team financial discipline: know what is being spent, attribute it to the teams
and products that drive it, prove whether the economics work, and put guardrails in place before costs run
away. The skill spans budget tracking, cost allocation/showback, unit economics (CAC/LTV, gross margin,
ROI), and cloud cost guardrails. The output is a financial governance summary. The honesty rule: financial
figures are only as good as their inputs and time window, so every ratio carries its assumptions and period.

## Steps
1. **Track the budget against actuals.**
   - Set the budget per category and period, then track actual spend versus plan, computing variance and
     burn rate. Surface trajectory ("at current burn, the budget exhausts in N weeks"), not just a snapshot.
2. **Allocate cost and run showback.**
   - Attribute shared and direct costs to the consuming teams, products, or features using a documented
     allocation basis (usage, headcount, tagged resources).
   - Run **showback** (visibility without forced cross-charge) to create accountability; reserve **chargeback**
     for when the org is ready, since premature chargeback drives gaming over good behavior.
3. **Compute unit economics.**
   - **CAC** (cost to acquire a customer) and **LTV** (lifetime value); a healthy business needs LTV
     meaningfully above CAC and a sensible payback period, so always show the LTV:CAC ratio *and* the
     payback months, not LTV alone.
   - **Gross margin** = (revenue − cost of goods/service) ÷ revenue — the structural profitability per unit,
     and the number that tells you if scaling helps or hurts.
4. **Assess ROI honestly.**
   - Compare expected return against cost over a stated horizon. State whether benefits are realized or
     projected; a projected ROI is a forecast carrying uncertainty, not a booked return.
5. **Set cloud cost guardrails.**
   - Establish budgets and threshold alerts, enforce resource tagging for attribution, identify idle/over-
     provisioned resources, and define committed-use or autoscaling policies. Guardrails are preventive
     (alert and limit before overspend), not just after-the-fact reporting.
6. **Assemble the governance summary.**
   - Combine budget status, allocation/showback, unit economics, and guardrails into one summary with
     owners and a review cadence.

## Constraints
- Every ratio (LTV:CAC, gross margin, ROI) MUST be reported with its time window and key assumptions;
  the agent MUST NOT present a unit-economics figure as fact when it rests on projected inputs — label
  realized vs projected explicitly.
- Show LTV:CAC together with payback period and gross margin; the agent MUST NOT present LTV in isolation,
  since a favorable LTV with poor margin or long payback is not actually healthy.
- Cost guardrails are preventive controls, not reports; the plan MUST include thresholds and alerts that
  fire before overspend, not just monthly variance after the fact.
- Showback before chargeback unless the org explicitly opts in; do not impose cross-charges that incentivize
  gaming over genuine efficiency.

## Output Format
Produce a financial governance summary containing:
- Budget vs actuals by category: variance, burn rate, and a runway/trajectory note.
- Cost allocation / showback: the allocation basis and cost attributed to each team/product/feature.
- Unit economics: CAC, LTV, the LTV:CAC ratio, payback period, and gross margin — each with its period and
  assumptions, and realized-vs-projected clearly marked.
- ROI for key initiatives with horizon and the realized/projected flag.
- Cloud cost guardrails: budgets, alert thresholds, tagging coverage, and idle/over-provisioning findings.
- Owners and review cadence.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Flattering-number bias — assumptions are tuned (long LTV horizon, excluded costs) to make
  economics look healthy; mitigation: the agent fixes and exposes the time window and cost inclusions,
  marks projected vs realized, and refuses to publish a ratio without its assumptions.
- **Risk**: Allocation manipulation — costs are shifted off a team to dodge accountability; mitigation: the
  agent uses a documented, consistent allocation basis and flags reallocations that lack a stated rationale.

### 2. System Integration Security
- **Risk**: Sensitive financial-data exposure — budgets, margins, CAC, and contract costs are confidential;
  mitigation: the agent treats the summary as restricted, routes it only to authorized finance/leadership
  audiences, and scrubs sensitive figures from any broadly shared version.
- **Risk**: Unauthorized cost actions — automated guardrails terminate or rescale production resources;
  mitigation: the agent limits automation to alerting and recommendations and requires human approval before
  any spend-affecting infrastructure change.

### 3. LLM & Agent Guardrails
- **Risk**: Hallucinated financials — the model invents a plausible CAC, margin, or ROI figure to complete
  the summary; mitigation: every number must trace to a named source, and the agent labels any value it
  cannot ground as an explicit assumption requiring finance validation.
- **Risk**: False precision and overconfidence — projected returns are presented as certainty; mitigation:
  the agent attaches ranges and confidence to forecasts, separates booked from projected results, and states
  the assumption most likely to break the conclusion.
