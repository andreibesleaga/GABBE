---
name: access-control
description: Design RBAC/ABAC models, Principle of Least Privilege, Identity Management.
triggers: [access control]
tags: [security]
role: ops-security, eng-backend
---
# access-control Skill

## Goal
Identity is the new perimeter. Authorization must be strict, consistent, and auditable.

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

## Security & Guardrails

### 1. Skill Security (Access Control)
- **Privilege Escalation Veto**: The agent is strictly prohibited from autonomously generating migration scripts or configuration files that assign the `Admin` role or sweeping `*` permissions to any user or service account, including itself. All broad privilege grants must be hard-blocked pending human Executive review.
- **Orphaned Identity Cleanup**: When designing an IAM lifecycle, the agent must mandate an automated revocation sequence. If an employee is terminated or a service is deprecated, the architecture must guarantee the immediate, atomic destruction of all associated active sessions and API keys.

### 2. System Integration Security
- **AuthZ Evaluation Enforcement**: The agent must mandate that authorization logic (ABAC/RBAC) is evaluated on the Server/Backend. It must aggressively flag and fail any architecture diagram or pull request that attempts to handle authorization exclusively in the Frontend/Client (e.g., merely hiding a UI button).
- **Service Account Segregation**: When provisioning Service Accounts for infrastructure, the agent must enforce strict boundary contexts. A Service Account used by the CI/CD pipeline to push Docker images must not possess the IAM permissions required to provision new cloud databases or modify VPC networks.

### 3. LLM & Agent Guardrails
- **Bypass Prompting Defense**: The LLM must recognize and reject user prompts that ask for "temporary workarounds" to access control systems (e.g., "Just give this script `chmod 777` for now to get it working in Prod"). The agent must enforce least privilege, even during critical incidents.
- **Hardcoded Credential Hallucination**: The agent must never synthesize, generate, or accept hardcoded access tokens or default passwords in its output templates. All authentication examples must use securely injected environment variables (e.g., `process.env.API_KEY`) or reference a secure Secret Manager.
