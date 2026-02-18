# Audit Log — [PROJECT_NAME]
<!-- APPEND ONLY — never modify or delete existing entries -->
<!-- Updated by: audit-trail.skill, orch-coordinator, sdlc-checkpoint.skill -->
<!-- Read by: session-resume.skill, orch-coordinator, humans -->

**Format version**: 1.0
**Log started**: [YYYY-MM-DD]
**Project**: [PROJECT_NAME]

---

## Action Type Reference

| Type | Description |
|---|---|
| `LOKI_INIT` | Loki Mode initialized for a new project |
| `SESSION_START` | New session beginning |
| `SESSION_END` | Session ending |
| `PHASE_TRANSITION` | Entering or completing an SDLC phase |
| `CHECKPOINT_SAVED` | SESSION_SNAPSHOT written |
| `TASK_DONE` | Task completed (T-NNN) |
| `TASK_BLOCKED` | Task blocked after self-heal exhausted |
| `TASK_UNBLOCKED` | Blocked task resumed after human decision |
| `QUALITY_GATE` | orch-judge quality gate result |
| `SECURITY_FINDING` | ops-security finding logged |
| `ADR_CREATED` | Architecture Decision Record created |
| `DECISION` | Significant decision made |
| `HUMAN_ESCALATION` | Human decision requested |
| `HUMAN_DECISION` | Human decision received and applied |
| `SELF_HEAL_ATTEMPT` | Self-heal iteration (attempt N of 5) |
| `SELF_HEAL_RESOLVED` | Self-heal succeeded |
| `RESEARCH_FINDING` | orch-researcher found authoritative fact |
| `ERROR` | Unexpected error encountered |
| `ROLLBACK` | Rollback executed |

---

## Log Entries

<!-- Each entry format:
| [ISO 8601 UTC] | [SESSION_ID] | [Actor] | [Type] | [Description] | [Outcome] | [References] |
-->

| Timestamp | Session | Actor | Type | Description | Outcome | References |
|---|---|---|---|---|---|---|
| [YYYY-MM-DDTHH:MM:SSZ] | [S001] | loki-mode | `LOKI_INIT` | Audit log initialized for [PROJECT_NAME] | OK | — |

<!-- Append new entries below this line. Never edit rows above. -->
