# Test Plan: [Project Name]

**Version**: 1.0
**Date**: [YYYY-MM-DD]
**Author**: [Name]

## 1. Introduction
**Scope**: [What is being tested? e.g., "The Checkout Flow and Payment API".]
**Out of Scope**: [What is NOT tested? e.g., "3rd party banking interface".]

## 2. Testing Strategy
**Model**: [Testing Pyramid / Testing Trophy]
**Justification**: [e.g., "We are using the Trophy because this is a UI-heavy React app."]

| Level | Goal | Tools | Coverage Goal |
|---|---|---|---|
| **Static** | Catch typos & type errors | ESLint, TypeScript | 100% (Strict) |
| **Unit** | Verify isolated logic | Vitest | > 96% |
| **Integration** | Verify component interactions | Vitest / Supertest | Critical Paths |
| **Contract** | Verify API consumers | Pact | All Microservices |
| **E2E** | Verify user journeys | Playwright | Smoke Tests Only |

## 3. Test Data Strategy
-   **Unit**: Mocks/Stubs.
-   **Integration**: In-memory DB or Dockerized test DB (seeded).
-   **E2E**: Dedicated staging environment with seeded "Golden Data".

## 4. CI/CD Integration
-   **PR Checks**: Static + Unit + Integration.
-   **Merge to Main**: All of the above + Smoke E2E.
-   **Nightly**: Full Regression E2E.

## 5. Critical User Journeys (Smoke Tests)
1.  [User Login successful]
2.  [User can add item to cart]
3.  [User can complete checkout]
