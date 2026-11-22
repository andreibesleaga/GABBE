# SDLC Tracker
<!-- Updated by: sdlc-checkpoint.skill | Read by: session-resume.skill, integrity-check.skill -->
<!-- Project: [Project Name] | Started: [date] -->

---

## Current Status

```
Current Phase: S<NN> — [Phase Name]   (S00–S13)
Status:        NOT_STARTED | IN_PROGRESS | BLOCKED | DONE
Last updated:  [date]
Updated by:    [agent/human]
```

---

## Phase Progress Board

The lifecycle has 14 phases, S00–S13. The canonical table is in
`agents/guides/processes/loki-sdlc-phases.md`; this board must match it. Six human
gates (hard stops): S00, S01, S02, S07, S08, S10. Record each as a `HUMAN_APPROVED`
row in AUDIT_LOG.md. The quality gates G1–G9 run at S06 (see `agents/personas/orch-judge.md`).

| Phase | Name | Status | Started | Completed | Approver | Gate Criteria |
|---|---|---|---|---|---|---|
| S00 | Strategy & Discovery (Day 0) | NOT_STARTED | — | — | Human (go / no-go) | Problem statement + opportunity assessment + RICE, human GO/NO-GO |
| S01 | Requirements | NOT_STARTED | — | — | Human | PRD.md with EARS, human approval |
| S02 | Architecture | NOT_STARTED | — | — | Human | Architecture + ADRs + threat model + cost check |
| S03 | Technical Spec | NOT_STARTED | — | — | prod-tech-lead | Tech spec + API contracts |
| S04 | Task Decomposition | NOT_STARTED | — | — | orch-judge | Atomic tasks, acyclic dependency graph |
| S05 | Implementation | NOT_STARTED | — | — | verify green | All project/TASKS.md items DONE |
| S06 | Testing & Quality | NOT_STARTED | — | — | orch-judge | Quality gates G1–G9 pass, final-review = SHIP |
| S07 | Security Review | NOT_STARTED | — | — | Human (security sign-off) | SECURITY_CHECKLIST.md 100%, no open HIGH finding |
| S08 | Human Review | NOT_STARTED | — | — | Human | Human review approved |
| S09 | Staging | NOT_STARTED | — | — | smoke green | Deployed + smoke tests passing |
| S10 | Production | NOT_STARTED | — | — | Human ("deploy now") | Human approval before deploy; health checks pass and the human confirms the observation window has ended; rollback documented |
| S11 | Operate & Maintain (Day 2) | NOT_STARTED | — | — | recurring | SLOs met, runbooks live, no critical CVEs, spend within budget |
| S12 | Evolve & Improve (Day 2) | NOT_STARTED | — | — | recurring | Retrospective actions logged, experiments decided, DORA/SPACE reviewed |
| S13 | Decommission & Sunset (Day 2) | NOT_STARTED | — | — | entered on the human's decision | Data archived/migrated, users notified, contracts wound down |

**Status values:** `NOT_STARTED` | `IN_PROGRESS` | `BLOCKED` | `DONE`

---

## Definition of Done — Per Phase

### S00 — Strategy & Discovery (Day 0)
```
[ ] Problem statement drafted (job-to-be-done, who hurts, why now)
[ ] Opportunity assessment complete (sizing, risks, North-Star + HEART metrics)
[ ] Market/competitive scan + Wardley map captured
[ ] Candidate bets prioritized with RICE
[ ] Human GO/NO-GO decision recorded (GO required to start S01)
[ ] SESSION_SNAPSHOT/S00_discovery.md created
```

### S01 — Requirements
```
[ ] PRD.md created using PRD_TEMPLATE.md
[ ] All requirements written in EARS syntax (no "should" or "might")
[ ] Ambiguity layer completed — no unresolved questions
[ ] Out-of-scope section filled
[ ] Human explicitly approved PRD.md
[ ] SESSION_SNAPSHOT/S01_requirements.md created
[ ] AUDIT_LOG.md entry: HUMAN_APPROVED
```

### S02 — Architecture
```
[ ] Architecture approach documented in PLAN.md
[ ] C4 Level 1+2 diagrams in docs/architecture/ (or documented exception)
[ ] ADR created for every significant technology choice
[ ] Threat model completed for ALL security-sensitive features
[ ] Cost check done (financial-governance.skill)
[ ] Human approved architecture approach (AUDIT_LOG.md entry: HUMAN_APPROVED)
[ ] SESSION_SNAPSHOT/S02_architecture.md created
```

### S03 — Technical Spec
```
[ ] SPEC_TEMPLATE.md completed: domain model, API contracts, DB changes
[ ] OpenAPI spec at docs/api/openapi.yaml (or equivalent)
[ ] Migration plan documented (if DB changes)
[ ] Testing strategy defined per layer
[ ] prod-tech-lead approved the technical specification (the human may review later)
[ ] SESSION_SNAPSHOT/S03_tech_spec.md created
```

### S04 — Task Decomposition
```
[ ] All PLAN.md items decomposed into TASKS_TEMPLATE.md
[ ] Each task is atomic: one concern, at most three files, one verifying test, about 15 minutes for an expert
[ ] Each task: has testable acceptance criteria
[ ] Tasks have correct dependency ordering; the dependency graph has no cycles; parallel groups are conflict-free
[ ] orch-judge reviewed the decomposition
[ ] No ambiguous tasks ("do the stuff" — must be specific files/functions)
[ ] SESSION_SNAPSHOT/S04_task_decomp.md created
```

### S05 — Implementation
```
[ ] All tasks in project/TASKS.md have status DONE (none TODO/IN_PROGRESS/BLOCKED)
[ ] TDD followed for each task: failing test written first
[ ] Each task commit references the task ID
[ ] AUDIT_LOG.md has TASK_DONE entry for each task
[ ] SESSION_SNAPSHOT/S05_implementation.md created
```

### S06 — Testing & Quality
```
[ ] [test command] passes: 0 failing, 0 unexpected skips
[ ] Quality gates G1–G9 pass (definitions in agents/personas/orch-judge.md; G7 and G8 may be N/A with a reason)
[ ] G3 Coverage: 99% of new and changed lines, total at or above coverage_min (run [coverage command])
[ ] G6 Complexity: max cyclomatic complexity 10 or less
[ ] final-review = SHIP; no performance regression against the baseline
[ ] SESSION_SNAPSHOT/S06_testing.md created
```

### S07 — Security Review
```
[ ] security-audit.skill run on full codebase
[ ] SECURITY_CHECKLIST.md 100% complete
[ ] No open CRITICAL or HIGH CVE in dependencies
[ ] gitleaks detect: CLEAN (no secrets in git)
[ ] All threat model mitigations implemented
[ ] Sustainability report reviewed
[ ] Human security sign-off (AUDIT_LOG.md entry: HUMAN_APPROVED)
[ ] SESSION_SNAPSHOT/S07_security.md created
```

### S08 — Human Review
```
[ ] PR created with complete description
[ ] Human reviewer has reviewed all changes
[ ] All reviewer comments addressed
[ ] No "RESOLVE LATER" comments (all blocking feedback resolved)
[ ] PR approved and merge ready
[ ] SESSION_SNAPSHOT/S08_review.md created
```

### S09 — Staging
```
[ ] Deployed to staging environment
[ ] Database migrations applied to staging
[ ] Smoke tests passing (health check + core user flows)
[ ] No error spike in monitoring after deploy
[ ] Performance within acceptable range
[ ] SESSION_SNAPSHOT/S09_staging.md created
```

### S10 — Production
```
[ ] The human said "deploy now" in this request, before the deploy (AUDIT_LOG.md entry: HUMAN_APPROVED)
[ ] Production deploy completed
[ ] Database migrations applied to production
[ ] Smoke tests passing in production
[ ] Monitoring/alerting active for new feature
[ ] Rollback plan documented and verified
[ ] No error spike in first 30 minutes post-deploy
[ ] SESSION_SNAPSHOT/S10_production.md created
[ ] Git tag: v[semver] proposed to the human (run only when the human asks)
```

### S11 — Operate & Maintain (Day 2)
```
[ ] Observability stack live (metrics/logs/traces, dashboards, SLOs)
[ ] Runbooks authored per service (RUNBOOK_TEMPLATE.md)
[ ] On-call rotation + error-budget policy defined
[ ] Dependency/patch cadence running; 0 open critical CVEs
[ ] SLO adherence report green; cost within budget
[ ] SESSION_SNAPSHOT/S11_operate.md created
```

### S12 — Evolve & Improve (Day 2)
```
[ ] Blameless retrospective held; action items logged
[ ] Product analytics reviewed (funnels, retention, North-Star movement)
[ ] A/B experiments planned and each has a decision (ship/iterate/kill)
[ ] Tech-debt paydown items fed back into the backlog/S04
[ ] DORA + SPACE metrics reviewed; stale feature flags retired
[ ] SESSION_SNAPSHOT/S12_evolve.md created
```

### S13 — Decommission & Sunset (Day 2)
```
[ ] The human decided to retire the system (entry condition)
[ ] Deprecation policy + timeline approved
[ ] Data retention/migration executed; archives + final backups taken
[ ] Users notified; migration paths communicated
[ ] Infra torn down safely; no live dependents remain
[ ] License/contract/vendor wind-down confirmed
[ ] SESSION_SNAPSHOT/S13_sunset.md created
```

---

## Current Blockers

| Blocker | Since | Waiting for | Owner |
|---|---|---|---|
| [description] | [date] | [decision/person/event] | [name] |

---

## Upcoming Milestones

| Milestone | Target Date | Dependencies |
|---|---|---|
| PRD approved (S01) | [date] | Stakeholder availability |
| Ready to code (S04) | [date] | S01–S03 complete |
| Feature complete (S05) | [date] | All tasks |
| Production deploy (S10) | [date] | S06–S09 done, human "deploy now" |

---

## History

| Date | Phase | Event | By |
|---|---|---|---|
| [date] | S00 | Kit initialized | setup-context.sh |
