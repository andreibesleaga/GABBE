---
name: monolith
description: Design and refactor Monolithic and Modular Monolithic architectures
triggers: [design monolith, build modular monolith, enforce boundaries]
tags: [architecture]
context_cost: medium
---
# monolith

## Goal
Design strictly structured Modular Monoliths or enforce clean boundaries within an existing monolithic codebase.


## Steps
1. **Module Definition**: Identify the core modules and define their public interfaces.
2. **Dependency Rules**: Establish strict visibility and dependency rules between modules (e.g., using ArchUnit or Dependency Cruiser).
3. **Implementation**: Ensure database transactions and code execution do not bypass module boundaries.
4. **Verification**: Run architecture linters to catch dependency violations (e.g., Module A importing internal classes of Module B).

## Security & Guardrails

### 1. Skill Security
- **Governance Evasion**: Prevent the agent from disabling the CI architectural linters (e.g., `dependency-cruiser.json`) in order to resolve boundary violations.
- **God-Class Creation**: Prevent the agent from merging domains into single "God Objects" to avoid compilation errors.

### 2. System Integration Security
- **Shared Memory Poisoning**: If the monolith uses global state or a shared cache, strictly partition keys by module domain.
- **Privilege Escalation**: Ensure all modules enforce authorization explicitly; one module cannot assume another module has pre-authorized a request.

### 3. LLM & Agent Guardrails
- **Boundary Hallucination**: The LLM must not invent exceptions to the dependency rules.
- **Refactor Avalanche**: When fixing a boundary violation, the agent must not initiate a massive, undirected refactoring avalanche across the entire monolithic codebase.
