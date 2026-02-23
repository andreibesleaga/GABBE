---
name: architecture-governance
description: Automated fitness functions (ArchUnit) to prevent architectural drift.
triggers: [architecture governance]
tags: [architecture]
role: prod-architect
---
# architecture-governance Skill

## Goal
Architecture is not a document; it's a constraint system checked by CI/CD.

## Steps
## 1. Fitness Functions (Automated Tests)
Write tests that verify your architecture, not just your logic.

- **Layering**: "Classes in `Domain` should not depend on `Infrastructure`."
- **Cycles**: "No circular dependencies between slices."
- **Naming**: "All Interfaces should start with `I`" (if that's your rule).
- **Inheritance**: "All Domain Events must implement `IDomainEvent`."

## 2. Tools
- **Java/Kotlin**: ArchUnit.
- **.NET**: NetArchTest.
- **TypeScript**: `dependency-cruiser` or custom ESLint rules (see `agentic-linter`).
- **PHP**: PHPArkitect or Deptrac.

## 3. Examples (Pseudocode)
```typescript
describe('Architecture', () => {
  it('Domain layer should not import Infrastructure', () => {
    const violations = analyzeImports()
      .from('src/domain')
      .to('src/infrastructure');
    expect(violations).toBeEmpty();
  });

  it('All Use Cases should end with UseCase', () => {
    const useCases = classes.in('src/application').thatImplement('IUseCase');
    expect(useCases).toHaveNameEndingWith('UseCase');
  });
});
```

## 4. Governance Policy
- **Breaking the Build**: Architecture violations are treated as compilation errors.
- **Waivers**: If you *must* break a rule, it requires an ADR and a specific `// eslint-disable` comment with the ticket number.

## Security & Guardrails

### 1. Skill Security (Architecture Governance)
- **Governance Rule Tampering**: The agent must verify that the configuration files defining the architecture rules (e.g., `archunit.properties`, `.dependency-cruiser.js`) are protected by CODEOWNERS requiring explicit Security/Architecture team approval for modification. A developer cannot silently disable a security layer check to merge a PR quickly.
- **Fail-Open Veto**: The agent must mandate that all architecture validation tools fail-closed in the CI/CD pipeline. If the `dependency-cruiser` process crashes or fails to download its ruleset, the pipeline must block the deployment.

### 2. System Integration Security
- **Security Boundary Enforcement**: The agent must explicitly define fitness functions for security patterns. For example, "No class in the `Presentation` layer may instantiate a database query directly" or "All classes implementing `IExternalService` must also implement `ICircuitBreaker`."
- **Waiver Auditability**: When developers use `// eslint-disable` or `@SuppressWarnings` (Step 4) to bypass a governance rule, the agent must require a linked, open JIRA/GitHub ticket explicitly documenting the accepted risk. The agent should periodically scan for orphaned waivers (waivers linked to closed or non-existent tickets).

### 3. LLM & Agent Guardrails
- **Automated Rule Dilution**: An LLM might suggest loosening a strict architecture rule (e.g., "Allow the domain to call infrastructure just this once") if a user repeatedly complains about compilation errors. The agent must fiercely defend the established architecture constraints, suggesting code refactoring instead of rule dilution.
- **Hallucinated Syntax/Tools**: When generating custom linting rules or `ArchUnit` queries, the LLM must only output valid, tested syntax for the target tool. It cannot hallucinate non-existent rule types (e.g., `classes().shouldBe().secure()`) that would silently fail to execute, providing a false sense of security.
