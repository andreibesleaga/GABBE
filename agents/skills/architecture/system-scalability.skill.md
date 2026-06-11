---
name: system-scalability
description: Audit and architect scaling boundaries and bottlenecks
triggers: [scale up, scale out, horizontal scalability, vertical scaling, load balancing, analyze scalability]
tags: [architecture, ops, scale, performance]
context_cost: medium
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

## Security & Guardrails

### 1. Skill Security
- **No Direct Infrastructure Muting**: The agent must output Terraform/Kubernetes manifests for scaling but **cannot** execute apply operations directly against production clusters.

### 2. System Integration Security
- **Data Locality in Sharding**: When suggesting database sharding, the agent must verify that the sharding key respects any regional data privacy laws (e.g., EU data stays in EU shards).

### 3. LLM & Agent Guardrails
- **Anti-Overengineering**: Prevent the LLM from suggesting hyper-complex architectures (e.g., microservices + Kafka) for workloads under 100 requests per minute.
- **Cost Awareness**: Any horizontal scaling proposal must include a FinOps warning about exponential cost increases if unmonitored.
