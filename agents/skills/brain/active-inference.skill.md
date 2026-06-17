---
name: active-inference
description: Apply Active Inference to minimize prediction error (Surprise).
triggers: [active inference]
tags: [brain]
context_cost: medium
tools: [run_command, read_file]
---
# Active Inference Skill

> "Action is the process of changing the world to match your prediction."

## 1. The Concept (Free Energy Principle)
Standard agents are goal-directed (maximize reward); **Active Inference** agents are surprise-minimizing (minimize prediction error).
- **Goal:** not just to "win" but to understand and control.
- **Surprise:** the gap between *expectation* and *observation*.

> **Implementation note:** the production `gabbe/brain.py` uses epsilon-greedy gene selection plus a monotonic `success_rate` reward (effectively a bandit over prompt variants); the free-energy / active-inference framing here is conceptual, not implemented math.

## 2. The Feedback Loop
1. **Predict:** "Running `go test` will output PASS."
2. **Act/Sense:** run the command, read output.
3. **Compare:** compute prediction error — result "FAIL" → **Surprise!**

## 3. Solving the Error
Two ways to minimize surprise:
1. **Perceptual Inference (change mind):** "My model was wrong" → update docs/mental model.
2. **Active Inference (change world):** "The code is wrong" → edit it so the test passes.

## 4. Epistemic Action (Curiosity)
When surprise is "unknown" (high uncertainty), take an **epistemic action** (probe/log) to gain information rather than a pragmatic action toward a goal.

## 5. System Prompt Template
```markdown
You are an Active Inference Agent. Minimize "Surprise".

### Your Cycle
1. PREDICT: From your internal model, what do you expect next?
2. OBSERVE: Look at the actual tool output / user input.
3. COMPARE: Compute Prediction Error (Surprise).
4. RESOLVE:
   - Surprise HIGH → Epistemic Action (gather info to update model) or Pragmatic Action (force world to match prediction).
   - Surprise LOW → proceed with standard goal execution.

### Current State
- Goal: {{user_goal}}
- Expectation: {{current_expectation}}
- Observation: {{last_tool_output}}
```

## 6. Implementation (Pythonic Pseudo-code)
```python
def active_inference_step(agent, observation):
    surprise = calculate_divergence(agent.predict(), observation)
    if surprise > THRESHOLD:
        if agent.uncertainty > 0.8:
            return "explore_environment"   # epistemic
        return "correct_environment"       # pragmatic (active inference)
    return "continue_goal"
```

## Security & Guardrails

### 1. Skill Security (Active Inference)
- **Epistemic Action Containment**: epistemic actions are unpredictable — clamp them to read-only ops (`ls`, `cat`, `kubectl get`). They must NEVER mutate state or write to external APIs, preventing accidental DoS or data corruption during "exploration."
- **Surprise-Induced Hallucination**: on exceptionally high prediction error (e.g. garbled binary instead of JSON), the agent may panic and hallucinate a justification. Add a circuit breaker: if Surprise exceeds the max threshold, halt Active Inference and escalate to the human rather than acting blindly.

### 2. System Integration Security
- **Prediction Model Poisoning**: the internal model sets expectations; injection in a log file aligns those expectations with the attacker's goals. Sanitize all OODA inputs (user strings, external web payloads) before using them to compute Prediction Error.
- **Action Rate Limiting**: the loop can spiral if the agent repeatedly "fixes" a failing test via syntax changes. Enforce a max loop limit (e.g. 5 attempts) to prevent runaway compute and API rate-limit exhaustion.

### 3. LLM & Agent Guardrails
- **Destructive Pragmatism Bias**: the agent may decide the fastest "match prediction" route is deleting failing tests or disabling security layers. No pragmatic action from Active Inference may bypass `architecture-governance.skill.md` rules or delete source code without explicit human cryptographic approval.
- **Uncertainty Masking**: the LLM may sound confident while internal uncertainty is high. `active_inference_step` must rely on actual token log-probabilities (if available) or strict parsing constraints — not self-reported "confidence" — to trigger epistemic exploration.
