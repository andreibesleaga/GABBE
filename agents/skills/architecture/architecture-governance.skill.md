---
name: architecture-governance
description: Enforce layer and dependency rules as architecture tests in CI (ArchUnit, dependency-cruiser, Deptrac). Use when a layering rule keeps being broken or a pipeline needs an architecture gate.
triggers: [architecture governance, archunit, dependency rules, layer violations, architecture tests in ci]
tags: [architecture]
role: prod-architect
context_cost: low
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
- For measurable thresholds and CI wiring beyond layering, see `fitness-functions.skill`.

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

## Constraints
- Architecture violations break the build.
- A waiver needs an ADR and a ticket number.

## Output Format
Architecture test files and the rule configuration of the chosen tool, plus an ADR for each waiver.

## Limits and safety
- Rule files (`archunit` config, `.dependency-cruiser.*`) change only with the human's approval. If your platform provides CODEOWNERS or branch protection, use it to require review of them.
- The CI check fails closed: if the tool crashes or its rules do not load, the job fails.
- Do not loosen a rule to make a build pass; fix the code or propose a waiver with an ADR.
- Every waiver names an open ticket; scan for waivers whose ticket is closed.
- Check each generated rule against the tool's documentation and run it on a known violation to see it fail.
