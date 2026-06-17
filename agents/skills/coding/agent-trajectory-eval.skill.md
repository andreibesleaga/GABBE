---
name: agent-trajectory-eval
description: Evaluate an agent's trajectory — its sequence of tool calls and state transitions — not just its final answer.
triggers: [evaluate agent trajectory, tool-use precision recall, in-order trajectory match, state transition check, task success rate, pass at k agent reliability]
tags: [coding, ai, agents, evaluation]
core: false
context_cost: medium
---
# Agent Trajectory Evaluation

## Goal
Evaluate an agent's **trajectory** — the sequence of tool calls, arguments, observations, and
state-machine transitions it produces — rather than scoring the final answer alone. A correct
final answer can hide a reckless or lucky path (wrong tools, illegal state jumps, wasted calls),
and a wrong answer can sit on top of a nearly-correct path worth one fix. You must score *both*
how the agent got there and where it ended up.

## Steps
1. **Capture the full execution trace.**
   - Record every step: each tool call, its arguments, the observation returned, and any
     state-machine transition. The trace is the evidence; a trajectory eval is only as good as the
     completeness of the captured trace.
2. **Compute tool-use metrics.**
   - **Tool-selection Precision / Recall / F1** — of the tools the agent called, how many were the
     right ones (precision), and of the tools it *should* have called, how many did it call
     (recall)? F1 balances both.
   - **Parameter F1** — given the right tool was chosen, were its arguments correct? A correct tool
     with wrong parameters is still a failure.
3. **Match the trajectory and verify legality.**
   - Prefer **in-order match** (the required tools appear in the correct relative sequence, with
     optional/extra steps permitted) over brittle **exact match** (every step identical) — exact
     match punishes harmless reordering and benign extra steps and is almost always too strict.
   - Verify state-machine transitions are *legal*: the agent must never take an impossible
     transition (e.g. "refund" before "authenticate"). Flag any illegal transition as a hard fail
     regardless of outcome.
4. **Measure task-success independently.**
   - Score milestone/goal achievement on its own axis: did the agent reach the required end state,
     even via a non-optimal path? Outcome success and trajectory quality are orthogonal — report
     them separately so neither masks the other.
5. **Report reliability over stochasticity.**
   - Agents are non-deterministic; one success can be luck. Run k trials and report **pass^k**
     (succeeds in *all* k trials) so a single fluke run cannot be mistaken for reliability.
   - Methodological grounding (named benchmarks, not dependencies): **tau-bench** evaluates agents
     by final-state comparison and popularized the pass^k reliability metric; **SWE-bench Verified**
     evaluates coding agents on real, human-validated GitHub issues. Borrow their methods —
     final-state checking plus pass^k, and human-validated tasks.

## Constraints
- Trajectory **exact-match is usually too strict** — use in-order / subset matching, allowing
  optional steps, unless the task genuinely requires a rigid sequence.
- Task success can hide a bad path, and a good path can still fail the task — always report
  **both** trajectory quality and outcome, never one as a proxy for the other.
- Evals **sample** the space of possible runs; they raise confidence but do not prove the agent is
  correct or safe.
- pass^k over k trials is the reliability signal; a single passing run is not evidence of
  reliability for a stochastic agent.

## Output Format
Produce a **trajectory scorecard** containing:
- Tool-selection F1 and **Parameter F1**.
- In-order trajectory match % (and a flag for any illegal state transition).
- Task-success rate (milestone/goal achievement).
- **pass^k** across k trials, with the value of k stated.
- A disclaimer that the eval samples runs and does not prove correctness.

## Security & Guardrails

### 1. Skill Security
- **Outcome-only blind spots**: Scoring just the final answer lets a dangerous path (illegal
  transitions, destructive tool calls that happened to be reverted) pass undetected. The agent MUST
  evaluate trajectory legality and tool-use metrics in addition to outcome, and treat any illegal
  state transition as a failure even when the final state looks correct.
- **Sampling overconfidence**: A single green run is not evidence of a reliable agent. The agent
  MUST report pass^k over multiple trials and label results as sampled, never as a correctness
  proof.

### 2. System Integration Security
- **Trace tampering**: Traces drive the verdict, so a writable or mutable trace can be edited to
  hide bad steps. The agent MUST capture traces in an append-only audit log with integrity checks,
  so the evaluated record cannot be retroactively altered.
- **Replaying destructive tool calls**: Re-running k trials of a trajectory can re-trigger
  real-world side effects (payments, deletes, emails). The agent MUST execute trajectory evals
  against sandboxed/mock tools or an isolated environment, never against live production systems.

### 3. LLM & Agent Guardrails
- **Benchmark contamination**: Evaluating against a leaked or memorized benchmark inflates scores
  without real capability. The agent MUST hold out fresh, unseen tasks and report on them
  separately, treating any public benchmark as potentially contaminated.
- **Trajectory reward-hacking**: An agent can learn to game the trajectory metric — calling the
  "expected" tools for appearance while not actually achieving the goal, or padding optional steps
  to satisfy an in-order matcher. The agent MUST verify the real outcome *state*, not just the
  path, and cross-check that scored tool calls produced their expected observations.
