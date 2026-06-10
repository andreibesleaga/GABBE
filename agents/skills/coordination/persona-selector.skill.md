---
name: persona-selector
description: Dynamically rank and select the best Loki persona(s) per task, enable contractor-style persona-to-persona delegation and persona-to-skill use, consensus voting for high-stakes calls, and bounded self-refinement — all cost-gated
triggers: [persona selector, best persona, which agent, pick persona, delegate to persona, route task, assign persona, who should do this, persona voting]
when_to_use: "Use this when the task involves: persona selector; best persona; which agent; pick persona; delegate to persona; route task; assign persona; who should do this; persona voting."
tags: [coordination]
context_cost: medium
---
# Persona-Selector Skill

## Goal
Pick the **best persona(s)** for each task instead of relying only on the fixed per-phase assignments in `loki-mode.skill`. The phase defaults remain the baseline; this skill lets the orchestrator adapt — choosing a more relevant persona, tiering by cost, delegating between personas under a contract, voting on high-stakes decisions, and letting personas refine themselves within bounds. Everything here is cost-gated by `GABBE_AUTONOMY` + budget.

## Selection (semantic routing — markdown-heuristic by default)
Rank candidate personas for the task using the persona registry (`agents/personas/00-index.md`) — no new embedding infra required:
1. **Relevance** — match task keywords/intent against each persona's role + primary output + swarm. (Optional v2: embed persona profiles and retrieve top-k; for now reason over the index text.)
2. **Scope fit** — does the task fall inside this persona's mandate and phase boundary?
3. **Past success** — if `AUDIT_LOG`/memory shows a persona handled similar tasks well, weight it up (and vice-versa).
4. **Cost tier (SLM/LLM tiering)** — route to the **cheapest persona + model tier that clears the task's complexity bar**. Keep the persona, drop the model tier, for simple work; reserve SOTA models for genuinely hard/critical tasks. This reconciles with each skill's `context_cost` and the `brain/cost-benefit-router.skill`. **Biggest cost lever in multi-persona work.**

Output the top 1–3 with a one-line justification each; pick one unless the task benefits from a panel (see Voting).

## Delegation (contractor paradigm)
When a persona hands work to another persona, treat it as a **binding contract**, not a vague handoff:
```
CONTRACT
- Task spec:        [precise deliverable]
- Constraints:      [perf/security/compat/phase boundary]
- Eval metric:      [how "done" is judged — REUSE the existing quality gates]
- Output schema:    [shape of the expected result]
- Budget:           [token/cost ceiling for this subcontract]
```
- **Negotiation phase:** the receiving persona may **early-reject** ambiguous/underspecified work (ask for clarification via `clarify.skill`) before accepting — cheaper than producing wrong output.
- **Subcontracting:** a persona may further delegate, but subcontracts must respect the SDLC phase boundaries and the same contract discipline.
- **Validation:** delegation targets MUST be a real, approved persona from the registry (see Security — no hallucinated personas like `eng-god-mode`).

## Voting (consensus for high-stakes decisions)
For high-stakes, ambiguous decisions (e.g. a security/compliance/architecture call), optionally spawn a small panel of personas/attempts and take a **k-threshold consensus** (MAKER-style): accept the option that leads by `k`; on no-consensus, escalate to a human.
- Cost-gate it: voting multiplies cost, so only fire when `GABBE_AUTONOMY` + budget allow and the decision's stakes justify it.
- Prefer **diverse lenses** over identical voters (e.g. correctness / security / cost) so the panel catches more failure modes.
- Default to deterministic single-persona execution for ordinary tasks.

## Bounded self-refinement
Personas may improve over time within tight bounds (markdown-level, via `brain/learning-adaptation.skill`):
- Refine from **successful** outcomes only (misaligned-replay guard); never from failed runs.
- Keep refinements reversible + audited; a persona's core mandate and security scope are immutable (only humans change those).
- A persistent `persona_genes` store (DB-backed, project-scoped evolution) is a tracked **v2** — this skill stays markdown-driven for now.

## Output Format
```markdown
## PERSONA SELECTION — [task]
- Candidates: 1) [persona] — [why] (cost tier: [SLM/LLM/SOTA])
              2) ...
- Chosen: [persona] @ [model tier]   (or PANEL of [n] with k=[k])
- Delegation contract (if any): [task spec / eval metric / output schema / budget]
- Gate: autonomy=[ask|hybrid|auto], within budget=[yes/no]
```

## Constraints
- Default to the cheapest persona+model tier that reliably clears the bar; escalate tiers only with justification (and human approval for SOTA/expensive).
- Delegation targets must validate against the approved persona registry — never invent a persona.
- Voting/panels only when stakes + budget justify; otherwise single-persona deterministic execution.
- Persona core mandate, phase boundaries, and security scope are immutable to self-refinement.
- The fixed `loki-mode` phase assignments remain the safe default when selection is uncertain.

## Security & Guardrails

### 1. Skill Security (Persona-Selector)
- **Approved-target enum:** every selected/delegated persona must exist in `agents/personas/` — reject hallucinated or out-of-scope targets, failing safe back to the coordinator (mirrors loki-mode's Delegation-Hallucination guard).
- **Scope lock:** selection cannot grant a persona permissions outside its mandate (e.g. an `eng-qa` persona never gains deploy/merge rights by being "selected").

### 2. System Integration Security
- **Contract integrity:** the delegation contract (constraints, eval metric, budget) is binding; a subcontract cannot relax its parent's security/phase constraints.
- **Vote tampering:** consensus tallies must come from actual independent persona outputs, not a single model asserting a count — otherwise voting is theatre that can be gamed.

### 3. LLM & Agent Guardrails
- **Cost-gate integrity:** tier/voting decisions use live budget, not model-asserted budget, so the selector cannot talk itself into an expensive panel.
- **No self-promotion:** a persona's bounded self-refinement must never expand its own authority, budget, or security scope — those are human-only changes.
