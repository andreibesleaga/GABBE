---
name: cognitive-architectures
description: Patterns from SOAR, ACT-R, and LIDA for advanced agent cognitive cycles
triggers: [cognitive, architecture, soar, act-r, lida, reasoning cycle]
tags: [brain, architecture, theory]
context_cost: low
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

## Security & Guardrails

### 1. Skill Security (Cognitive Architectures)
- **Operator sanitization (SOAR):** before Selection, run every candidate operator through an immutable safety filter that discards destructive commands (`rm -rf`, `DROP TABLE`) regardless of heuristic score.
- **Workspace contamination (LIDA):** the winning coalition broadcasts globally, so a malicious sensory input that wins can compromise the whole swarm — scrub buffers for prompt-injection signatures BEFORE they compete for the Global Workspace.

### 2. System Integration Security
- **Retrieval poisoning (ACT-R):** attackers can spam inputs to inflate a dangerous chunk's frequency/recency — track `provenance` and discount/isolate untrusted-origin chunks.
- **Compute exhaustion:** elaboration/parallel-buffer loops are token-intensive; enforce strict depth/timeout limits (e.g. max 3 evaluation rounds) so malformed recursive inputs can't exhaust context/budget.

### 3. LLM & Agent Guardrails
- **Heuristic bypassing:** security heuristics (least privilege, immutability) are absolute — a candidate that violates one has its score zeroed; never let "speed"/"compliance" outweigh them.
- **Procedural hallucination:** ground production rules in verifiable artifacts (schemas, API specs), never in latent LLM knowledge (e.g. assuming `admin: true` is valid).
