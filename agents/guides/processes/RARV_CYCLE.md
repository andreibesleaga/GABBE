# RARV Cycle — Reason, Act, Reflect, Verify

> The per-agent cognitive loop. Every task follows this cycle.
> Used by all eng-* personas in Loki Mode and by single agents in standard mode.

---

## The Full Loop

```
Task assigned by orch-planner
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  REASON                                              │
│  1. Load task context                               │
│  2. Read CONTINUITY.md (past failures)              │
│  3. Detect knowledge gaps                           │
│  4. Formulate explicit plan                         │
└─────────────────────────────────────────────────────┘
    │
    ├─── Knowledge gap? ──► research.skill (via orch-researcher)
    │                           │
    │         Verified source found ──► Store in semantic memory
    │         Not found ──► Human escalation
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  ACT                                                 │
│  1. Write failing test (TDD Red)                    │
│  2. Implement minimal code (TDD Green)              │
│  3. Use MCP tools as needed                         │
│  4. Update task: status → IN_PROGRESS               │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  REFLECT                                             │
│  1. Library-First check: is business logic in domain?│
│  2. Circular import check: did I introduce any?     │
│  3. API version check: via Context-7, not training? │
│  4. Edge case check: are null/empty/error paths     │
│     covered by tests?                               │
│  5. Security check: did I validate inputs? Any PII  │
│     in logs? Any hardcoded secret?                  │
│  6. Governance check: Data classified? Events       │
│     typed? DLQs configured?                         │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  VERIFY                                              │
│  Run: [test command] ──► GREEN?                     │
│  Run: [typecheck] ──────► zero errors?              │
│  Run: [lint] ───────────► zero errors?              │
│  Run: agentic-linter ───► no violations?            │
└─────────────────────────────────────────────────────┘
    │
    ├─── PASS ──► audit-trail.skill → task: DONE ──► DONE
    │
    └─── FAIL ──► self-heal.skill
                      │
                      ├─ Attempt 1-4 ──► diagnose → fix → verify ──► loop back
                      │
                      └─ Attempt 5 FAIL ──► ESCALATE TO HUMAN
                                              │
                                              ├─ Write escalation report
                                              ├─ AUDIT_LOG.md: HUMAN_ESCALATION
                                              ├─ project/tasks.md: status → BLOCKED
                                              └─ WAIT for human decision
                                                      │
                                                    Human responds
                                                      │
                                                  Apply decision ──► loop back to ACT
```

---

## REASON Phase — Detailed

### 1. Load Task Context
```
Read from orch-planner's task assignment:
  - Task description and acceptance criteria
  - Which layer/module this task belongs to
  - Dependencies: what must be done before this task

Read from AGENTS.md:
  - Architecture rules for this project
  - Operational commands (test, lint, typecheck)
  - Forbidden patterns

Read from CONSTITUTION.md:
  - Immutable project law relevant to this task
```

### 2. Read CONTINUITY.md (MANDATORY — never skip)
```
Scan for entries related to:
  - This module or layer
  - Similar operations (if implementing auth, check auth-related entries)
  - Libraries being used in this task

If relevant entry found:
  "Past failure: [X]. Avoid [approach]. Use [resolution] instead."
  Apply the recorded resolution without rediscovery.
```

### 3. Detect Knowledge Gaps
```
Ask yourself: "Can I cite an official Tier 1/2 source for each API I'm about to call?"

Research Gate — mandatory before:
  - Using a library not in package.json / composer.json
  - Calling an API method not recently verified
  - Implementing any security or cryptographic operation
  - Interpreting any regulatory requirement

If gap found: invoke knowledge-gap.skill → orch-researcher
If orch-researcher finds answer: proceed with verified knowledge
If orch-researcher cannot find answer: escalate to human
```

### 4. Formulate Explicit Plan
```
Write out (even briefly) before touching any file:
  - "I will create: [file list]"
  - "I will modify: [file list + what changes]"
  - "I will write tests for: [behaviors]"
  - "This change affects layers: [list]"
  - "Potential risks: [list]"

For complex tasks: write mini-plan to project/tasks.md task notes
```

---

## ACT Phase — Detailed

### TDD Integration
```
Step 1: Write failing test
  - Create test file if it doesn't exist
  - Write test that captures the EXACT acceptance criteria
  - Run test → MUST FAIL (false-positive check!)
  - If it passes immediately: test is broken, fix the test

Step 2: Write minimal implementation
  - Implement ONLY what's needed to pass the test
  - No gold-plating, no premature optimization
  - No features not covered by a failing test

Step 3: Run tests → must be GREEN
```

### MCP Tool Usage
```
Context-7 MCP:     Verify library API before calling
GitHub MCP:        Search existing code for patterns, check PRs
PostgreSQL MCP:    Introspect schema before migrations
Playwright MCP:    Browser automation for visual TDD
Semgrep MCP:       Security scan while implementing security features
Sequential Think:  Complex multi-step reasoning before acting
```

---

## REFLECT Phase — Detailed

Self-critique questions (answer before claiming done):

```
Architecture:
  "Is business logic in the correct layer (domain/application)?"
  "Are there any new imports from outer layers in inner layers?"
  "Did I create any new circular dependencies?"

Code Quality:
  "Is cyclomatic complexity < 10 for new/modified functions?"
  "Are there any magic numbers or strings that should be constants?"
  "Is any function > 30 lines? Should it be extracted?"

Security:
  "Are all user inputs validated at this layer boundary?"
  "Is there any PII in log statements?"
  "Are there any hardcoded secrets?"
  "For auth/data features: was a threat model done?"

Governance:
  "Data: Is new data classified (PII/Public/Confidential)?"
  "Events: Do new events have a defined Schema?"
  "Async: Does the new consumer have a DLQ?"

Tests:
  "Are null/undefined edge cases tested?"
  "Are error paths tested?"
  "Are boundary values tested (empty string, max length, etc.)?"
```

---

## VERIFY Phase — Detailed

### Verification Commands (from AGENTS.md)
```bash
# Run in order — fix each before proceeding to next
[test command]              # All tests MUST be green
[typecheck command]         # Zero type errors
[lint command]              # Zero lint errors
npx madge --circular src/   # Zero circular dependencies (optional, run periodically)
```

### Verification Failures → self-heal.skill
```
If any verification fails:
  - Classify error type (type, test, lint, runtime, unknown)
  - Apply fix (see self-heal.skill for full procedure)
  - Re-run verification
  - Repeat up to 5 times
  - After 5: escalate to human
```

---

## Integration with Memory System

### After Successful RARV
```
1. Update project/tasks.md: task status → DONE
2. Write AUDIT_LOG.md entry: TASK_DONE
3. Store any research findings in semantic/PROJECT_KNOWLEDGE_TEMPLATE.md
4. If pattern worth remembering: add to semantic memory
   Example: "Prisma cursor pagination works with: { cursor: { id }, take: 20, skip: 1 }"
```

### After Failed RARV (escalation)
```
1. Write AUDIT_LOG.md entry: HUMAN_ESCALATION
2. Update project/tasks.md: task status → BLOCKED
3. Write to CONTINUITY.md: what was tried and why it failed
   This prevents the same failure in future sessions
4. Wait for human decision
```

---

## RARV in Context of Multi-Session Projects

```
Session 1: Complete tasks T-001 to T-020 via RARV
  → AUDIT_LOG records all decisions
  → SESSION_SNAPSHOT saved at end

[Interruption — session ends]

Session 2: session-resume.skill loads all memory
  → CONTINUITY.md reviewed (prevents repeating T-015's mistake)
  → AUDIT_LOG last 50 entries reviewed
  → Continue from T-021 via RARV
```

The RARV cycle is stateless per-task but accumulates knowledge through the memory system across sessions.
