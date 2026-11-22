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
| **Current Phase** | S<NN> — [Phase Name, e.g., STRATEGY_DISCOVERY, REQUIREMENTS, ARCHITECTURE] |
| **Status** | [NOT_STARTED / IN_PROGRESS / BLOCKED / DONE] |
| **Last Updated** | [YYYY-MM-DD] |

<!-- Valid phases: exactly 14, S00–S13 (canonical table: agents/guides/processes/loki-sdlc-phases.md)
     S00 STRATEGY_DISCOVERY (Day 0),
     S01 REQUIREMENTS, S02 ARCHITECTURE, S03 TECH_SPEC, S04 TASK_DECOMP,
     S05 IMPLEMENTATION, S06 TESTING, S07 SECURITY, S08 HUMAN_REVIEW,
     S09 STAGING, S10 PRODUCTION (Day 1),
     S11 OPERATE_MAINTAIN, S12 EVOLVE_IMPROVE, S13 DECOMMISSION_SUNSET (Day 2).
     Human gates (six): S00 go / no-go, S01, S02, S07, S08, S10 ("deploy now").
     S03: prod-tech-lead. S04, S06: orch-judge (quality gates G1–G9 at S06).
     S05: verify green. S09: smoke green. S11, S12: recurring review.
     S13 is entered on the human's decision to retire the system.
     Status words: NOT_STARTED, IN_PROGRESS, BLOCKED, DONE. -->

## Phase History
- [YYYY-MM-DD] S00 — STRATEGY_DISCOVERY (Day 0, human go / no-go)
- [YYYY-MM-DD] S01 — REQUIREMENTS (IN_PROGRESS)
- [YYYY-MM-DD] S11 — OPERATE_MAINTAIN (Day 2, after S10)
- [YYYY-MM-DD] S12 — EVOLVE_IMPROVE (Day 2)
- [YYYY-MM-DD] S13 — DECOMMISSION_SUNSET (Day 2)

## Active Tasks
- T-001: [Task description] (IN_PROGRESS)

## Blockers
- None
