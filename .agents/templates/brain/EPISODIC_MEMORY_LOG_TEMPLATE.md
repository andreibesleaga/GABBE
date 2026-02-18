# EPISODIC_MEMORY_LOG_TEMPLATE.md — Service Experience Log

> **Purpose**: Long-term record of "events" and "lessons" learned by the agent.
> **Updated by**: `episodic-consolidation.skill.md`
> **Read by**: `session-resume.skill.md`, `research.skill.md`

## Session [SESSION_ID] — [DATE]

### 1. Narrative Summary
*Brief story of what happened in this session.*
We attempted to refactor the user service. We started by creating a new interface, but hit a circular dependency issue with the `AuthService`. We resolved it by extracting a shared `types` module.

### 2. Key Events (Episodes)
| Time | Event Type | Description | Emotion/Result |
|---|---|---|---|
| 10:00 | START | Started refactoring `UserService` | Optimistic |
| 10:15 | ERROR | Circular dependency detected | Frustrated |
| 10:30 | BREAKTHROUGH | Realized `UserType` is shared | Relieved |
| 10:45 | SUCCESS | Refactor complete, tests passed | Satisfied |

### 3. Consolidated Lessons (Semantic Memory)
*Generalizable rules extracted from these episodes.*
- **Rule**: When two services depend on each other's types, extract the types to a separate module immediately.
- **Pattern**: Circular dependencies often manifest as "Module not found" or "Undefined" at runtime in Node.js.
- **Tactic**: Use `madge` to check for circular dependencies before starting a big refactor.

### 4. Unresolved Issues
- The `AuthService` tests are slow (needs optimization).
