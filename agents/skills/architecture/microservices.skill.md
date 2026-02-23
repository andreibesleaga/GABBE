---
name: microservices
description: Design and implement microservices architecture
triggers: [design microservices, split monolith, architect distributed system]
tags: [architecture]
context_cost: high
---
# microservices

## Goal
Design, decouple, and orchestrate microservices architectures using bounded contexts, defining clear API contracts and data segregation.


## Steps
1. **Domain boundaries**: Identify bounded contexts using Domain-Driven Design (DDD).
2. **Contract Definition**: Establish rigorous API/gRPC contracts and message schemas for inter-service communication.
3. **Data Segregation**: Assign each service its own dedicated database schema to prevent coupling.
4. **Verification**: Verify that the failure of Service A does not synchronously bring down Service B (circuit breaking).

## Security & Guardrails

### 1. Skill Security
- **Config Sprawl**: Restrict unbounded creation of new service template folders to prevent filesystem exhaustion.
- **Dependency Hell**: Forbid circular dependencies between microservices during the design phase.

### 2. System Integration Security
- **Service-to-Service Auth**: Require mutual TLS (mTLS) or internal JWT validation for all inter-service traffic. No implicit trust boundaries.
- **Data Leakage**: Ensure that aggregated edge-responses do not accidentally expose internal service identifiers or foreign keys.

### 3. LLM & Agent Guardrails
- **Distributed Monolith Hallucination**: Prevent the LLM from designing tightly-coupled synchronous systems masquerading as microservices.
- **Simplification Bias**: The LLM must not omit critical distributed systems concerns (network latency, retries, eventual consistency) from its proposed architecture.
