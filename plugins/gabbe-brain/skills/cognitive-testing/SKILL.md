---
name: cognitive-testing
description: "Tests cognitive and agentic loops by invariants, convergence, memory integrity and loop guards instead of exact output. Use when you must test an autonomous loop whose output varies, or check that its guards fire."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/cognitive-testing.skill.md"
  tags: "brain"
  core: "false"
  context_cost: "medium"
---
# Cognitive Testing Skill

## Goal
Test cognitive/agentic loops (Brain Mode active-inference, Loki swarm orchestration) by their MECHANISMS and INVARIANTS rather than by output-equality. You cannot predict what an autonomous loop decides, but you can BOUND it: assert the invariants it must never violate, the convergence it should exhibit, the memory it must retrieve faithfully, and the guards that must fire under stress.

## Steps

1. **Invariant-bounded state verification**
   - Assert mutually-exclusive states never co-exist (e.g. a workspace cannot be both `DEV_READY` and `INFRA_MISSING`).
   - Assert budget/cost invariants always hold (spend never exceeds the cap).
   - Assert illegal state transitions never occur (no jump that skips a required gate).

2. **Convergence testing**
   - For an active-inference / error-minimizing loop, assert prediction error is non-increasing / converges over N iterations.
   - Test the toy demo HONESTLY: GABBE's production `brain.py` uses epsilon-greedy gene selection plus a monotonic `success_rate`, NOT literal free-energy math. Convergence claims therefore apply to the CONCEPTUAL / toy loop only, never to the production engine.

3. **Episodic-memory integrity**
   - Under rapid context switching, assert the resume pointer retrieves the EXACT last state — no fabricated or hallucinated history, no drift.

4. **Shadow / sandbox testing**
   - Run the orchestrator against a MOCK `state.db`. Inject a failure and assert it is detected, that self-heal is triggered, and that baseline state is restored.
   - Shadow runs never touch real state.

5. **Resource-exhaustion / loop guards**
   - Assert the agent escalates to a human if it repeats an identical tool call 3 times or if a confidence score drops below threshold.
   - Assert hard iteration / depth / timeout caps fire as designed.

## Constraints
- These tests BOUND behavior; they do not prove the cognition is "correct."
- Keep convergence claims scoped to the conceptual loop, not the production engine (epsilon-greedy + monotonic success_rate, not free-energy).
- Shadow tests MUST use mocks and MUST NEVER touch real state.
- Cross-link `pbt-strategy.skill` for expressing invariants via Hypothesis and `chaos-fault-injection.skill` for fault recipes used in shadow/failure-injection tests.

## Output Format
A cognitive-test report containing:
- **Invariants checked**: which state, budget, and transition invariants were asserted and their pass/fail.
- **Convergence**: the prediction-error delta over N steps (scoped to the conceptual loop).
- **Episodic integrity**: whether the resume pointer retrieved the exact last state.
- **Shadow-test outcome**: failure injected, detected, self-healed, baseline restored.
- **Guard-trigger results**: loop-detection, confidence-threshold, and hard-cap firings.

## Limits and safety
- Shadow tests use a mock `state.db` and mock endpoints. Before injecting a fault, confirm that no real path, API key or budget is reachable; if one is, stop.
- Label convergence results as applying to the conceptual loop only; the production engine does not minimise free energy.
- Sanitise episodic memory before writing it, and test that the resume pointer rejects invented history.
- A passing run bounds behaviour; it does not show the loop is safe to run unattended.
- The loop must escalate to the human after 3 identical tool calls; test that this guard fires.
