---
name: system-qualities
description: Define and enforce Quality Attributes (Non-Functional Requirements)
triggers: [define NFRs, analyze system qualities, set SLAs]
tags: [architecture]
context_cost: low
---
# system-qualities

## Goal
Elicit, define, and enforce system Quality Attributes (NFRs) such as performance, scalability, reliability, and security metrics.


## Steps
1. **Elicitation**: Parse the `PRD_TEMPLATE.md` to map business goals to technical NFRs.
2. **Definition**: Use the `QUALITY_ATTRIBUTES_TEMPLATE.md` to specify exact Service Level Indicators (SLIs) and Service Level Objectives (SLOs).
3. **Mapping**: Map these NFRs to architectural decisions (e.g., caching for latency, redundancy for availability).
4. **Verification**: Verify that the chosen architecture patterns theoretically support the required SLOs.

## Security & Guardrails

### 1. Skill Security
- **Metric Overwriting**: Prevent the agent from lowering defined SLOs (e.g., changing 99.9% to 99%) without human rationale and approval.
- **File Integrity**: Ensure the NFR definitions are strictly parsed as markdown tables/lists and do not execute external scripts.

### 2. System Integration Security
- **Security as an NFR**: Security and Compliance must always be defined as tier-1 NFRs. The agent cannot deprioritize them below Performance or Feature Velocity.
- **Audit Logging**: Data retention and immutability must be specified to comply with SOC2/GDPR compliance logging standards.

### 3. LLM & Agent Guardrails
- **Unrealistic Guarantees**: The LLM must not promise 100% availability or zero-latency for distributed networks (violating the CAP theorem).
- **Vague Metrics**: The agent must reject vaguely defined NFRs ("system must be fast") and mandate measurable SLIs ("p99 latency < 100ms").
