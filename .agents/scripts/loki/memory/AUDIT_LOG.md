# AUDIT_LOG.md — Project Audit Trail

> APPEND ONLY — never delete or modify existing entries.
> Updated by: audit-trail.skill
> Read by: session-resume.skill (last 50 entries), integrity-check.skill

## Log Format

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome | References |
|---|---|---|---|---|---|---|

## Action Types
- DECISION — a choice was made between options
- PHASE_TRANSITION — SDLC phase changed
- TASK_DONE — a task was completed
- TASK_BLOCKED — a task is stuck, human needed
- QUALITY_GATE — gate pass/fail result
- SECURITY_FINDING — security issue found
- ADR_CREATED — architecture decision recorded
- HUMAN_ESCALATION — agent escalated to human
- SELF_HEAL_ATTEMPT — agent tried to fix itself
- RESEARCH_FINDING — authoritative source found
- ERROR — unexpected error encountered
- ROLLBACK — change was reverted

## Log Entries

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome | References |
|---|---|---|---|---|---|---|
| INIT | S00 | setup-context.sh | PHASE_TRANSITION | Kit initialized | SUCCESS | README_FULL.md |

