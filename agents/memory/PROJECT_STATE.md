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
```
NOT_STARTED → Project initialized but no phase begun
S01_REQUIREMENTS → PRD and EARS requirements in progress
S02_DESIGN → Architecture and ADRs in progress
S03_SPEC → Technical specification in progress
S04_TASKS → Task decomposition in progress
S05_IMPLEMENTATION → Engineering execution in progress
S06_TESTING → Quality gates and coverage validation
S07_SECURITY → Security review
S08_REVIEW → Human code review
S09_STAGING → Staging deployment and smoke tests
S10_PRODUCTION → Production deployment
COMPLETE → Project delivered
```

---

## Phase Gate Status

| Phase | Status | Completed | Approver |
|---|---|---|---|
| S01 Requirements | NOT_STARTED | — | Human |
| S02 Architecture | NOT_STARTED | — | Human |
| S03 Specification | NOT_STARTED | — | prod-tech-lead |
| S04 Tasks | NOT_STARTED | — | orch-planner |
| S05 Implementation | NOT_STARTED | — | orch-planner |
| S06 Testing | NOT_STARTED | — | orch-judge |
| S07 Security | NOT_STARTED | — | ops-security |
| S08 Human Review | NOT_STARTED | — | Human |
| S09 Staging | NOT_STARTED | — | ops-devops |
| S10 Production | NOT_STARTED | — | Human |

---

## Task Summary

| Metric | Value |
|---|---|
| **Total Tasks** | 0 (project/tasks.md not yet created) |
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
| project/tasks.md | NOT_CREATED | project/tasks.md |
| openapi.yaml | NOT_CREATED | docs/api/ |
| SECURITY_CHECKLIST.md | NOT_CREATED | — |

---

## Quality Gate Status

| Gate | Last Run | Result | Issues |
|---|---|---|---|
| Gate 1 — Lint | Never | — | — |
| Gate 2 — Types | Never | — | — |
| Gate 3 — Coverage | Never | — | — |
| Gate 4 — Integration | Never | — | — |
| Gate 5 — Security | Never | — | — |
| Gate 6 — Complexity | Never | — | — |
| Gate 7 — EARS | Never | — | — |

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
3. Invoke `prod-pm` (or `spec-writer.skill`) to create PRD.md
4. Get human approval on PRD before proceeding to S02

---

## Memory Pointers

| Memory Layer | File | Status |
|---|---|---|
| Episodic | agents/memory/episodic/ | Empty — add DECISION_LOG entries |
| Semantic | agents/memory/semantic/PROJECT_KNOWLEDGE_TEMPLATE.md | Empty — populate as research accumulates |
| Continuity | agents/memory/CONTINUITY.md | Empty — populate as failures occur |
| Audit | agents/memory/AUDIT_LOG.md | Initialized |
