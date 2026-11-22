---
name: enterprise-patterns
description: "Choose and specify an enterprise resilience pattern (saga, circuit breaker, BFF, API gateway) with retries, timeouts, fallbacks and failure tests. Use when a distributed call chain needs a transaction or fault-isolation design."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/enterprise-patterns.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "medium"
---
# enterprise-patterns

## Goal
Implement widespread architectural patterns (BFF, API Gateway, Saga Pattern, Circuit Breaker) for scalable and resilient enterprise operations.

## Steps
1. **Identify Constraint**: Select the pattern that solves the specific distributed computing constraint (e.g., Saga for distributed transactions).
2. **Component Implementation**: Generate the boilerplate (e.g., Spring/Go libraries) for the specific pattern.
3. **Resilience Engineering**: Define retry counts, timeouts, and fallback protocols.
4. **Verification**: Enforce Chaos testing or failure simulation tests before marking the task complete.

## Constraints
- Pick the pattern from the named constraint, not from habit.
- Failure tests pass before the task is done.

## Output Format
The pattern code with its retry, timeout and fallback values, and the failure tests.

## Limits and safety
- Use the platform's maintained resilience library; do not hand-write distributed locks or retry engines.
- List a compensating action for every saga step; no distributed two-phase commit across loosely coupled services.
- A tripped circuit breaker's fallback returns no placeholder or cached data that belongs to another user; saga logs mask personal data.
- Do not add sagas or queues to a plain CRUD app; say which constraint needs the pattern.
