# Session Snapshot — S[XX]_[PHASE_NAME]
<!-- Created by: sdlc-checkpoint.skill -->
<!-- Store in: agents/memory/episodic/SESSION_SNAPSHOT/S[XX]_[phase].md -->
<!-- IMMUTABLE after creation — never overwrite, create new snapshot for revisions -->

---

**Snapshot ID:** S[XX]-[YYYYMMDD]-[HH]
**Timestamp:** [ISO 8601: 2025-03-15T14:30:00Z]
**SDLC Phase:** S[XX] — [Phase Name: REQUIREMENTS/DESIGN/SPEC/TASKS/IMPLEMENTATION/TESTING/SECURITY/REVIEW/STAGING/PRODUCTION]
**Created by:** [agent persona name or "human"]
**Project:** [Project name from AGENTS.md]

---

## 1. Current Project State

```
SDLC Phase:           S[XX] — [Phase Name]
Phase status:         COMPLETED / IN_PROGRESS
Gate criteria met:    YES / NO (if NO, explain)
Overall progress:     [X]/10 phases complete
Confidence:           HIGH / MEDIUM / LOW
```

---

## 2. What Was Decided / Built This Phase

<!-- Summary of the key work done since the last snapshot -->

**Key decisions:**
- [Decision 1: e.g., "Chose Prisma as ORM — see ADR-003"]
- [Decision 2: e.g., "Deferred multi-currency support to v2 — PRD updated"]

**Key artifacts produced:**
- [Artifact 1: e.g., "PRD.md with 12 EARS requirements — human approved 2025-03-15"]
- [Artifact 2: e.g., "PLAN.md with 5 implementation phases"]
- [Artifact 3: e.g., "ADR-001 to ADR-003 in docs/architecture/decisions/"]

**Key code changes:**
- [e.g., "Implemented CreateUserUseCase — all 8 unit tests passing"]
- [e.g., "Database migration: added users table + email_verified_at column"]

---

## 3. Artifact Status

| Artifact | Status | Location | Notes |
|---|---|---|---|
| PRD.md | exists / MISSING | docs/PRD.md | Human approved [date] |
| SPEC.md | exists / MISSING | docs/SPEC.md | — |
| PLAN.md | exists / MISSING | docs/PLAN.md | — |
| project/tasks.md | [N/M tasks done] | project/tasks.md | [N] TODO, [N] IN_PROGRESS, [N] DONE, [N] BLOCKED |
| ADRs | [N] created | docs/architecture/decisions/ | Latest: ADR-[NNN] |
| Threat models | [N] created | docs/security/threat-models/ | — |
| OpenAPI spec | exists / MISSING | docs/api/openapi.yaml | — |

---

## 4. Test Status

```
Last run:     [ISO datetime or "never"]
Pass:         [N]
Fail:         [0] (must be 0 at checkpoint)
Skip:         [0] (or documented reason for each skip)
Coverage:     [X]% (must be >= 96% at S06+)

Flaky tests:  [none / list any known flaky tests]
Last test cmd: [exact command run]
```

---

## 5. Quality Gate Status

| Gate | Status | Last Run | Score/Notes |
|---|---|---|---|
| Gate 1: Lint | PASS/FAIL | [date] | [0 errors] |
| Gate 2: Typecheck | PASS/FAIL | [date] | [0 errors] |
| Gate 3: Coverage | PASS/FAIL | [date] | [X]% |
| Gate 4: Integration | PASS/FAIL | [date] | [N] endpoints tested] |
| Gate 5: Security scan | PASS/FAIL | [date] | [0 critical CVEs] |
| Gate 6: Complexity | PASS/FAIL | [date] | [max complexity: X] |
| Gate 7: EARS compliance | PASS/FAIL | [date] | [N/M requirements covered] |

---

## 6. Security Status

```
Last security audit:      [date or "not run"]
Open CVEs (critical):     [0]
Open CVEs (high):         [0]
SECURITY_CHECKLIST:       [X]% complete
Threat models created:    [N]
Last gitleaks scan:       [date] — CLEAN / ISSUES FOUND
```

---

## 7. Architecture Status

```
Last agentic-linter run:  [date or "not run"]
Architecture violations:  [0] (must be 0 at S06+)
Circular dependencies:    [0]
ADRs for decisions:       ALL / [N missing]
```

---

## 8. Open Issues & Known Debt

**Blocked tasks:**
- [Task ID]: [reason it's blocked]

**Pending human decisions:**
- [Question 1: e.g., "Should we support SSO in v1 or defer to v2?"]

**Known bugs (not blocking):**
- [Bug 1: file.ts:42 — non-critical edge case]

**Tech debt backlog size:** [N items] — see TECH_DEBT_TEMPLATE.md

---

## 9. Memory Pointers

<!-- Help the next session quickly find key context -->

**Key ADRs to read:**
- ADR-[NNN]: [topic — link]

**Key CONTINUITY.md entries relevant to next phase:**
- [Any past failures that the next phase should be aware of]

**Semantic knowledge to load:**
- [Key facts in agents/memory/semantic/ relevant to continuing work]

---

## 10. Next Actions

<!-- Ordered list of what needs to happen next to advance the project -->

1. [First thing to do in the next session]
2. [Second thing]
3. [Third thing]

**Next phase entry criteria:**
- [ ] [What must be true to start Phase S[XX+1]]
- [ ] [Human approval received for: X]

---

## 11. Gate Criteria — Verified This Checkpoint

<!-- Document what was checked and confirmed for this phase gate -->

- [x] [criterion 1 — verified]
- [x] [criterion 2 — verified]
- [ ] [criterion 3 — NOT MET (reason)]

**Gate PASSED: YES / NO**

If NO: list what must be done before this checkpoint is valid.
