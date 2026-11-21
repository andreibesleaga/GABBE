---
name: "agent-analytics"
description: Logs token use, task duration and retries per task to a metrics file and flags retry loops and cost spikes. Use when the human asks about token usage, cost or agent efficiency, or when a task keeps retrying.
triggers: ["analytics", "metrics", "tokens used", "cost tracking", "performance report", "agent stats"]
tags: ["core"]
context_cost: "low"
---
# Agent Analytics Skill

## Goal
Provide visibility into the "Black Box" of agent execution by tracking cost (tokens) and efficiency (time/loops).

## Flow

### Steps
## 1. Metric Capture
**Input**: Completion of a Task / Tool Call / Phase.
**Action**: Log the following structured data:
*   `timestamp`: ISO 8601
*   `agent_id`: Loki / Claude / Gemini
*   `task_id`: T-NNN
*   `tokens_in`: (Estimated)
*   `tokens_out`: (Estimated)
*   `duration_ms`: execution time, only if the platform reports it; otherwise leave it empty (do not guess)
*   `status`: SUCCESS | FAILURE | RETRY

### 2. Analysis & Alerts
*   **Loop Detection**: If `task_id` appears > 5 times in `agents/memory/metrics/analytics.jsonl` with `status: RETRY`, trigger `human_escalation`.
*   **Cost Anomaly**: If `tokens_out` > 5000 for a simple task, flag as "Verbose/Inefficient".

### 3. Reporting
**When**: on request, and at the end of each S11 or S12 cycle.
**Output**: `agents/memory/metrics/report.md`, computed from `analytics.jsonl` with a script (`jq` or Python), not estimated by hand.
*   Total Tokens consumed.
*   Average Task Duration.
*   Success Rate % (First-pass vs Retry).

## Storage
*   `agents/memory/metrics/analytics.jsonl` (Append-only log)

## Predictive Cost Admission Control

The metrics above are *reactive* — they detect overruns after tokens are already spent. Admission control is *proactive*: a financial-middleware gate sits in front of every premium-model call, tool call, and subagent spawn and decides, BEFORE the step runs, whether the budget can afford its worst case. A step that cannot be afforded is **rejected at the gate and never enters the loop**, so a runaway plan is stopped before it costs anything rather than after.

### The reserve → execute → reconcile cycle
1. **Estimate worst-case cost** for the pending step (max output tokens × model rate, plus tool/subagent overhead and any retry budget). Estimate the ceiling, not the average.
2. **Reserve it from the remaining budget.** If the optional CLI's budget layer is wired in, call its `reserve(amount)` (backed by `can_afford(amount)`). Without the CLI this check is advisory: compare the estimate with the budget the human gave you and ask before going over it.
3. **If the reservation fails, reject the step at the gate.** The call is never dispatched; surface a structured "budget-denied" outcome (and escalate to human if the goal still needs it). Nothing enters the agent loop on a failed reservation.
4. **Execute** only the steps whose reservation held.
5. **Reconcile reservation vs actual** after the call returns: release the unused remainder back to the budget (or debit the overage), then **recompute the forecast** of remaining steps so the next admission decision uses fresh numbers.

### Deterministic floor (counters the LLM cannot reason around)
Admission estimates are derived from the model's own (non-deterministic, gameable) reasoning, so they should sit on top of a deterministic floor: hard counters enforced by the platform or the CLI, outside the agent's control. The kit itself does not provide them; if your platform has token, turn or time limits, set them:
- **Consumption cap** — absolute token/spend ceiling per task and per session.
- **Wall-clock boundary** — a hard deadline that terminates the run on elapsed time.
- **Loop / pagination cap** — max iterations of any ReAct/refine loop and max pages fetched per paginated source.
- **Delegation-depth cap** — max depth of subagent-spawns-subagent chains.
- **Idempotency / dedup keys** — a key per logical action so a retried or re-reasoned step debits the budget and executes once, not N times.

These counters are authoritative: the agent's non-deterministic logic cannot talk its way past them, because they are checked by the runtime, not the model. The probabilistic estimator decides *whether to attempt* a step; the deterministic floor decides *when to stop no matter what*.

## Constraints
- The log is append-only: add rows, never change earlier rows.
- Token figures are estimates unless the platform reports them; label them "estimated".
- Totals and averages come from a script, not from the model's arithmetic.

## Output Format
One JSON line per task in `agents/memory/metrics/analytics.jsonl` (fields above) and, on request, `agents/memory/metrics/report.md` with total tokens, average duration and first-pass success rate.

## Limits and safety
- Log ids, counts and statuses only: no prompts, user data or tokens in `analytics.jsonl`.
- Do not edit or delete earlier lines of the log; append only.
- Cost admission (`reserve`, `can_afford`) works only when the CLI calls it. If your platform provides budget limits or hooks, use them as the hard stop.
- Compute totals with a script; label token counts "estimated" unless the platform reported them.
