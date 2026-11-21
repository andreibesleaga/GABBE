---
name: access-control
description: Design roles and permissions with least privilege and review authorisation checks. Use when adding roles, permissions or admin features, or when auditing who can access what.
triggers: [access control, rbac, abac, permissions, least privilege, roles and permissions]
tags: [security]
role: ops-security, eng-backend
context_cost: low
---
# access-control Skill

## Goal
Identity is the new perimeter. Authorization must be strict, consistent, and auditable.

## Where it fits
Phase and gate: S02 (authorisation design), S03 (permission contract in the spec), S07 (review). Evidence: the role and permission table in `docs/security/THREAT_MODEL.md` or `SPEC.md`, and tests that an unauthorised call is rejected. Part of `security-baseline.skill.md`.

## Steps
## 1. Models
- **RBAC (Role-Based)**: `Admin`, `Editor`, `Viewer`. Simple, coarse-grained.
- **ABAC (Attribute-Based)**: `CanEdit if user.dept == doc.dept AND time < 5pm`. Flexible, complex.
- **ReBAC (Relationship-Based)**: `CanView if user is friend_of document.owner`. (Graph-based, e.g., Zanzibar).

## 2. Best Practices
- **Least Privilege**: Start with `Deny All`. Explicitly `Allow` specific actions.
- **Decoupling**: Decouple logic (`if user.isAdmin`) from policy (`can(user, 'delete:report')`). Use libraries like CASL or Oso.
- **No Hardcoded IDs**: Never checks `if (user.id === '123')`.

## 3. Infrastructure IAM
- **Service Accounts**: Separate identity for apps/machines. Rotate keys automatically.
- **Short-Lived Credentials**: Use OIDC/STS (AssumeRole) instead of long-lived access keys.

## 4. Audit
- **Log Decisions**: "User X tried to do Action Y on Resource Z -> Result: DENIED".
- **Review**: Quarterly review of `Admin` group membership.

## Constraints
- Default is deny; each allow is explicit and written in the permission table.
- Authorisation logic lives in one place, not scattered in handlers.

## Output Format
A role and permission table, the decision-logging rule, and the list of service accounts with their scopes.

## Limits and safety
- Do not write migrations or config that give `Admin` or `*` permissions to any user or service account; propose them and wait for the human.
- Authorisation is checked on the server. A pull request that only hides a UI element fails the review.
- A CI service account gets no right to create databases or change networks.
- Examples use environment variables or a secret manager, never a literal token or default password.
- When asked for a temporary wide permission, propose the narrow one and note the request in `AUDIT_LOG.md`.
