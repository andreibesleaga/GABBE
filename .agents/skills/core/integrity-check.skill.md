---
name: integrity-check
description: End-to-end 8-dimension verification — requirements through delivery, all aligned and correct
triggers: [integrity, verify all, are we done, is it complete, end-to-end check, check everything, full verification]
context_cost: high
---

# Integrity Check Skill

## Goal
Verify the ENTIRE project is consistent and correct from requirements to delivery. Catch regressions, drift, and gaps across 8 dimensions. Only orch-judge or human may sign off as "INTEGRITY VERIFIED."

## 8 Dimensions of Integrity

### Dimension 1 — Requirements Integrity
- Does spec.md (or SPEC_TEMPLATE.md) cover ALL EARS requirements from PRD.md?
- Run spec-analyze.skill to check alignment
- Check: no requirements without tests
- Result: GREEN (all covered) | YELLOW (minor gaps) | RED (requirements missing)

### Dimension 2 — Architecture Integrity
- Run agentic-linter.skill: zero architecture boundary violations
- Run `npx madge --circular src/` or `vendor/bin/deptrac`: zero circular dependencies
- Check: all architectural decisions have ADRs in `docs/architecture/decisions/`
- Result: GREEN / YELLOW / RED

### Dimension 3 — Implementation Integrity
- All tasks in tasks.md have status: DONE
- No tasks with status TODO, IN_PROGRESS, or BLOCKED
- Every feature from PRD.md has corresponding code
- Result: GREEN / YELLOW / RED

### Dimension 4 — Test Integrity
```bash
[test command]          # Run all tests — MUST be 100% green
[coverage command]      # Coverage MUST be >= 96%
```
- Zero failing tests (not even flaky ones currently failing)
- Zero skipped tests without documented reason
- Integration tests exist for all API endpoints
- Result: GREEN / YELLOW / RED

### Dimension 5 — Security Integrity
```bash
[security_scan command]  # dependency audit — zero critical/high CVEs
```
- SECURITY_CHECKLIST.md fully completed (not partially)
- Threat model exists for all security-sensitive features
- No secrets detected by gitleaks
- OWASP Top 10 items checked
- Result: GREEN / YELLOW / RED

### Dimension 6 — Tech Debt Integrity
- No uncatalogued TODO/FIXME/HACK markers (all have task tickets)
- Cyclomatic complexity < 10 for all modified files
- No dead code in production branches
- TECH_DEBT_TEMPLATE.md entries are current
- Result: GREEN / YELLOW / RED

### Dimension 7 — Documentation Integrity
- All public APIs have docstrings/JSDoc
- README reflects current state (not aspirational)
- `docs/api/openapi.yaml` is in sync with actual implementation (if exists)
- C4 diagrams reflect current architecture (if docs/architecture/ exists)
- Result: GREEN / YELLOW / RED

### Dimension 8 — SDLC Integrity
- SDLC_TRACKER.md phase matches actual state of the project
- PROJECT_STATE.md current phase is accurate
- All SESSION_SNAPSHOT files exist for completed phases
- AUDIT_LOG.md has entries for all major decisions
- Result: GREEN / YELLOW / RED

## Steps

1. **Run all 8 dimension checks** (in order of priority)
   - Each dimension: run the relevant commands, read the relevant files
   - Rate each: GREEN / YELLOW / RED with specific evidence

2. **For each RED dimension**: list specific items that must be fixed

3. **For each YELLOW dimension**: list items to address before production

4. **Generate Integrity Report**
   ```markdown
   ## Integrity Report

   Date: [date]
   Project phase: [current SDLC phase]
   Run by: [agent/human]

   | Dimension | Status | Issues Found |
   |---|---|---|
   | 1. Requirements | GREEN | None |
   | 2. Architecture | RED | 2 circular deps in users module |
   | 3. Implementation | YELLOW | 1 task still IN_PROGRESS |
   | 4. Tests | GREEN | 247 passing, 84% coverage |
   | 5. Security | GREEN | SECURITY_CHECKLIST 100% |
   | 6. Tech Debt | YELLOW | 3 uncatalogued TODOs |
   | 7. Documentation | YELLOW | /api/users endpoint missing JSDoc |
   | 8. SDLC | GREEN | All snapshots current |

   ### OVERALL STATUS: RED (1 RED dimension = not release-ready)

   ### Blocking Issues (must fix before release)
   - [ARCH] Circular dependency: UserService <-> OrderService
     Fix: Extract IUserQueryPort interface

   ### Non-Blocking Issues (address before next sprint)
   - [IMPL] CreatePaymentTask still IN_PROGRESS
   - [DEBT] 3 TODO markers without task tickets
   - [DOCS] Missing JSDoc on 2 public functions

   ### INTEGRITY VERIFIED: NO
   Ready for production: NO
   Ready for staging: YES (if blocking issues fixed)
   ```

5. **Recommended actions** (priority ordered)
   - RED items: fix immediately (blocking)
   - YELLOW items: fix before next gate
   - GREEN items: monitor

6. **Sign-off** (only orch-judge persona or human may sign)
   - When all dimensions GREEN: "INTEGRITY VERIFIED — READY FOR [next gate]"

## Constraints
- NEVER mark integrity as verified if any dimension is RED
- NEVER skip dimensions — partial verification is not verification
- Security dimension RED = hard block on production deployment
- Run this check before every SDLC checkpoint and before any production deploy

## Output Format
8-dimension integrity report with GREEN/YELLOW/RED per dimension + OVERALL STATUS + prioritized action list.
