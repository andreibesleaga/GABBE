# Decision Log — Session [SESSION_ID]
<!-- Episodic memory: per-session log of decisions, actions, and outcomes -->
<!-- Append entries as you work. Never edit past entries. -->
<!-- Store file as: loki/memory/episodic/YYYY-MM-DD_S[SESSION_NUM].md -->

---

## Session Header

| Field | Value |
|---|---|
| **Session ID** | [YYYY-MM-DD-HH-MM or sequential number] |
| **Date** | [YYYY-MM-DD] |
| **Started by** | [agent persona or human] |
| **SDLC Phase at Start** | [S01-S10 or COMPLETE] |
| **Tasks at Start** | [T-NNN (IN_PROGRESS), T-NNN (BLOCKED), ...] |
| **Goal for this Session** | [one sentence: what we're trying to accomplish] |

---

## Decision Log Entries

<!-- Format: append one block per significant decision or action -->
<!-- Minimum: log every SDLC phase change, blocked task, architecture decision, human input -->

---

### Entry 001

| Field | Value |
|---|---|
| **Timestamp** | [HH:MM UTC] |
| **Actor** | [agent persona / human] |
| **Action Type** | [DECISION / TASK_DONE / TASK_BLOCKED / RESEARCH / ESCALATION / ARCHITECTURE / HUMAN_INPUT / PHASE_TRANSITION] |
| **Subject** | [one sentence: what was decided/done/found] |
| **Rationale** | [why this decision was made] |
| **Outcome** | [PASS / FAIL / PENDING / DEFERRED] |
| **References** | [tasks.md#T-NNN, ADR-001, SPEC.md#section, etc.] |

---

### Entry 002

| Field | Value |
|---|---|
| **Timestamp** | [HH:MM UTC] |
| **Actor** | [agent persona / human] |
| **Action Type** | [DECISION / TASK_DONE / TASK_BLOCKED / RESEARCH / ...] |
| **Subject** | |
| **Rationale** | |
| **Outcome** | |
| **References** | |

<!-- Add more entries as needed -->

---

## Failed Experiments (worth recording in CONTINUITY.md)

<!-- List approaches that didn't work — transfer these to CONTINUITY.md at session end -->

| What was tried | Why it failed | What to do instead |
|---|---|---|
| [e.g., Used library X] | [Conflicted with Y because Z] | [Use library W instead] |

---

## Research Findings (worth recording in semantic/)

<!-- List authoritative facts discovered — transfer to loki/memory/semantic/ at session end -->

| Finding | Source (Tier 1/2) | Relevance |
|---|---|---|
| [e.g., Prisma cursor pagination requires `skip: 1`] | [Prisma official docs v5.x] | [Used in T-045 pagination feature] |

---

## Session Summary

| Field | Value |
|---|---|
| **Tasks Completed** | [T-NNN, T-NNN, ...] |
| **Tasks Blocked** | [T-NNN (reason), ...] |
| **SDLC Phase at End** | [S01-S10 or COMPLETE] |
| **Key Decisions Made** | [bullet summary] |
| **Transferred to CONTINUITY.md** | [Yes/No — list entries] |
| **Transferred to semantic/** | [Yes/No — list entries] |
| **Human Escalations Raised** | [count + ticket references] |
| **Next Session Start Point** | [what to do first next session] |

---

## Handoff Notes

<!-- What the NEXT session/agent needs to know to continue without context loss -->

```
State at handoff:
  - Current task: [T-NNN — description]
  - Why stopped: [session ended / context limit / blocked]
  - Critical context: [anything the next agent MUST know before starting]
  - Don't repeat: [approaches already tried and failed]
  - Human input pending: [questions/decisions waiting for human]
```
