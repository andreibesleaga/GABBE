---
name: enterprise-migration-scenario
description: Plan and execute complex enterprise-scale legacy migrations
triggers: [plan enterprise migration, migrate legacy to microservices, architect system migration]
tags: [architecture]
context_cost: high
---
# enterprise-migration-scenario

## Goal
Design and execute large-scale migrations from legacy systems (mainframe/on-prem) to modern, cloud-native architectures without dropping traffic or data.


## Steps
1. **Audit Legacy**: Parse existing legacy docs using `architecture/LEGACY_AUDIT_TEMPLATE.md`.
2. **Select Pattern**: Choose migration strategies like Strangler Fig, Anti-Corruption Layer (ACL), or CDC (Change Data Capture).
3. **Execution Plan**: Output a phased `core/PLAN.md` with incremental rollout checkpoints.
4. **Verification**: Verify backward-compatibility testing (parallel runs) and automated rollback plans are explicitly documented.

## Security & Guardrails

### 1. Skill Security
- **Irreversible Actions**: The agent must NEVER output commands that drop or truncate legacy databases. Migrations must strictly be additive/shadow writes until final approval.
- **Migration Script Generation**: Enforce strict input sanitization on any LLM-generated SQL or scripting intended for migration execution.

### 2. System Integration Security
- **Data In-Flight**: Assure all synchronization between legacy and new systems runs over encrypted tunnels, even within perceived "safe" corporate boundaries.
- **Anti-Corruption Layer Hardening**: Implement strict type-checking at the ACL boundary to prevent legacy structural malformations from poisoning the new domains.

### 3. LLM & Agent Guardrails
- **Big-Bang Fallacy**: The LLM might hallucinate that an entire enterprise system can be migrated synchronously over a weekend. Agents must reject Big-Bang migrations and mandate phased, Strangler Fig rollouts.
- **Knowledge Overreach**: Prevent the LLM from making assumptions about proprietary legacy behaviors (like custom Mainframe DB architectures) without explicit user documentation.
