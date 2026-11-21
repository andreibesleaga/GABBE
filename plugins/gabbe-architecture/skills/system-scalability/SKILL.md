---
name: system-scalability
description: "Scaling audit — bottlenecks, vertical or horizontal options, externalised state, database scaling and a cost note. Use when load is expected to grow or the system is slow under load."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/system-scalability.skill.md"
  tags: "architecture, ops, scale, performance"
  core: "false"
  context_cost: "medium"
---
# system-scalability

## Goal
To audit an existing architecture or propose a new one that appropriately utilizes horizontal and vertical scaling techniques, database sharding/partitioning, and decentralized state management to meet projected performance loads.

## Steps
1. **Current State Analysis**: Evaluate the system's current boundaries (e.g., monolithic database, stateful web servers).
2. **Dimension Scaling**: Determine the optimal approach for the workload:
   - **Vertical Scaling (Scale Up)**: Suggest hardware upgrades (CPU/RAM) where architectural changes are temporally or financially restrictive.
   - **Horizontal Scaling (Scale Out)**: Propose adding more instances via Load Balancers, Kubernetes, or Auto-Scaling Groups. Ensure application state is externalized (e.g., Redis).
3. **Database Scaling**: Propose Read Replicas, Sharding (range vs. hash), Partitioning, or NoSQL migrations for data-heavy bottlenecks.
4. **Documentation**: Output the findings using `agents/templates/architecture/SCALABILITY_ANALYSIS_TEMPLATE.md`.

## Constraints
- Application state is externalised before scaling out.
- Proposals rest on measured or projected load.

## Output Format
`SCALABILITY_ANALYSIS_TEMPLATE.md` (`agents/templates/architecture/`) filled in.

## Limits and safety
- Write scaling manifests (Terraform, Kubernetes) as files; do not apply them to a real cluster. A plan or dry run only on request.
- A sharding key must respect data residency rules (for example EU data in EU shards); confirm the legal requirement with the human.
- Every scale-out proposal carries a cost note.
- Do not propose microservices and queues for small loads without a measured reason.
