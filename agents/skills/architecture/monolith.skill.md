---
name: monolith
description: Module boundaries, dependency rules and architecture checks for a modular monolith. Use when building a monolith that must stay modular, or when module boundaries in an existing one are being violated.
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

## Constraints
- Modules are reached only through their public interfaces.
- Transactions and code do not bypass module boundaries.

## Output Format
The module list with public interfaces, and the architecture linter configuration that enforces the dependency rules.

## Limits and safety
- Do not disable or loosen the architecture linter config to clear a violation; fix the dependency or ask for a waiver.
- Do not invent exceptions to the dependency rules or merge modules into one class to silence errors.
- Partition cache keys and global state by module; each module checks authorization itself.
- Fix one violation at a time, scoped to the two modules involved, with tests passing after each step.
