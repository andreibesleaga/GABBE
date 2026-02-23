---
name: enterprise-patterns
description: Implement robust Enterprise Architecture Patterns
triggers: [implement enterprise pattern, add circuit breaker, design saga pattern]
tags: [architecture]
context_cost: medium
---
# enterprise-patterns

## Goal
Implement widespread architectural patterns (BFF, API Gateway, Saga Pattern, Circuit Breaker) for scalable and resilient enterprise operations.


## Steps
1. **Identify Constraint**: Select the pattern that solves the specific distributed computing constraint (e.g., Saga for distributed transactions).
2. **Component Implementation**: Generate the boilerplate (e.g., Spring/Go libraries) for the specific pattern.
3. **Resilience Engineering**: Define retry counts, timeouts, and fallback protocols.
4. **Verification**: Enforce Chaos testing or failure simulation tests before marking the task complete.

## Security & Guardrails

### 1. Skill Security
- **Pattern Bloat**: Prevent the agent from overly engineering simple CRUD apps with unnecessary Sagaservers or Kafka queues.
- **Library Vet**: Force the agent to rely only on enterprise-approved libraries (e.g., Resilience4j) rather than attempting to handwrite complex distributed locks.

### 2. System Integration Security
- **Circuit Breaker Fallbacks**: Ensure that when a circuit breaker trips, the fallback mechanism (cached data, default error) does not accidentally leak sensitive placeholder data to the client.
- **Distributed Logging**: Ensure Saga orchestrators redact PII when logging complex multi-stage rollbacks or compensations.

### 3. LLM & Agent Guardrails
- **Saga Complexity Hallucination**: The LLM must explicitly list all compensatory transactions for every step of a Saga; it cannot gloss over failure states.
- **Anti-Pattern Prevention**: Agents must explicitly block the use of distributed 2-Phase Commits in favor of Saga patterns across loosely coupled services.
