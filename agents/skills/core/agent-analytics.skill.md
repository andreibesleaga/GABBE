---
name: "agent-analytics"
description: "Tracks key performance indicators (KPIs) for AI Agents: Token Usage, Task Duration, Loop Cycles, and Success Rate."
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
*   `duration_ms`: Execution time
*   `status`: SUCCESS | FAILURE | RETRY

### 2. Analysis & Alerts
*   **Loop Detection**: If `task_id` appears > 5 times in `metrics.log` with `status: RETRY`, trigger `human_escalation`.
*   **Cost Anomaly**: If `tokens_out` > 5000 for a simple task, flag as "Verbose/Inefficient".

### 3. Reporting
**Command**: `generate-report`
**Output**: `metrics/weekly_report.md`
*   Total Tokens consumed.
*   Average Task Duration.
*   Success Rate % (First-pass vs Retry).

## Storage
*   `agents/memory/metrics/analytics.jsonl` (Append-only log)

## Predictive Cost Admission Control

The metrics above are *reactive* — they detect overruns after tokens are already spent. Admission control is *proactive*: a financial-middleware gate sits in front of every premium-model call, tool call, and subagent spawn and decides, BEFORE the step runs, whether the budget can afford its worst case. A step that cannot be afforded is **rejected at the gate and never enters the loop**, so a runaway plan is stopped before it costs anything rather than after.

### The reserve → execute → reconcile cycle
1. **Estimate worst-case cost** for the pending step (max output tokens × model rate, plus tool/subagent overhead and any retry budget). Estimate the ceiling, not the average.
2. **Reserve it from the remaining budget.** Call the budget layer's `reserve(amount)` (backed by `can_afford(amount)`). GABBE's budget layer already exposes `reserve()` / `can_afford()` as the runtime primitive — this is the gate, not advisory.
3. **If the reservation fails, reject the step at the gate.** The call is never dispatched; surface a structured "budget-denied" outcome (and escalate to human if the goal still needs it). Nothing enters the agent loop on a failed reservation.
4. **Execute** only the steps whose reservation held.
5. **Reconcile reservation vs actual** after the call returns: release the unused remainder back to the budget (or debit the overage), then **recompute the forecast** of remaining steps so the next admission decision uses fresh numbers.

### Deterministic floor (counters the LLM cannot reason around)
Admission estimates are derived from the model's own (non-deterministic, gameable) reasoning, so they MUST sit on top of a deterministic floor — hard runtime counters enforced by the harness, outside the agent's control, that halt execution regardless of what the agent "decides":
- **Consumption cap** — absolute token/spend ceiling per task and per session.
- **Wall-clock boundary** — a hard deadline that terminates the run on elapsed time.
- **Loop / pagination cap** — max iterations of any ReAct/refine loop and max pages fetched per paginated source.
- **Delegation-depth cap** — max depth of subagent-spawns-subagent chains.
- **Idempotency / dedup keys** — a key per logical action so a retried or re-reasoned step debits the budget and executes once, not N times.

These counters are authoritative: the agent's non-deterministic logic cannot talk its way past them, because they are checked by the runtime, not the model. The probabilistic estimator decides *whether to attempt* a step; the deterministic floor decides *when to stop no matter what*.

## Security & Guardrails

### 1. Skill Security (Agent Analytics)
- **PII Scrubbing in Telemetry**: Ensure that `task_id` or any logged payload data does not inadvertently capture and store user PII or raw authentication tokens in the `analytics.jsonl` file.
- **Log Forgery Prevention**: The analytics logging mechanism must be isolated so that a compromised agent cannot forge or alter historical telemetry data to hide malicious activity or disguise token theft.

### 2. System Integration Security
- **Cost Denial of Service (DoS)**: Tie the anomaly detection (e.g., `tokens_out > 5000`) directly to a hard circuit breaker that revokes the agent's API keys or suspends the session to prevent runaway financial billing attacks.
- **Secure Metric Access**: The `metrics/weekly_report.md` and raw log files must be access-controlled, as traffic patterns and task duration metrics can leak business intelligence or identify high-value target processes to an attacker.

### 3. LLM & Agent Guardrails
- **Analytics Manipulation Defense**: Agents must not have `write` access to historical `analytics.jsonl` lines. They may only append new records.
- **Metric Hallucination Avoidance**: If an LLM is used to summarize the weekly report, it must use hard math validation (e.g., via a Python script execution) rather than estimating or hallucinating aggregated token counts and success rates.
