---
name: compatibility-design
description: Plan for changing a system without breaking users — expand-contract database migrations, API versioning, deprecation notices, feature flags. Use when a change would break clients or needs zero downtime.
triggers: [compatibility, migration, versioning, breaking change, deprecation, legacy support, expand contract]
tags: [architecture]
context_cost: medium
---
# Compatibility Design Skill

## Goal
To evolve systems without breaking existing users or downtime.

## Capabilities

### 1. Database Migrations (Zero Downtime)
-   **Expand & Contract Pattern**:
    1.  **Expand**: Add new column/table. Sync data.
    2.  **Migrate**: Code reads new, writes both.
    3.  **Contract**: Remove old column (propose the exact command; run it only after the human confirms).

### 2. API Versioning
-   **Strategies**: URI Path (`/v1/`), Header (`Accept-Version`), Query Param.
-   **Tolerant Reader**: Clients should ignore unknown fields (Forward Compatibility).

### 3. Feature Flags
-   **Decoupling**: Launch != Deploy.
-   **Kill Switch**: Turn off broken features instantly without rollback.

## Steps
1.  **Never Break Consumers**: If you must break, create a new version (`v2`).
2.  **Dual Write**: During migrations, write to old AND new data structures.
3.  **Deprecation Policy**: Announce sunset dates clearly (e.g., 6 months notice).

## Constraints
- If a change must break consumers, create a new version.
- During migrations write to the old and the new structure.
- Announce sunset dates clearly.

## Output Format
-   `migration-plan.md`: Steps for Expand/Contract.
-   `api-evolution-strategy.md`: Versioning rules.
-   `deprecation-notice.md`: Communication template.

## Limits and safety
- Feature flags are admin controls: name who may change them. If your platform provides access control for the flag service, use it.
- Write migration scripts with parameterised statements or the ORM, and run them first on a copy of the data.
- Do not propose rolling back an expand-contract migration after data was written; propose roll-forward or switching the flag off.
- Deprecated API versions keep receiving security fixes until they are removed.
- A tolerant reader ignores unknown fields, but validation still rejects sensitive ones (`role`, `isAdmin`) where they are not allowed.
- Enabling a legacy or insecure mode (old TLS) needs the human's explicit yes.
