---
name: cognitive-testing
description: Test cognitive and agentic loops by their mechanisms and invariants rather than by output-equality.
triggers: [cognitive testing, invariant testing, convergence testing, episodic memory integrity, shadow testing, loop guard, brain mode testing]
tags: [brain]
core: false
context_cost: medium
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

## Security & Guardrails

### 1. Skill Security (Cognitive Testing)
- **Episodic-memory poisoning**: Episodic memory is an injection sink — a poisoned memory replayed on resume becomes a persistent instruction the loop trusts as its own history. Memories MUST be sanitized before write, and the integrity test in Step 3 MUST assert the resume pointer rejects fabricated history rather than merely matching the happy path.
- **Convergence-claim overreach**: A test that asserts "free-energy convergence" against the production engine misrepresents what `brain.py` does and gives false assurance. The skill MUST keep convergence assertions scoped to the conceptual/toy loop and label them as such in the report, never implying the production engine minimizes free energy.

### 2. System Integration Security
- **Shadow tests hitting production resources**: A shadow test misconfigured against the real `state.db`, live APIs, or production budget can corrupt state or spend real money while injecting failures. Mock isolation MUST be enforced structurally (separate connection/credentials, no production endpoints reachable from the test harness), failing closed if a real resource is detected.
- **Fault-injection blast radius**: Faults injected in shadow runs (per `chaos-fault-injection.skill`) must be contained to the sandbox. The harness MUST verify the mock boundary before injecting and MUST NOT propagate injected failures to shared or live infrastructure.

### 3. LLM & Agent Guardrails
- **Runaway loops exhausting budget**: An autonomous loop without guards can spin indefinitely, exhausting token/cost budget — a self-inflicted denial of service. The skill MUST assert hard iteration/depth/timeout caps and identical-call loop detection (escalate to human after 3 repeats), and these guards MUST fail closed.
- **Bounding is not correctness**: Passing invariant, convergence, and guard tests bounds behavior but does NOT prove the cognition is correct or safe to run unsupervised. High-impact autonomous actions still require human approval per `ai-safety-guardrails.skill` and `prompt-injection-defense.skill`.
