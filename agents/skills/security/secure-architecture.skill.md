---
name: secure-architecture
description: "Design defence in depth: trust zones, least-privilege access policy and encryption boundaries. Use at S02 when drawing the architecture of a system that handles untrusted input, personal data or money."
triggers: [design secure system, enforce zero trust, audit architecture security, defence in depth, trust zones]
tags: [security]
context_cost: high
---
# secure-architecture

## Goal
Enforce robust, defense-in-depth architectural patterns including Zero Trust boundaries, secure access service edge (SASE), network segmentation, and strict IAM.

## Where it fits
Phase and gate: S02. Evidence: trust zones and boundaries marked on the C4 diagram, and the matching rows in `docs/security/THREAT_MODEL.md`. Guide: `guides/security/secure-architecture.md`.

## Steps
1. **Perimeter Audit**: Assume breach. Establish micro-perimeters around critical logical domains.
2. **Access Policy**: Design the Authorization logic (e.g., using OPA or AWS IAM) ensuring least privilege access across all services.
3. **Data Protection**: Mandate explicit data transit TLS boundaries and rest encryption.
4. **Verification**: Verify that the C4 diagrams explicitly mark trusted vs untrusted zones and the security boundary implementations.

## Constraints
- Every cross-zone flow has an authentication and an encryption decision.
- Trust zones in the diagram match the threat model.

## Output Format
The C4 diagram with trust zones marked, the access policy proposal, and the data protection decisions.

## Limits and safety
- Mark every trust zone and boundary on the C4 diagram. An unmarked boundary is a review finding.
- Policy examples (OPA, IAM) are proposals. Applying policy to live infrastructure needs the human's yes.
- A diagram alone does not show zero trust or any certification. Say what was checked.
