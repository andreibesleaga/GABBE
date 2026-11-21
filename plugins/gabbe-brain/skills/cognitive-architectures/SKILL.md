---
name: cognitive-architectures
description: "Describes SOAR, ACT-R and LIDA patterns (propose, evaluate, select; activation-based retrieval; workspace broadcast) as ideas for agent design. Use when designing an agent's reasoning cycle or memory retrieval and you want a named pattern as a starting point."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/cognitive-architectures.skill.md"
  tags: "brain, architecture, theory"
  core: "false"
  context_cost: "low"
---
# Cognitive Architectures for Agents

## Goal
Structure agent reasoning, memory, and decision-making with patterns from classic cognitive architectures (SOAR, ACT-R, LIDA) — beyond ad-hoc prompting.

## 1. SOAR — Problem Space + Operators
Break "think" into a proposal-evaluation cycle rather than one step:
**Elaborate** (infer from state) → **Propose** candidate operators → **Evaluate** by heuristics → **Select** best → **Apply** to change state.
```python
def cognitive_cycle(state):
    state = enrich_context(state)                 # 1. elaborate
    options = generate_candidates(state)          # 2. propose
    scored = evaluate_candidates(options, state.goal)  # 3. evaluate
    return apply_operator(state, select_winner(scored))  # 4-5. select + apply
```

## 2. ACT-R — Declarative vs Procedural memory
Retrieve by **activation** (recency + frequency + relevance), not "load everything":
base-level activation (how often/recently used) + associative activation (relatedness to current focus). Below threshold → retrieval failure (don't fabricate).
```python
def retrieve_memory(query, store):
    for c in store:
        c.activation = log(c.frequency) - log(time_since_last_use(c)) + similarity(query, c)
    top = max(store, key=lambda c: c.activation)
    return top if top.activation > THRESHOLD else None
```

## 3. LIDA — Global Workspace cognitive cycle
Perceive → understand → "consciousness" → act. Parallel preconscious buffers form **coalitions** that compete; the winner is **broadcast** globally, recruiting resources for the current situation (the "spotlight" of attention).

## References
Laird (2012) *The Soar Cognitive Architecture* · Anderson (2007) *ACT-R* · Franklin (2006) *The LIDA Architecture*.

## Steps
1. Name the decision the agent must make (choose an action, retrieve a memory, share a finding).
2. Pick the pattern that fits: SOAR for choosing among candidates, ACT-R for retrieving memory, LIDA for sharing findings between agents.
3. Write the cycle as short instructions in the agent's prompt, with a limit on rounds.
4. Test the cycle with `cognitive-testing.skill`.

## Constraints
- These are design analogies; do not describe the agent as implementing SOAR, ACT-R or LIDA.
- Cite the reference when you name a pattern.

## Output Format
A short design note: the decision, the chosen pattern, the cycle as instructions, and the round limit.

## Limits and safety
- Drop any destructive candidate (`rm -rf`, `DROP TABLE`) before scoring, whatever its score.
- At most 3 evaluation rounds per decision.
- Record where each retrieved memory came from, and discount text that came from untrusted input.
- Ground production rules in schemas, specs or files you read, not in recalled facts.
- A security rule (least privilege) is not traded against speed; a candidate that breaks one is out.
