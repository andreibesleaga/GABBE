---
name: compatibility-design
description: Manage breaking changes, migrations, and API evolution.
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
    3.  **Contract**: Remove old column.

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

## Deliverables
-   `migration-plan.md`: Steps for Expand/Contract.
-   `api-evolution-strategy.md`: Versioning rules.
-   `deprecation-notice.md`: Communication template.

## Security & Guardrails

### 1. Skill Security (Compatibility Design)
- **Feature Flag Authorization**: The agent must ensure that Feature Flags (Step 3) are treated as highly sensitive administrative controls. Access to the Feature Flag toggling dashboard/API must be protected by strict RBAC and multi-factor authentication, as an attacker could instantly disable critical security protections or unleash untested code by flipping a flag.
- **Migration Script Integrity**: The agent must verify that any code generated for "Expand & Contract" database migrations cannot be used for SQL injection. Migrations are often run with high-privilege database credentials; therefore, the automated scripts must exclusively use parameterized queries or trusted ORM methods, even for structural schema changes.

### 2. System Integration Security
- **Deprecation Sabotage**: When an API version is deprecated (e.g., `v1` replaced by `v2` with better security), attackers will often specifically target the deprecated `v1` endpoint because it might lack the new rate limits or auth checks. The agent must enforce that deprecated endpoints maintain parity with critical security patches until they are completely decommissioned.
- **Tolerant Reader Exploitation**: The "Tolerant Reader" pattern (ignoring unknown fields) can be exploited to smuggle malicious payloads or perform mass assignment attacks. The agent must mandate that while the parser may *ignore* unknown fields for compatibility, the validation layer must *explicitly reject* known sensitive keys (e.g., `isAdmin`, `role`) if they are submitted to inappropriate endpoints.

### 3. LLM & Agent Guardrails
- **Rollback Hallucination**: An LLM might suggest "just rolling back the database" if a migration fails. The agent must actively counter this dangerous advice in production systems, recognizing that rolling back an "Expand & Contract" database migration often causes catastrophic data loss. The agent must always suggest "roll forward" or "feature flag disabling" strategies.
- **Version Pinning Defiance**: A user might ask the agent to "force the API to accept the old, insecure protocol so a legacy client can connect." The agent must refuse to silently downgrade the security posture of the application. It must require explicit human authorization to enable legacy/insecure compatability modes (like TLS 1.0).
