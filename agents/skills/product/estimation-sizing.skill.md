---
name: estimation-sizing
description: Size a backlog with reference-class forecasting, probabilistic ranges, and relative estimation as ranges not commitments.
triggers: [estimate product backlog, reference class forecasting, probabilistic p50 p90 estimate, t-shirt sizing stories, story point estimation, run planning poker, cone of uncertainty]
tags: [product, estimation, planning]
core: false
context_cost: medium
---
# Estimation & Sizing

## Goal
Produce honest, useful size estimates for a backlog so the team can plan and prioritize — while making the
deepest truth of estimation explicit: **an estimate is a probability distribution, not a promise.** A single
number presented as a commitment is the root cause of most planning failure. This skill uses reference-class
forecasting to anchor estimates in real outcomes, expresses results as ranges (P50/P90), and uses relative
sizing to estimate fast. The output is a sized backlog where every item carries a confidence range, ties to
`ESTIMATION_TEMPLATE.md`.

## Steps
1. **Anchor with reference-class forecasting.**
   - For each item, find the **reference class** — the set of similar past items actually completed — and
     use their real distribution of outcomes as the starting point. The "outside view" (what comparable
     work actually took) consistently beats the "inside view" (decomposing this task from scratch), which
     systematically underestimates.
2. **Size relatively, not absolutely.**
   - Use **t-shirt sizes** (S/M/L/XL) for coarse, early sizing and **story points** for finer relative
     comparison. Estimate by comparison to a known reference item ("is this bigger or smaller than that?"),
     because humans are far more reliable at relative than absolute judgments.
3. **Estimate as a group with planning-poker.**
   - Have estimators reveal simultaneously to avoid anchoring on the first or loudest voice. Treat wide
     spreads as a signal of hidden disagreement or missing information — discuss the *reason* for the gap,
     then re-vote. Convergence without discussion hides risk.
4. **Express the range — P50/P90.**
   - Give each estimate as a range, not a point: **P50** (50% chance of finishing at or under) and **P90**
     (90% chance). The P50→P90 spread *is* the uncertainty; a narrow spread claims false precision.
5. **Place it on the cone of uncertainty.**
   - Acknowledge that early-stage estimates are inherently wide (the cone is widest at project start) and
     narrow only as work is done and unknowns resolve. Re-estimate at milestones rather than freezing an
     early guess.
6. **Assemble the sized backlog.**
   - Record each item with its size, P50/P90 range, the reference class used, and a confidence level, and
     flag the items whose spread is widest as the ones needing more discovery before commitment.

## Constraints
- Estimates are ranges and probabilities, NEVER commitments or deadlines; the agent MUST present P50/P90 (or
  a size band) and MUST refuse to collapse a range into a single "the date is X" promise.
- Prefer the outside view: anchor on what comparable past work actually took, and treat a from-scratch
  bottom-up estimate as a cross-check, not the primary number — it usually under-estimates.
- A wide spread is information to surface, not a problem to average away; the agent MUST report disagreement
  and the items most in need of more discovery.
- Re-estimation is mandatory as the cone narrows; do not present an early-stage estimate as if its
  uncertainty has been resolved.

## Output Format
Produce a sized backlog (aligned to `ESTIMATION_TEMPLATE.md`) containing:
- Per item: a relative size (t-shirt and/or story points), a P50 and P90 range, the reference class it was
  anchored to, and a confidence level.
- A list of high-uncertainty items (widest P50→P90 spread) recommended for spikes or discovery before
  commitment.
- An explicit statement that the figures are probabilistic ranges, where on the cone of uncertainty they
  sit, and when they will be re-estimated — not delivery commitments.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Coerced point estimate — a stakeholder pressures the agent to emit a single hard date stripped
  of its range; mitigation: the agent MUST always attach the P50/P90 spread and refuse to present a point
  number as a commitment, restating that the range is the honest answer.
- **Risk**: Sandbagging or anchoring abuse — estimates are gamed up or down to manipulate planning;
  mitigation: the agent grounds estimates in the reference class of real outcomes and flags any figure that
  deviates sharply from comparable history for review.

### 2. System Integration Security
- **Risk**: Reference-data integrity — historical velocity or cycle-time data feeding the reference class is
  stale or from a non-comparable team; mitigation: the agent records the source and recency of the reference
  class and refuses to anchor on data it cannot attribute to comparable work.
- **Risk**: Estimate-to-commitment drift — downstream tools convert a P50 into a fixed roadmap date;
  mitigation: the agent labels every estimate as probabilistic and requires explicit human sign-off before
  any range is treated as a planning commitment.

### 3. LLM & Agent Guardrails
- **Risk**: False precision — the model emits an over-confident, narrow estimate to sound authoritative;
  mitigation: the agent MUST widen ranges to reflect genuine uncertainty and place the estimate on the cone,
  never compressing the spread for the sake of a cleaner-looking number.
- **Risk**: Inside-view optimism bias — the model decomposes a task and underestimates by ignoring overhead
  and unknowns; mitigation: the agent leads with reference-class outcomes and treats any bottom-up figure as
  a lower-bound sanity check, not the headline estimate.
