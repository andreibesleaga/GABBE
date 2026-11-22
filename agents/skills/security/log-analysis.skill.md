---
name: log-analysis
description: "Read structured logs to find a cause: scope the time range, group by message, follow one trace id. Also flags secrets and personal data in logs. Use when investigating an error or incident from logs, or when reviewing what an application logs."
triggers: [log analysis, read logs, trace id, logql, error spike, find in logs]
tags: [security]
role: ops-monitor
context_cost: low
---
# log-analysis Skill

## Goal
This skill helps agents and engineers interpret logging data to find root causes of issues.

## Where it fits
Phase and gate: S07 (review what the application logs), S11 (operate and incident work, with `ops/incident-response.skill.md`). Evidence: the query and the counts in the incident or review notes.

## Steps
## 1. Structured Logging (The Prerequisite)
- **Format**: JSON. Always.
- **Why**: Allows querying `level="ERROR" AND service="user-api"`. Text logs require fragile regex.
- **Context**: Every log must have `trace_id`, `user_id`, and `environment`.

## 2. Analysis Workflow

1.  **Scope the Timeframe**: "Last 15 minutes" or "Since deployment at 14:00".
2.  **Filter by Level**: Start with `ERROR` and `FATAL`. Ignore `INFO` initially.
3.  **Group by Message**:
    - **Bad**: Reading 1000 lines of `Connection timeout`.
    - **Good**: "Count of errors by message type: Timeout (800), Auth Fail (200)".
4.  **Trace Correlation**: take one `trace_id` from an error and filter ALL logs (inc INFO) for that ID to see the sequence of events leading to failure.

## 3. Query Cheatsheet

### Loki (LogQL)
```logql
{app="frontend"} |= "error" | json | latency > 500ms
```

### Elasticsearch / Kibana (Lucene)
```lucene
service:backend AND level:ERROR AND NOT message:"healthcheck"
```

### Splunk
```splunk
index=prod sourcetype=k8s | stats count by message | sort - count
```

### Command Line (jq)
```bash
cat logs.json | jq 'select(.level=="error") | .message' | sort | uniq -c
```

## 4. Red Flags ("Smells")
- **"Swallowed Exception"**: Logs that say "Error occurred" but print no stack trace.
- **"Noise"**: Periodic errors (e.g., every 5 mins) that everyone ignores. These mask real issues.
- **"Sensitive Data"**: Passwords or PII in logs. -> **CRITICAL**: Report immediately.

## Constraints
- State the time range and the query used for every finding.
- Group before reading: counts by message type first.

## Output Format
A short note: time range, queries, counts by message, the trace followed, and any secret or personal data found (type and place only).

## Limits and safety
- Read logs read-only and only for the time range you need. Do not copy raw lines with personal data or secrets into reports or chat; write the type, file and count.
- A password, token or personal data in a log is a finding. Report it to the human at once and propose rotation. Do not delete log files yourself.
- Query production log systems only when the human gave access for this task.
- The query examples show syntax. Check it against your log system's documentation.
