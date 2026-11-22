---
name: audit-trail
description: "Appends one structured row per decision, phase change, approval or failure to agents/memory/AUDIT_LOG.md. Use when a decision, human approval, gate result or task outcome must be recorded, or when someone asks why something was done."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/audit-trail.skill.md"
  tags: "core"
  core: "true"
  context_cost: "low"
---
# Audit Trail Skill

## Goal
Maintain an append-only, chronological record of all significant decisions, changes, and outcomes for compliance, debugging, project continuity, and team transparency.

## When to Auto-Log (triggered by other skills)
- Every SDLC phase transition (sdlc-checkpoint.skill)
- Every human decision (when human provides direction or approval)
- Every ADR creation (adr-writer.skill)
- Every failed self-heal attempt and resolution (self-heal.skill)
- Every security finding and its remediation (security-audit.skill)
- Every task DONE, BLOCKED, or FAILED
- Every quality gate pass/fail with scores
- Every research finding that changes implementation approach

## Log Entry Format

Append to: `agents/memory/AUDIT_LOG.md`

**Table format:**
```
| [ISO datetime] | [Session-ID] | [Agent/Human] | [Action Type] | [Description] | [Outcome] | [References] |
```

**Action Types:**
```
DECISION         - A choice made between options
PHASE_TRANSITION - SDLC phase changed
TASK_DONE        - A task was completed successfully
TASK_BLOCKED     - A task is stuck, human decision needed
QUALITY_GATE     - Quality gate pass/fail result with scores
SECURITY_FINDING - Security issue found (severity + description)
ADR_CREATED      - Architecture decision documented
HUMAN_ESCALATION - Agent escalated to human (blocked after 5 attempts)
SELF_HEAL_ATTEMPT- Agent tried to fix itself (attempt N of 5)
RESEARCH_FINDING - Authoritative source verified (for future reference)
ERROR            - Unexpected error encountered
ROLLBACK         - Change was reverted
HUMAN_APPROVED   - Human provided approval for a phase or decision
```

A `HUMAN_APPROVED` row holds the phase, the date and the human's own words. Phases S00, S01, S02, S07, S08 and S10 are not advanced without one.

## Steps

1. **Determine what needs to be logged**
   - Was a decision made? (architecture, library choice, requirement interpretation)
   - Did a task complete or get blocked?
   - Did a quality gate run?
   - Did a human provide input or approval?

2. **Write the log entry**
   ```bash
   # Get current timestamp
   date -u +"%Y-%m-%dT%H:%M:%SZ"
   ```

   **Example entries:**
   ```
   | 2025-03-15T14:23:00Z | SES-002 | prod-pm | PHASE_TRANSITION | PRD.md approved by human | SUCCESS | docs/PRD.md |
   | 2025-03-15T14:25:00Z | SES-002 | human | HUMAN_APPROVED | Approved PRD.md — proceed to design | APPROVED | docs/PRD.md |
   | 2025-03-15T15:10:00Z | SES-003 | prod-architect | ADR_CREATED | Chose Prisma over TypeORM for ORM | ACCEPTED | docs/architecture/decisions/ADR-001-prisma.md |
   | 2025-03-15T16:00:00Z | SES-004 | eng-backend | TASK_DONE | Implemented CreateUserUseCase | SUCCESS | src/application/create-user.use-case.ts |
   | 2025-03-15T16:45:00Z | SES-004 | eng-backend | SELF_HEAL_ATTEMPT | Type error on UserDto.email field — attempt 1/5 | FAIL | src/application/create-user.use-case.ts:42 |
   | 2025-03-15T16:50:00Z | SES-004 | eng-backend | TASK_DONE | Fixed type error via research (strict null check) | SUCCESS | src/application/create-user.use-case.ts |
   | 2025-03-15T17:00:00Z | SES-004 | ops-security | SECURITY_FINDING | HIGH: Missing rate limit on /auth/login | OPEN | src/adapters/http/auth.controller.ts:23 |
   | 2025-03-15T17:30:00Z | SES-005 | orch-judge | QUALITY_GATE | G3 Coverage: 99.2% of new and changed lines (>= 99%), 247 tests pass | PASS | — |
   ```

3. **APPEND ONLY — never modify existing entries**
   - Use bash append operator: `>> agents/memory/AUDIT_LOG.md`
   - Never use a write that overwrites the file
   - If a decision is reversed: add a new ROLLBACK entry (don't delete the original)

4. **Verify the append worked**
   - Read the last few lines to confirm the entry was added correctly

## Querying the Audit Log

For humans reviewing history:
```bash
# Find all security findings
grep "SECURITY_FINDING" agents/memory/AUDIT_LOG.md

# Find all human decisions
grep "HUMAN_APPROVED\|DECISION" agents/memory/AUDIT_LOG.md

# Find all escalations
grep "HUMAN_ESCALATION" agents/memory/AUDIT_LOG.md

# Find history for a specific file
grep "auth.controller.ts" agents/memory/AUDIT_LOG.md
```

## Constraints
- APPEND ONLY — never delete or modify existing entries
- Every SDLC phase transition must be logged immediately
- Security findings must be logged even if they will be fixed immediately
- Human decisions must be logged with the actual decision made (not just "human approved")
- Log is shared across all agent sessions — it provides continuity

## Output Format
New row appended to AUDIT_LOG.md. No output to user unless requested.

## Limits and safety
- Append only (`>>`); never rewrite or delete a row. A reversal is a new ROLLBACK row.
- Write an intent row before a risky action and an outcome row after it; an intent row with no outcome row means the action is unfinished.
- Remove newlines and `|` from the description before appending, so one entry stays one row.
- Log references, not secrets or personal data. If personal data is already in the log, tell the human; do not edit the log yourself.
- If your platform provides an append-only file mode, a protected branch or a CI check on the log, use it to enforce the append-only rule.
- Tell the human at once about a SECURITY_FINDING row; do not wait for someone to read the log.
