# Project State — Master SDLC Tracker
<!-- Updated by: orch-coordinator, sdlc-checkpoint.skill -->
<!-- Read by: session-resume.skill, loki-mode.skill, orch-planner -->
<!-- This is the single source of truth for current project position -->

---

## Project Identity

| Field | Value |
|---|---|
| **Project Name** | [PROJECT_NAME] |
| **Repository** | [git remote URL] |
| **Started** | [YYYY-MM-DD] |
| **Last Updated** | [YYYY-MM-DD HH:MM UTC] |
| **Updated by** | [agent/human] |

---

## Current SDLC Phase

| Field | Value |
|---|---|
| **Current Phase** | NOT_STARTED |
| **Phase Status** | — |
| **Phase Started** | — |
| **Blocking Issues** | None |

### Phase Legend
The lifecycle has 14 phases, S00–S13. The canonical table is in
`agents/guides/processes/loki-sdlc-phases.md`; this list must match it.
```
NOT_STARTED → Project initialized but no phase begun
S00 STRATEGY_DISCOVERY → Problem, opportunity, go / no-go (Day 0)
S01 REQUIREMENTS → PRD and EARS requirements in progress
S02 ARCHITECTURE → Architecture, ADRs and threat model in progress
S03 TECH_SPEC → Technical specification in progress
S04 TASK_DECOMP → Task decomposition in progress
S05 IMPLEMENTATION → Engineering execution in progress
S06 TESTING → Quality gates G1–G9 and coverage validation
S07 SECURITY → Security review
S08 HUMAN_REVIEW → Human review
S09 STAGING → Staging deployment and smoke tests
S10 PRODUCTION → Production deployment (the human says "deploy now" first)
S11 OPERATE_MAINTAIN → Operate and maintain (Day 2, recurring)
S12 EVOLVE_IMPROVE → Evolve and improve (Day 2, recurring)
S13 DECOMMISSION_SUNSET → Decommission and sunset (Day 2, on the human's decision)
```
Status words: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`.

---

## Phase Gate Status

Six human gates: S00, S01, S02, S07, S08, S10. Record each as a `HUMAN_APPROVED`
row in `agents/memory/AUDIT_LOG.md`; a phase is not advanced without it.

| Phase | Status | Completed | Approver |
|---|---|---|---|
| S00 Strategy & Discovery | NOT_STARTED | — | Human (go / no-go) |
| S01 Requirements | NOT_STARTED | — | Human |
| S02 Architecture | NOT_STARTED | — | Human |
| S03 Technical Spec | NOT_STARTED | — | prod-tech-lead |
| S04 Task Decomposition | NOT_STARTED | — | orch-judge |
| S05 Implementation | NOT_STARTED | — | verify green |
| S06 Testing & Quality | NOT_STARTED | — | orch-judge (G1–G9) |
| S07 Security Review | NOT_STARTED | — | Human (security sign-off) |
| S08 Human Review | NOT_STARTED | — | Human |
| S09 Staging | NOT_STARTED | — | smoke tests green |
| S10 Production | NOT_STARTED | — | Human ("deploy now"), then health check |
| S11 Operate & Maintain | NOT_STARTED | — | recurring review |
| S12 Evolve & Improve | NOT_STARTED | — | recurring review |
| S13 Decommission & Sunset | NOT_STARTED | — | entered on the human's decision to retire |

---

## Task Summary

| Metric | Value |
|---|---|
| **Total Tasks** | 0 (project/TASKS.md not yet created) |
| **TODO** | 0 |
| **IN_PROGRESS** | 0 |
| **DONE** | 0 |
| **BLOCKED** | 0 |
| **Completion %** | 0% |

---

## Artifact Status

| Artifact | Status | Location |
|---|---|---|
| PRD.md | NOT_CREATED | docs/requirements/PRD.md |
| EARS_REQUIREMENTS.md | NOT_CREATED | docs/requirements/ |
| PLAN.md | NOT_CREATED | PLAN.md |
| C4_ARCHITECTURE.md | NOT_CREATED | docs/architecture/ |
| SPEC.md | NOT_CREATED | SPEC.md |
| project/TASKS.md | NOT_CREATED | project/TASKS.md |
| openapi.yaml | NOT_CREATED | docs/api/ |
| SECURITY_CHECKLIST.md | NOT_CREATED | — |

---

## Quality Gate Status

The quality gates G1–G9 run at S06 and are defined in `agents/personas/orch-judge.md`.
G7 and G8 may be recorded `N/A` with a reason.

| Gate | Last Run | Result | Issues |
|---|---|---|---|
| G1 — Lint | Never | — | — |
| G2 — Types | Never | — | — |
| G3 — Coverage | Never | — | — |
| G4 — Integration | Never | — | — |
| G5 — Dependency security | Never | — | — |
| G6 — Complexity | Never | — | — |
| G7 — Architecture fitness | Never | — | — |
| G8 — End-to-end | Never | — | — |
| G9 — EARS coverage | Never | — | — |

---

## Active Blockers

*(None)*

---

## Pending Human Decisions

*(None)*

---

## Next Actions

1. Run `setup-context.sh` to configure tool symlinks
2. Fill in AGENTS.md for this specific project
3. Start at S00 (discovery, `prod-research`) unless the human says "skip discovery"; then `prod-pm` (or `spec-writer.skill`) creates PRD.md at S01
4. Get the human's go at S00 and approval of the PRD at S01 before proceeding

---

## Memory Pointers

| Memory Layer | File | Status |
|---|---|---|
| Episodic | agents/memory/episodic/ | Empty — add DECISION_LOG entries |
| Semantic | agents/memory/semantic/PROJECT_KNOWLEDGE_TEMPLATE.md | Empty — populate as research accumulates |
| Continuity | agents/memory/CONTINUITY.md | Empty — populate as failures occur |
| Audit | agents/memory/AUDIT_LOG.md | Initialized |
