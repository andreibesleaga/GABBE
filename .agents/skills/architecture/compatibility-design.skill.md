---
name: compatibility-design
description: Manage breaking changes, migrations, and API evolution.
context_cost: medium
---
# Compatibility Design Skill

## Triggers
- compatibility
- migration
- versioning
- breaking change
- deprecation
- legacy support
- expand contract

## Purpose
To evolve systems without breaking existing users or downtime.

## Capabilities

### 1. Database Migrations (Zero Downtime)
-   **Expand & Contract Pattern**:
    1.  **Expand**: Add new column/table. Sync data.
    2.  **Migrate**: Code reads new, writes both.
    3.  **Contract**: Remove old column.

### 2. API Versioning
-   **Strategies**: URI Path (`/v1/`), Header (`Accept-Version`), Query Param.
-   **Tolerant Reader**: Clients should ignore unknown fields (Forward Compatibility).

### 3. Feature Flags
-   **Decoupling**: Launch != Deploy.
-   **Kill Switch**: Turn off broken features instantly without rollback.

## Instructions
1.  **Never Break Consumers**: If you must break, create a new version (`v2`).
2.  **Dual Write**: During migrations, write to old AND new data structures.
3.  **Deprecation Policy**: Announce sunset dates clearly (e.g., 6 months notice).

## Deliverables
-   `migration-plan.md`: Steps for Expand/Contract.
-   `api-evolution-strategy.md`: Versioning rules.
-   `deprecation-notice.md`: Communication template.
