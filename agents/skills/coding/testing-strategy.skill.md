---
name: testing-strategy
description: Formulates a comprehensive testing strategy (Pyramid vs Trophy) and selects appropriate tools.
triggers: [test plan, testing strategy, qa strategy, e2e testing, integration testing, contract testing]
tags: [coding]
context_cost: medium
---
# Testing Strategy Skill

## Goal
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

## Steps
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

## Security & Guardrails

### 1. Skill Security (Testing Strategy)
- **Malicious Test De-prioritization**: An attacker might subtly attempt to convince the LLM or developer to abandon the "Testing Trophy" or Contract Testing in favor of an unbalanced, unit-test-only strategy. This intentionally creates systemic blind spots at the integration boundaries, where complex authentication and data-flow vulnerabilities typically reside. The agent must firmly reject any generated `TEST_PLAN.md` that completely omits Integration or E2E coverage for mission-critical paths.
- **Test Environment Data Exfiltration**: When defining the Tool Stack (Step 3), the agent might recommend tools or SaaS platforms (like cloud-based browser testing or visual regression services) without considering data sovereignty. If the E2E tests process actual production data replicas, routing that data through third-party CI environments constitutes a massive data breach. The strategy MUST mandate data sanitization protocols prior to any data entering the testing ecosystem.

### 2. System Integration Security
- **Symmetrical Vulnerability Injection**: If the agent uses the same LLM context to write both the implementation code and the security tests for that code, the LLM will likely suffer from systemic blind spots, writing tests that perfectly mirror the flaws in its implementation. To break this symmetry, the Testing Strategy must advocate for *adversarial test generation*, where a separate agent persona (e.g., `ops-security`), using a different prompt or model, is responsible for writing the vulnerability tests.
- **CI/CD Pipeline DoS**: The agent instructs configuring CI/CD pipelines (Deliverables). If the agent recommends a strategy that triggers thousands of Heavy E2E browser tests on every single micro-commit, it will effectively execute a Denial of Service against the organization's CI infrastructure and drastically increase compute costs. The strategy must enforce strict "Test Tiering" (e.g., running slow E2E tests only on PR merge or nightly, while keeping pre-commit hooks fast).

### 3. LLM & Agent Guardrails
- **Hallucinated Testing Frameworks**: The LLM might recommend a trendy but immature or unmaintained testing framework it saw briefly in its training data (e.g., an obscure Selenium wrapper). The agent must strictly bind its tool recommendations (Step 3) to the "Approved Tool Stack" defined in the project's architectural CONSTITUTION, rejecting hallucinated or out-of-policy libraries.
- **The "100% Coverage" Fallacy**: The LLM might fixate on achieving an artificial metric like "100% Code Coverage" as the primary goal of the strategy. This leads to useless assertion-free tests that just execute code lines to satisfy the coverage crawler, providing a dangerous false sense of security. The strategy prompt must explicitly prioritize "Confidence in Critical Paths" over arbitrary percentage metrics.
