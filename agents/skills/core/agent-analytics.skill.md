---
name: agent-analytics
description: Tracks key performance indicators (KPIs) for AI Agents: Token Usage, Task Duration, Loop Cycles, and Success Rate.
triggers: [analytics, metrics, tokens used, cost tracking, performance report, agent stats]
tags: [core]
context_cost: low
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
