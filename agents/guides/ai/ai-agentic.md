# Guide: AI / Agentic Engineering
<!-- RARV Cycle, SDD Lifecycle, Memory Architecture, MCP, Multi-Agent Orchestration -->

---

## The Agentic Engineering Stack

```
┌─────────────────────────────────────────────────────┐
│ AGENTS.md (Agent Context Layer)                      │
│  - Project `diagramming`, `domain-model`, `adaptive-architecture`, `compatibility-design` | diagram, domain, local-first, compatibility |
| `architecture-governance`, `error-handling-strategy`, `event-governance` | archunit, error handling, schema registry |identity, commands, architecture rules    │
│  - Workflow policies, research rules, self-heal limits│
├─────────────────────────────────────────────────────┤
│ Skills (Capability Layer)                            │
│  - Packaged workflows with triggers + constraints    │
│  - Invoked by keyword or explicit name               │
├─────────────────────────────────────────────────────┤
│ MCP Servers (Tool Layer — "Agent Hands")             │
│  - Context-7, GitHub, PostgreSQL, Semgrep, Playwright│
│  - Configured in MCP_CONFIG_TEMPLATE.json            │
├─────────────────────────────────────────────────────┤
│ Memory (Continuity Layer)                            │
│  - Working → Episodic → Semantic → Procedural        │
│  - Stored in agents/memory/                    │
└─────────────────────────────────────────────────────┘
```

---

## RARV Cycle — The Agent Cognitive Loop

Every task follows Reason → Act → Reflect → Verify:

### Reason
```
1. Read relevant context: AGENTS.md, CONSTITUTION.md, current task
2. Read CONTINUITY.md — what past failures are relevant?
3. Detect knowledge gaps → invoke knowledge-gap.skill if uncertain
4. Formulate explicit plan: what files, what tests, what outcome?
5. If security-sensitive: invoke threat-model.skill first
```

### Act
```
1. Write failing test (TDD Red)
2. Implement minimal code (TDD Green)
3. Use MCP tools for: DB queries, code search, external APIs, research
4. Update task status in project/tasks.md → IN_PROGRESS
```

### Reflect
```
Self-critique before claiming done:
- "Did I follow Library-First? Is business logic in the domain layer?"
- "Did I introduce any circular imports?"
- "Did I verify the API version via Context-7 (not training data)?"
- "Are all edge cases covered in tests?"
- "Would a security reviewer find issues here?"
```

### Verify
```
1. Run: [test command] → must be GREEN
2. Run: [typecheck command] → zero errors
3. Run: [lint command] → zero errors
4. Run: agentic-linter → no boundary violations
5. If FAIL: invoke self-heal.skill (max 5 attempts)
6. If still FAIL after 5: ESCALATE to human (stop all action)
```

---

## SDD Lifecycle — Spec-Driven Development

### Phase 1: Specify (`spec-writer.skill`)
```
Input: User goal ("Build X for Y")
Process:
  1. Identify actors, use cases, constraints
  2. Invoke Ambiguity Layer — ask clarifying questions
  3. Generate PRD.md with EARS requirements
  4. Define acceptance criteria (Given/When/Then)
Output: PRD.md — human reviews and approves
```

### Phase 2: Clarify (Ambiguity Layer, built into spec-writer.skill)
```
Questions the agent MUST ask before writing any requirement:
  - "Who are the users? What are their roles/permissions?"
  - "What happens when [edge case]?"
  - "What is explicitly out of scope for v1?"
  - "Are there regulatory requirements? (GDPR, HIPAA, PCI)"
  - "What are the performance expectations?"

No assumptions allowed — everything ambiguous must be clarified.
```

### Phase 3: Plan (`adr-writer.skill` + prod-architect persona)
```
Input: Approved PRD.md
Process:
  1. Identify architecture impact — which layers change?
  2. Create ADR for each significant technology decision
  3. Create C4 Level 1-3 diagrams
  4. Invoke `security-audit`, `threat-model`, `privacy-audit`, `compliance-review`, `legal-review` | security, threat, privacy, SOC2, legal |
| `access-control`, `data-governance`, `backup-recovery`, `queue-management` | rbac, lineage, backup, dlq |threat-model.skill for security features
  5. Write PLAN.md with ordered implementation phases
Output: PLAN.md + ADRs + threat model — human reviews and approves
```

### Phase 4: Decompose (15-Minute Rule)
```
Input: Approved PLAN.md
Process:
  1. Break each phase into atomic tasks
  2. Each task: achievable in ~15 minutes, single file/function
  3. Each task: has testable acceptance criteria
  4. Verify task ordering matches dependencies
Output: project/TASKS.md — reviewed by tech lead
```

### Phase 5: Implement (RARV cycle per task)
```
Input: project/tasks.md, AGENTS.md, CONSTITUTION.md, CONTINUITY.md
For each task:
  1. RARV cycle (above)
  2. Audit trail entry
  3. Task status → DONE
  4. sdlc-checkpoint at phase boundaries
```

---

## Memory Architecture — 4 Layers

### Working Memory
```
Scope:      Current context window
Contains:   Current task, recent code, this session's decisions
Lifetime:   Single session
Management: Managed automatically by the agent runtime
```

### Episodic Memory
```
Scope:      Project-level, persists across sessions
Location:   agents/memory/episodic/
Contains:   Past decisions, failed experiments per session (DECISION_LOG)
            Per-milestone snapshots (SESSION_SNAPSHOT/)
            Audit log of all actions (AUDIT_LOG.md)
Lifetime:   Project lifetime
Use:        session-resume.skill reads last 50 AUDIT_LOG entries + latest snapshot
```

### Semantic Memory
```
Scope:      Project-level, crystallized knowledge
Location:   agents/memory/semantic/PROJECT_KNOWLEDGE_TEMPLATE.md
Contains:   Verified facts: auth quirks, schema conventions, API constraints
            Research findings from research.skill
            Decisions that affect all future work
Lifetime:   Project lifetime (updated, not replaced)
Use:        session-resume.skill loads this at start
```

### Procedural Memory
```
Scope:      Global (across projects)
Location:   agents/skills/*.skill.md
Contains:   Immutable how-to guides (TDD cycle, debug flow, etc.)
            Referenced by agent keywords
Lifetime:   Stable — only updated when workflows change
Use:        Invoked on demand by trigger keywords
```

### CONTINUITY.md — The Most Important Memory File
```
Location:   agents/memory/CONTINUITY.md
Read:       EVERY session start (before any action)
Contains:   Past failures: "Tried X, failed because Y, switched to Z"
Prevents:   Agents repeating failed approaches across sessions

Entry format:
### [DATE] — [Brief title]
Context: What were you trying to do?
Approach tried: What did you try?
Why it failed: Root cause
Resolution: What worked, or "unresolved"
Tags: [library-conflict | type-error | architecture | security]
```

---

## EARS Syntax — Quick Reference

### All 5 Patterns

```
Ubiquitous (always):
  THE SYSTEM SHALL [action].

Event-Driven (triggered):
  WHEN [trigger]
  THE SYSTEM SHALL [response].

State-Driven (while in state):
  WHILE [state]
  THE SYSTEM SHALL [behavior].

Optional Feature (conditional):
  WHERE [feature enabled]
  THE SYSTEM SHALL [behavior].

Unwanted (negative):
  THE SYSTEM SHALL NOT [forbidden behavior].
```

### Bad vs Good Requirements

```
BAD (vague — not testable):
  "The system should be fast"
  "Users might be able to export data"
  "The API should handle errors gracefully"

GOOD (EARS — testable):
  WHEN an API request is made to any endpoint
  THE SYSTEM SHALL respond within 200ms at p99 under 100 concurrent requests.

  WHERE the data export feature is enabled for the account
  THE SYSTEM SHALL allow users to export their data in CSV or JSON format.

  WHEN an API error occurs
  THE SYSTEM SHALL return an RFC 7807 Problem Details JSON response with appropriate HTTP status code.
```

---

## MCP Configuration for Agentic Projects

```json
{
  "mcpServers": {
    "context7": { "command": "npx", "args": ["@context7/mcp-server"] },
    "sequential-thinking": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"] },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}" }
    }
  }
}
```

**Key MCP servers for agentic engineering:**
- **Context-7**: Up-to-date library docs (prevents hallucinated API usage)
- **Sequential Thinking**: Forces structured reasoning before acting
- **GitHub MCP**: Read PRs, issues, search code — agent awareness of project history
- **Semgrep MCP**: SAST security scanning from within the agent session

---

## 7-Gate Quality System

| Gate | Tool | Command | Pass Criteria |
|---|---|---|---|
| 1 Syntax/Lint | ESLint / Pint | `[lint command]` | 0 errors |
| 2 Type Safety | TypeScript / PHPStan | `[typecheck command]` | 0 errors |
| 3 Test Coverage | Vitest / Pest | `[coverage command]` | ≥ 96% |
| 4 Integration | Docker Compose | `docker compose run tests` | Pass |
| 5 Security | npm audit / Semgrep | `[security_scan]` | 0 critical CVEs |
| 6 Complexity | complexity-report | `npx complexity-report` | Max < 10 |
| 7 EARS Compliance | spec-analyze.skill | Manual | All reqs have tests |

All 7 gates must pass before any SDLC checkpoint after S05.

---

## When to Use Loki Mode (Multi-Agent)

```
Single agent is sufficient for:
  - Features with < 5 tasks
  - Bug fixes and small refactors
  - Code reviews and audits
  - Documentation updates

Switch to Loki Mode for:
  - New product builds (> 5 features)
  - Architecture migrations
  - Projects spanning multiple sessions/days
  - When single agent hits context limits
  - When parallel workstreams would benefit from specialization
```

See `agents/skills/brain/README_ORCHESTRATORS.md` for Loki Mode setup and persona guide.
