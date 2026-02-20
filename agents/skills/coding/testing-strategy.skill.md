---
name: testing-strategy
description: Formulates a comprehensive testing strategy (Pyramid vs Trophy) and selects appropriate tools.
context_cost: medium
---
# Testing Strategy Skill

## Triggers
- test plan
- testing strategy
- qa strategy
- e2e testing
- integration testing
- contract testing

## Purpose
To help the user or agent define *what* to test, *how* to test it, and *where* to focus effort based on the project architecture.

## Strategies

### 1. The Testing Pyramid (Classic)
**Best for**: Monoliths, Backend-heavy apps.
-   **Structure**: 70% Unit, 20% Integration, 10% E2E.
-   **Focus**: Fast feedback loop at the unit level.
-   **Tools**: Jest/Vitest (Unit), Supertest (Int), Playwright (E2E).

### 2. The Testing Trophy (Modern / Frontend-heavy)
**Best for**: React/Next.js apps, Microservices.
-   **Structure**: Static Analysis (Base) -> Unit -> **Integration (Big)** -> E2E (Top).
-   **Focus**: "Write tests. Not too many. Mostly integration." (Kent C. Dodds).
-   **Rationale**: Integration tests give the most confidence per dollar.

### 3. Contract Testing (Microservices)
**Best for**: Distributed systems where teams work independently.
-   **Focus**: Verifying API contracts between Consumer and Provider.
-   **Tools**: Pact.

## Instructions
1.  **Analyze Project**:
    -   Is it a monolith or microservices?
    -   Is it UI-heavy or API-heavy?
2.  **Select Strategy**:
    -   *UI-Heavy* -> Recommend **Testing Trophy** (Focus on component integration tests).
    -   *Complex Business Logic* -> Recommend **Pyramid** (Heavy unit testing).
    -   *Microservices* -> Add **Contract Testing**.
3.  **Define Tool Stack**:
    -   **Unit/Int**: Vitest (JS/TS), Pytest (Python), PHPUnit (PHP).
    -   **E2E**: Playwright (Recommended) or Cypress.
    -   **Visual**: Percy, Chromatic.

## deliverables
-   Generate a `TEST_PLAN.md` using `templates/coding/TEST_PLAN_TEMPLATE.md`.
-   Configure CI/CD pipelines to run tests in the correct order (Fastest -> Slowest).
