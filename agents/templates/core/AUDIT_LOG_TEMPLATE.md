# AUDIT_LOG.md — Project Audit Trail
<!-- APPEND ONLY — never delete or modify existing entries -->
<!-- Updated by: audit-trail.skill | Read by: session-resume.skill, integrity-check.skill -->
<!-- Project: [Project Name] | Started: [date] | Format version: 1.0 -->

---

## Log Format

```
| Timestamp (ISO 8601) | Session ID | Agent/Human | Action Type | Description | Outcome | References |
```

**Session ID format:** `S[SDLC-phase]-[sequential-number]` (e.g., `S01-001`, `S05-023`)

**Action Types:**
| Type | When to use |
|---|---|
| `DECISION` | A choice was made between options |
| `PHASE_TRANSITION` | SDLC phase changed (sdlc-checkpoint.skill) |
| `TASK_DONE` | A task completed successfully |
| `TASK_BLOCKED` | A task is stuck, human decision needed |
| `QUALITY_GATE` | Quality gate pass/fail result |
| `SECURITY_FINDING` | Security issue found (include severity) |
| `ADR_CREATED` | Architecture decision documented |
| `HUMAN_ESCALATION` | Agent escalated to human (5 attempts exhausted) |
| `SELF_HEAL_ATTEMPT` | Agent tried to self-fix (include attempt N/5) |
| `RESEARCH_FINDING` | Authoritative source verified |
| `HUMAN_APPROVED` | Human provided approval/decision |
| `ERROR` | Unexpected error encountered |
| `ROLLBACK` | A change was reverted |

**Outcome values:** `SUCCESS` | `FAIL` | `PASS` | `OPEN` | `RESOLVED` | `APPROVED` | `REJECTED` | `ESCALATED`

---

## Instructions for Agents

1. **Append a new row** for every significant action (do NOT edit existing rows)
2. **Do NOT overwrite** this file — always append
3. **Reference artifacts** by path or URL in the References column
4. **Be specific** in Description — "fixed auth bug" is bad; "removed missing null check on user.email in UserService.update() line 42" is good
5. For HUMAN_ESCALATION: add a note row below the entry with the escalation report summary

---

## Log Entries

| Timestamp | Session | Agent/Human | Action Type | Description | Outcome | References |
|---|---|---|---|---|---|---|
| [INIT] | S00-001 | setup-context.sh | PHASE_TRANSITION | agents/ kit initialized for project | SUCCESS | agents/README_FULL.md |

<!--
EXAMPLE ENTRIES (remove this comment block when using):

| 2025-03-15T09:00:00Z | S01-001 | prod-pm | DECISION | Chose EARS format for requirements over user story format | SUCCESS | docs/PRD.md |
| 2025-03-15T09:30:00Z | S01-001 | prod-pm | PHASE_TRANSITION | PRD.md completed — awaiting human approval for S01 | OPEN | docs/PRD.md |
| 2025-03-15T10:00:00Z | S01-001 | human:alice | HUMAN_APPROVED | PRD.md approved — 12 EARS requirements signed off | APPROVED | docs/PRD.md |
| 2025-03-15T10:01:00Z | S01-001 | sdlc-checkpoint | PHASE_TRANSITION | S01 Requirements checkpoint created | SUCCESS | agents/memory/episodic/SESSION_SNAPSHOT/S01_requirements.md |
| 2025-03-15T11:00:00Z | S02-001 | prod-architect | ADR_CREATED | Chose Prisma over TypeORM — performance + type safety | ACCEPTED | docs/architecture/decisions/ADR-001-prisma.md |
| 2025-03-15T11:30:00Z | S02-001 | prod-architect | DECISION | Chose Clean Architecture — domain/application/adapters/infra/main | ACCEPTED | docs/PLAN.md |
| 2025-03-15T14:00:00Z | S05-001 | eng-backend | TASK_DONE | T-001: Created User domain entity with email value object | SUCCESS | src/domain/user.ts |
| 2025-03-15T14:30:00Z | S05-001 | eng-backend | SELF_HEAL_ATTEMPT | T-002: TypeScript error on UserDto.email — attempt 1/5 — null check missing | FAIL | src/application/create-user.use-case.ts:42 |
| 2025-03-15T14:35:00Z | S05-001 | eng-backend | TASK_DONE | T-002: Fixed type error — added null guard before email access | SUCCESS | src/application/create-user.use-case.ts |
| 2025-03-15T16:00:00Z | S05-001 | eng-backend | TASK_BLOCKED | T-020: Cannot implement payment integration — unclear if Stripe or Paddle | OPEN | project/tasks.md |
| 2025-03-15T16:01:00Z | S05-001 | eng-backend | HUMAN_ESCALATION | T-020 blocked: Payment provider not decided. Options: Stripe (fees: 2.9%) vs Paddle (fees: 5%). Recommend Stripe (direct settlement). | ESCALATED | project/tasks.md |
| 2025-03-15T16:45:00Z | S05-001 | human:bob | DECISION | Use Stripe for payment processing — direct settlement preferred | APPROVED | — |
| 2025-03-15T17:00:00Z | S06-001 | orch-judge | QUALITY_GATE | Gate 3 Tests: 247 pass, 0 fail, 0 skip, 84% coverage | PASS | — |
| 2025-03-15T17:05:00Z | S07-001 | ops-security | SECURITY_FINDING | HIGH: No rate limit on /auth/login endpoint — brute force possible | OPEN | src/adapters/http/auth.controller.ts:23 |
| 2025-03-15T17:30:00Z | S07-001 | eng-backend | TASK_DONE | Added rate limiting to /auth/login: 5 req/min per IP | SUCCESS | src/adapters/http/auth.controller.ts |
| 2025-03-15T17:31:00Z | S07-001 | ops-security | SECURITY_FINDING | HIGH: No rate limit on /auth/login — RESOLVED | RESOLVED | src/adapters/http/auth.controller.ts |
| 2025-03-15T18:00:00Z | S08-001 | human:alice | HUMAN_APPROVED | Code review approved — all feedback addressed | APPROVED | PR #42 |
| 2025-03-15T18:01:00Z | S10-001 | sdlc-checkpoint | PHASE_TRANSITION | S10 Production deployed. Project complete | SUCCESS | agents/memory/episodic/SESSION_SNAPSHOT/S10_production.md |

END EXAMPLES -->
