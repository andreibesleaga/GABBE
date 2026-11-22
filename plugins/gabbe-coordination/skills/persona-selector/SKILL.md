---
name: persona-selector
description: "Rank/select the best Loki persona(s) per task; persona delegation, consensus voting, bounded self-refinement — cost-gated. Use when: persona selector, best persona, which agent, pick persona, delegate to persona, route task, assign persona, who should do this, persona voting."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coordination/persona-selector.skill.md"
  tags: "coordination"
  core: "false"
  context_cost: "medium"
---
# Persona-Selector Skill

## Goal
Pick the **best persona(s)** for each task instead of relying only on the fixed per-phase assignments in `loki-mode.skill`. The phase defaults remain the baseline; this skill lets the orchestrator adapt — choosing a more relevant persona, tiering by cost, delegating between personas under a contract, voting on high-stakes decisions, and letting personas refine themselves within bounds. Everything here is cost-gated by `GABBE_AUTONOMY` + budget.

## Steps
1. Rank the candidate personas (Selection).
2. If work passes from one persona to another, write the contract (Delegation).
3. For a high-stakes decision, decide whether to convene a panel (Voting).
4. Report the result in the Output Format below.

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
For high-stakes, ambiguous decisions (e.g. a security/compliance/architecture call), optionally spawn a small panel of personas/attempts and take a **k-threshold consensus** (MAKER-style): accept the option that leads by `k`; on no-consensus, escalate to a human. **The voting algorithm itself (tally rule, first-to-ahead-by-k early stopping, red-flag-discard) is owned by `coordination/swarm-consensus.skill` — defer to it; this section only decides *when* to convene a panel.**
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

## Limits and safety
- Choose or delegate only to personas that exist in `agents/personas/`; if a name is not there, fall back to the coordinator and say so.
- Selecting a persona gives it no rights beyond its mandate (an `eng-qa` persona gets no deploy or merge right). A subcontract cannot relax its parent's security or phase constraints.
- A panel counts as a vote only when the votes come from separate subagent contexts or the human; otherwise it is a REVIEW (see `swarm-consensus.skill`).
- Read the budget from the real config or usage data, not from the model's own estimate.
- Self-refinement never widens a persona's authority, budget or security scope; only a human does.


---
Plugin note: the catalogue file(s) `agents/personas/00-index.md` named above list every skill of the full GABBE kit. They are in the full kit, not in this plugin.
