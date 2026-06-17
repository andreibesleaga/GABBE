---
name: ideation-facilitation
description: Facilitate divergent and convergent ideation to turn a framed problem into a ranked shortlist of concepts.
triggers: [facilitate brainstorming session, how might we framing, crazy eights sketching, scamper ideation, affinity grouping ideas, dot voting convergence, concept selection matrix]
tags: [product, ideation, facilitation]
core: false
context_cost: medium
---
# Ideation Facilitation

## Goal
Take a well-framed problem and run a structured ideation session that first **diverges** (generates a
wide, unconstrained set of ideas) and then **converges** (filters, clusters, and ranks them) into a
defensible shortlist of concepts. The deliberate separation of divergence from convergence is the core
discipline: mixing the two kills volume during generation and lets the loudest voice win during selection.
The output is a ranked concept shortlist, each with a plain-language rationale for why it earned its rank.

## Steps
1. **Frame with How-Might-We (HMW).**
   - Reframe the problem statement as 2-4 HMW questions ("How might we reduce checkout abandonment for
     first-time buyers?"). HMW questions are scoped wide enough to invite many answers but narrow enough
     to stay on-problem.
   - Reject HMW questions that smuggle in a solution ("How might we add a loyalty app?") — they collapse
     the solution space before generation starts.
2. **Diverge — generate volume.**
   - **Crazy-8s**: time-box 8 ideas in 8 minutes, one per fold, to force quantity over polish.
   - **SCAMPER**: prompt each lens deliberately — Substitute, Combine, Adapt, Modify/Magnify, Put to
     another use, Eliminate, Reverse — to push past the first obvious answers.
   - Defer all judgment during this phase; capture every idea verbatim, including weak ones, because they
     seed stronger adjacent ideas.
3. **Cluster with affinity grouping.**
   - Group raw ideas into themes by similarity, then name each cluster. Clustering reveals where thinking
     concentrated and which problem facets were under-explored.
4. **Converge — narrow the field.**
   - **Dot-voting**: give each participant a fixed budget of votes to surface collective preference fast
     and reduce single-voice dominance.
   - Carry forward the top vote-getters plus any high-potential outlier the facilitator flags.
5. **Score with a concept selection matrix.**
   - Score each surviving concept against weighted criteria — typically Desirability, Feasibility,
     Viability, and effort/risk. State the weights explicitly so the ranking is reproducible.
   - Rank by weighted score; never let the matrix override a clear strategic constraint without noting it.
6. **Write the rationale.**
   - For each shortlisted concept, record one or two sentences on why it ranked where it did and the main
     uncertainty that would change its rank.

## Constraints
- Never blend divergence and convergence in the same step — judgment during generation suppresses volume.
- A concept's rank is an informed estimate from named criteria and weights, not a guarantee of success;
  surface the weights and the dominant uncertainty so the ranking can be audited.
- Do not silently drop an outlier idea the group rated low — flag it, because under-voted ideas are often
  the genuinely novel ones.
- Quantity precedes quality: a thin idea pool produces a weak shortlist regardless of how good the
  convergence method is.

## Output Format
Produce a ranked concept shortlist containing:
- The HMW question(s) the session addressed.
- For each shortlisted concept: a short name, a one-line description, its weighted matrix score, and a
  one-to-two-sentence rationale naming the key uncertainty.
- The named selection criteria and their weights, so the ranking is reproducible.
- A short "parked ideas" note listing strong outliers held back for a later round.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Premature convergence — a stakeholder pushes a pet idea to the top before divergence runs, so
  the shortlist merely launders a pre-made decision; mitigation: the agent MUST complete a divergence pass
  and record idea volume before any scoring, and refuse to produce a ranking from a single seeded idea.
- **Risk**: Fabricated rationale — the agent invents plausible-sounding justifications for ranks; mitigation:
  every rationale MUST trace to the stated criteria and weights, and the agent labels any rank it cannot
  ground as "low-confidence, needs validation."

### 2. System Integration Security
- **Risk**: Idea provenance leakage — raw ideation logs may quote confidential roadmaps or named customers;
  mitigation: the agent sanitizes participant-attributed and customer-identifying content before the
  shortlist leaves the session, keeping raw notes in a restricted working artifact only.
- **Risk**: Auto-implementation of unvetted concepts — a downstream coding agent treats a brainstormed
  concept as an approved spec; mitigation: the agent watermarks the shortlist as DRAFT/UNVALIDATED and
  states that no concept is build-ready until it passes a separate assessment such as `opportunity-assessment.skill`.

### 3. LLM & Agent Guardrails
- **Risk**: Representation bias — the model defaults to ideas serving a narrow, high-bandwidth user and
  ignores accessibility or low-resource contexts; mitigation: the agent MUST deliberately generate at least
  one idea targeting an under-served or constrained user before converging.
- **Risk**: Harmful ideation — SCAMPER or "worst possible idea" prompts surface privacy-violating or
  manipulative concepts; mitigation: the agent flags such concepts as out-of-bounds rather than ranking
  them, and never advances a concept whose value depends on deceiving or surveilling users.
