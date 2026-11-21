# PROJECT_STATE_TEMPLATE.md — SDLC Master Tracker
<!-- Single source of truth for the current phase of the project -->
<!-- Updated by: sdlc-checkpoint.skill, loki-mode.skill, brain-mode.skill -->
<!-- Read by: session-resume.skill, active-inference.skill -->
<!-- Save as: agents/memory/PROJECT_STATE.md -->

---

## Current State

| Field | Value |
|---|---|
| **Project** | [Project Name] |
| **Current Phase** | S[XX] — [Phase Name, e.g., INITIALIZED, REQUIREMENTS, DESIGN] |
| **Status** | [NOT_STARTED / IN_PROGRESS / BLOCKED / DONE] |
| **Last Updated** | [YYYY-MM-DD] |

<!-- Valid phases (Day-0 → build loop → Day-2):
     S00 STRATEGY_DISCOVERY (Day-0, human GO/NO-GO),
     S01 REQUIREMENTS, S02 ARCHITECTURE, S03 TECH_SPEC, S04 TASK_DECOMP,
     S05 IMPLEMENTATION, S06 TESTING, S07 SECURITY, S08 HUMAN_REVIEW,
     S09 STAGING, S10 PRODUCTION,
     S11 OPERATE_MAINTAIN (Day-2), S12 EVOLVE_IMPROVE (Day-2), S13 DECOMMISSION_SUNSET (Day-2) -->

## Phase History
- [YYYY-MM-DD] S00 — STRATEGY_DISCOVERY (Day-0, GO/NO-GO)
- [YYYY-MM-DD] S01 — REQUIREMENTS (IN_PROGRESS)
- [YYYY-MM-DD] S11 — OPERATE_MAINTAIN (Day-2, after S10)
- [YYYY-MM-DD] S12 — EVOLVE_IMPROVE (Day-2)
- [YYYY-MM-DD] S13 — DECOMMISSION_SUNSET (Day-2)

## Active Tasks
- T-001: [Task description] (IN_PROGRESS)

## Blockers
- None
