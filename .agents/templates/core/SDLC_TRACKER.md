# SDLC Tracker
<!-- Updated by: sdlc-checkpoint.skill | Read by: session-resume.skill, integrity-check.skill -->
<!-- Project: [Project Name] | Started: [date] -->

---

## Current Status

```
Current Phase: S[XX] — [Phase Name]
Status:        NOT_STARTED | IN_PROGRESS | BLOCKED | COMPLETED
Last updated:  [date]
Updated by:    [agent/human]
```

---

## Phase Progress Board

| Phase | Name | Status | Started | Completed | Approver | Gate Criteria |
|---|---|---|---|---|---|---|
| S01 | Requirements | NOT_STARTED | — | — | — | PRD.md with EARS, human approval |
| S02 | Design | NOT_STARTED | — | — | — | Architecture + ADRs + threat model |
| S03 | Specification | NOT_STARTED | — | — | — | Tech spec + API contracts |
| S04 | Tasks | NOT_STARTED | — | — | — | All tasks decomposed to 15-min units |
| S05 | Implementation | NOT_STARTED | — | — | — | All tasks.md items DONE |
| S06 | Testing | NOT_STARTED | — | — | — | Tests pass, coverage ≥ 96%, 7 gates |
| S07 | Security | NOT_STARTED | — | — | — | SECURITY_CHECKLIST.md 100%, 0 critical CVEs |
| S08 | Review | NOT_STARTED | — | — | — | Human code review approved |
| S09 | Staging | NOT_STARTED | — | — | — | Deployed + smoke tests passing |
| S10 | Production | NOT_STARTED | — | — | — | Deployed + rollback documented |

**Status values:** `NOT_STARTED` | `IN_PROGRESS` | `BLOCKED` | `COMPLETED`

---

## Definition of Done — Per Phase

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

### S02 — Design
```
[ ] Architecture approach documented in PLAN.md
[ ] C4 Level 1+2 diagrams in docs/architecture/ (or documented exception)
[ ] ADR created for every significant technology choice
[ ] Threat model completed for ALL security-sensitive features
[ ] Human approved architecture approach
[ ] SESSION_SNAPSHOT/S02_design.md created
```

### S03 — Specification
```
[ ] SPEC_TEMPLATE.md completed: domain model, API contracts, DB changes
[ ] OpenAPI spec at docs/api/openapi.yaml (or equivalent)
[ ] Migration plan documented (if DB changes)
[ ] Testing strategy defined per layer
[ ] Human approved technical specification
[ ] SESSION_SNAPSHOT/S03_specification.md created
```

### S04 — Tasks
```
[ ] All PLAN.md items decomposed into TASKS_TEMPLATE.md
[ ] Each task: achievable in ~15 minutes
[ ] Each task: has testable acceptance criteria
[ ] Tasks have correct dependency ordering
[ ] No ambiguous tasks ("do the stuff" — must be specific files/functions)
[ ] SESSION_SNAPSHOT/S04_tasks.md created
```

### S05 — Implementation
```
[ ] All tasks in tasks.md have status DONE (none TODO/IN_PROGRESS/BLOCKED)
[ ] TDD followed for each task: failing test written first
[ ] Each task commit references the task ID
[ ] AUDIT_LOG.md has TASK_DONE entry for each task
[ ] SESSION_SNAPSHOT/S05_implementation.md created
```

### S06 — Testing
```
[ ] [test command] passes: 0 failing, 0 unexpected skips
[ ] Coverage >= 96% (run [coverage command])
[ ] Gate 1 Lint: 0 errors
[ ] Gate 2 Typecheck: 0 errors
[ ] Gate 3 Coverage: >= 96%
[ ] Gate 4 Integration: Docker Compose tests pass
[ ] Gate 5 Security: npm/composer audit clean (0 critical/high CVEs)
[ ] Gate 6 Complexity: max cyclomatic complexity < 10
[ ] Gate 7 EARS compliance: all requirements have tests
[ ] agentic-linter: 0 architecture violations
[ ] SESSION_SNAPSHOT/S06_testing.md created
```

### S07 — Security
```
[ ] security-audit.skill run on full codebase
[ ] SECURITY_CHECKLIST.md 100% complete
[ ] 0 critical CVEs in dependencies
[ ] 0 high CVEs unresolved (or risk accepted by human)
[ ] gitleaks detect: CLEAN (no secrets in git)
[ ] All threat model mitigations implemented
[ ] Human security approval
[ ] SESSION_SNAPSHOT/S07_security.md created
```

### S08 — Review
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
[ ] Production deploy completed
[ ] Database migrations applied to production
[ ] Smoke tests passing in production
[ ] Monitoring/alerting active for new feature
[ ] Rollback plan documented and verified
[ ] No error spike in first 30 minutes post-deploy
[ ] SESSION_SNAPSHOT/S10_production.md created
[ ] Git tag: v[semver] created
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
| Ready to code (S04) | [date] | S01+S02+S03 complete |
| Feature complete (S05) | [date] | All tasks |
| Production deploy (S10) | [date] | S06-S09 gates |

---

## History

| Date | Phase | Event | By |
|---|---|---|---|
| [date] | S00 | Kit initialized | setup-context.sh |
