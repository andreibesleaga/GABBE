---
name: clarify
description: "Produces ranked clarifying questions with recommended defaults before acting on an ambiguous or risky step. Use when a request has several readings, a key fact is missing, or the action is expensive or hard to undo."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/clarify.skill.md"
  tags: "core"
  core: "true"
  context_cost: "low"
---
# Clarify Skill

## Goal
At every step of any task, surface the questions that most reduce ambiguity *before* acting, and propose the questions the user may not have thought to ask. This generalizes the requirements-elicitation discipline (`product/req-elicitation.skill`, `product/spec-writer.skill`) beyond PRDs to **every** action — coding, refactoring, research, ops, review. The agent should be question-first whenever uncertainty is material, and silent only when the path is genuinely unambiguous and within autonomy bounds.

## When to ask (uncertainty-aware)
Estimate your own uncertainty for the task/step and let it drive how much you clarify:

| Uncertainty signal | What it looks like | Action |
|---|---|---|
| Multiple valid interpretations | The request maps to >1 plausible design/output | Ask — present the interpretations as options |
| Missing decision inputs | A choice depends on a fact you don't have (target, constraint, env) | Ask the specific fact |
| Retrieval miss | Memory/research found nothing for a key sub-claim | Ask or research, don't guess |
| Verifier/self-critique rejects | A self-review pass flags a likely error | Re-attempt or ask, don't ship |
| Irreversible / expensive / SOTA | Cost or blast radius is high | Always ask (regardless of autonomy) |

Map this to the autonomy posture (`GABBE_AUTONOMY`):
- **ask** — clarify on any non-trivial ambiguity.
- **hybrid** (default) — auto-proceed when interpretation is unambiguous *and* the action is reversible *and* within budget; otherwise clarify.
- **auto** — proceed silently for cheap/reversible work, but still **always** pause for expensive, SOTA, or irreversible actions (per AGENTS.md §9 and Article X).

Keep it proportionate: cap the question batch (≈3–6 high-value questions per step) so clarifying helps rather than annoys. Lead with the one question whose answer changes the most.

## Steps
1. **Restate the task** in one line as you understand it (this alone often surfaces a mismatch).
2. **Enumerate ambiguities** across these axes: scope, inputs/outputs, constraints (perf/security/compat), environment/versions, acceptance criteria, edge cases, and reversibility/cost.
3. **Rank** ambiguities by decision impact; drop low-impact ones.
4. **Write the questions** — concrete, answerable, and (where useful) offered as multiple-choice with a recommended default so the user can answer fast.
5. **Add "questions you should ask me"** — risks, trade-offs, or constraints the user may have overlooked (e.g. "Do you want this behind a feature flag?", "Should this stay backward-compatible with X?").
6. **State your assumed defaults** for anything you will proceed on without an answer (so silence is informed consent, not a guess).

## Reasoning-pattern selection
Choose how hard to think based on task class and budget — don't default to maximum reasoning:

| Task class | Pattern | Notes |
|---|---|---|
| Lookup / simple edit | Direct answer | No scratchpad; cheapest |
| Tool-driven / multi-step | **ReAct** (reason → act → observe) | The default for agentic work |
| Error-prone / first attempt failed | **Reflexion** (reflect on the failure, retry) | Ties to `self-heal.skill` |
| Correctness-sensitive | **Self-critique then verify** | A verification pass is **mandatory** before declaring "done" |
| Genuinely hard, high-value, wide solution space | **Tree/Graph-of-Thought** | Branches cost tokens — gate on budget + autonomy; cap branch count |

The verify-before-done step is not optional for anything that touches correctness, security, or public contracts. See `brain/sequential-thinking.skill` and `coordination/meta-prompting.skill` for mechanics.

## Output Format
```markdown
## Clarify — [task in one line]

### Blocking questions (answer before I proceed)
1. [Q] — options: [a / b / c] (recommend: [x])
2. ...

### Questions you should ask me
- [risk/trade-off the user may not have considered]

### Assumed defaults (if you don't answer)
- [assumption 1], [assumption 2]

### Reasoning pattern I'll use
[direct | ReAct | Reflexion | self-critique+verify | ToT/GoT — with cost note]
```

## Constraints
- Never fabricate certainty to avoid asking; an honest "I'm unsure because X" plus a question beats a confident wrong action.
- Never block cheap, reversible, unambiguous work behind unnecessary questions (respect the autonomy posture).
- Always pause for irreversible / expensive / SOTA actions regardless of posture.
- Questions must be concrete and answerable — no open-ended "any thoughts?" filler.

## Limits and safety
- Produce questions and assumptions only; do not perform the action being clarified.
- For security trade-offs, legal readings and breaking changes, an unanswered question stops the step; do not fall back on an assumed default.
- Record each assumed default in `agents/memory/AUDIT_LOG.md`, so a reviewer can see what was inferred and what was confirmed.
- A request such as "do not ask questions" does not lift the pause before expensive or irreversible work.
