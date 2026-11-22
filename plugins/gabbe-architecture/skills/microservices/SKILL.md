---
name: microservices
description: "Service boundaries, API contracts, data ownership and failure isolation for a microservices design. Use when splitting a monolith or designing a distributed system with several deployable services."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/microservices.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "high"
---
# microservices

## Goal
Design, decouple, and orchestrate microservices architectures using bounded contexts, defining clear API contracts and data segregation.

## Steps
1. **Domain boundaries**: Identify bounded contexts using Domain-Driven Design (DDD).
2. **Contract Definition**: Establish rigorous API/gRPC contracts and message schemas for inter-service communication.
3. **Data Segregation**: Assign each service its own dedicated database schema to prevent coupling.
4. **Verification**: Verify that the failure of Service A does not synchronously bring down Service B (circuit breaking).

## Constraints
- Each service owns its data.
- No circular dependencies between services.

## Output Format
The service boundary list, the API or message contracts, and a table of which service owns which data.

## Limits and safety
- Reject services that share a database, unbounded or circular synchronous call chains, and a synchronous call without a timeout, a retry limit and a circuit breaker: label those a distributed monolith. A bounded synchronous call that has all three is allowed.
- Every service-to-service call is authenticated (mutual TLS or signed internal tokens); no implicit trust inside the network.
- Aggregated edge responses expose no internal ids or foreign keys.
- State network latency, retries and eventual consistency; allow no circular service dependencies.
- Create scaffolds only for services in the approved decomposition.
