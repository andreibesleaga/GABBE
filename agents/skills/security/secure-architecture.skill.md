---
name: secure-architecture
description: Architect systems with defense-in-depth and Zero Trust principles
triggers: [design secure system, enforce zero trust, audit architecture security]
tags: [security]
context_cost: high
---
# secure-architecture

## Goal
Enforce robust, defense-in-depth architectural patterns including Zero Trust boundaries, secure access service edge (SASE), network segmentation, and strict IAM.


## Steps
1. **Perimeter Audit**: Assume breach. Establish micro-perimeters around critical logical domains.
2. **Access Policy**: Design the Authorization logic (e.g., using OPA or AWS IAM) ensuring least privilege access across all services.
3. **Data Protection**: Mandate explicit data transit TLS boundaries and rest encryption.
4. **Verification**: Verify that the C4 diagrams explicitly mark trusted vs untrusted zones and the security boundary implementations.

## Security & Guardrails

### 1. Skill Security
- **Config Drift Ban**: The agent must not manually execute cloud IAM changes without outputting them as declarative Infrastructure as Code (e.g., Terraform/CloudFormation) for review.
- **Root Veto**: Explicitly forbid creating or assigning "Admin", "*", or equivalent root-level global actions to any service role inside the generated documentation.

### 2. System Integration Security
- **MFA Enforcement**: Any external/remote access vectors defined in the architecture must explicitly mandate Multi-Factor Authentication.
- **Fail Closed Mechanism**: All network authorization services, if unavailable, must fail-closed (denying access), never fail-open.

### 3. LLM & Agent Guardrails
- **Trust Assumption Bias**: The LLM must not implicitly trust an internal network. Every node must re-validate the identity and authorization of the caller (Zero Trust).
- **Compliance Illusion**: The LLM cannot authorize itself or the architecture as "HIPAA Compliant" or "SOC2 Compliant" because it enforces Zero Trust; formal auditor attestation remains legally required.
