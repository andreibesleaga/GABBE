# CONTINUITY — Project Failure Memory
<!-- Checked EVERY session start (RARV Reason Phase — mandatory) -->
<!-- Prevents agents from repeating past failed approaches -->
<!-- Append new entries. Never delete. Mark RESOLVED if superseded. -->

---

## How to Use This File

During RARV Reason phase, EVERY agent MUST:
1. Scan this file for entries related to the current module or operation
2. If relevant entry found → apply the recorded resolution WITHOUT rediscovering
3. After a novel failure is resolved → add an entry here

Entry format:
```
### [Module/Area] — [Short description]
**Failed approach**: [what was tried]
**Why it failed**: [root cause]
**Resolution**: [what actually worked]
**Date**: [YYYY-MM-DD]
**Status**: ACTIVE | RESOLVED (superseded by entry #N)
```

---

## Entries

*(Empty — add entries as failures are encountered and resolved)*

<!-- Example entry (delete this comment when real entries are added):

### Auth Module — JWT token refresh race condition
**Failed approach**: Checking token expiry in middleware and refreshing inline
**Why it failed**: Concurrent requests both see expired token, both refresh, second refresh invalidates first
**Resolution**: Refresh tokens via dedicated /api/v1/auth/refresh endpoint with mutex lock in Redis
**Date**: 2026-01-15
**Status**: ACTIVE
-->

---

## Quick Reference — Common Failure Patterns to Avoid

*(Populated as project matures — move crystallized patterns here)*

| Pattern | Area | What to avoid | What to do instead |
|---------|------|---------------|-------------------|
| *(none yet)* | | | |
