---
name: active-inference
description: Frames an agent's predict, act, compare loop as surprise minimisation (conceptual, not a solver). Use when a tool result contradicts the agent's expectation and it must choose between probing and fixing.
triggers: [active inference, prediction error, result contradicts expectation, probe or fix]
tags: [brain]
context_cost: medium
tools: [run_command, read_file]
---
# Active Inference Skill

## Goal
Give an agent one habit: predict what a step will return, run it, compare, and decide whether to probe for information or fix the code. This is a framing for instructions, not a solver.

> "Action is the process of changing the world to match your prediction."

## 1. The Concept (Free Energy Principle)
Standard agents are goal-directed (maximize reward); **Active Inference** agents are surprise-minimizing (minimize prediction error).
- **Goal:** not just to "win" but to understand and control.
- **Surprise:** the gap between *expectation* and *observation*.

> **Implementation note (conceptual framing, not implemented CLI math):** the production `gabbe/brain.py` uses epsilon-greedy gene selection plus a monotonic `success_rate` reward (effectively a bandit over prompt variants); the free-energy / active-inference framing here is conceptual, not implemented math. Use it to *shape agent instructions*, not as a literal solver — and never claim it "guarantees correctness." See `guides/ai/self-evolving-skills.md` for what actually runs.

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

## Steps
1. Before a command, write the expected result in one line.
2. Run it and read the real output.
3. If it differs, probe read-only when the cause is unknown; edit the code when the cause is known.
4. After 5 failed corrections, stop and escalate (`self-heal.skill`).

## Constraints
- Probes are read-only.
- Never make a result match a prediction by deleting a test or disabling a check.
- Do not claim the method guarantees correctness.

## Output Format
A short trace per step: Expected, Observed, Difference, Action (probe, fix or continue).

## Limits and safety
- Probing actions are read-only (`ls`, `cat`, `git status`, `kubectl get`); they never write or call external APIs.
- On a very large surprise (garbled or binary output where JSON was expected), stop and ask the human instead of acting.
- Never make a result match the prediction by deleting a failing test or source code, or by switching off a check.
- At most 5 correction attempts per failure, then escalate.
- Measure surprise from the real tool output; the agent's own stated confidence is not a measure.
