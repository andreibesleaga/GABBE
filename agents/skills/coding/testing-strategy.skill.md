---
name: testing-strategy
description: "Choose a testing strategy (pyramid, trophy, contract, property, mutation) and tools for a project, and write a TEST_PLAN.md. Use when planning tests for a new project or feature, deciding how much unit, integration and end-to-end testing to do, or ordering CI test runs."
triggers: [test plan, testing strategy, qa strategy, e2e testing, integration testing, contract testing]
tags: [coding]
core: true
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
**Best for**: React/Next.js apps, UI-heavy frontends. (For microservices, prefer Contract Testing — see below.)
-   **Structure**: Static Analysis (Base) -> Unit -> **Integration (Big)** -> E2E (Top).
-   **Focus**: "Write tests. Not too many. Mostly integration." (Kent C. Dodds).
-   **Rationale**: Integration tests give the most confidence per dollar.

### 3. Contract Testing (Microservices)
**Best for**: Distributed systems where teams work independently.
-   **Focus**: Verifying API contracts between Consumer and Provider.
-   **Tools**: Pact.

## Advanced Tiers (Beyond the Pyramid)

Example-based unit/integration tests only exercise the cases a human thought to write.
The following four tiers attack the gaps — covering input spaces, relations, failure
modes, and the quality of the tests themselves.

-   **Property-Based Testing** (`pbt-strategy.skill`): Instead of asserting on hand-picked examples, declare *properties* (invariants) that must hold for all inputs, then let a generator (Hypothesis, fast-check) throw thousands of randomized cases at the function and **shrink** any counterexample to its minimal form. Best for parsers, serializers, encoders/decoders (round-trip properties), and pure business logic where you can state "for all X, this must be true."
-   **Metamorphic Testing** (`metamorphic-testing.skill`): For systems with no easy oracle (ML models, search ranking, numerical/optimization code, LLM pipelines), you cannot assert the exact output — but you *can* assert **relations between related inputs**. E.g. "translating A→B→A preserves meaning," "adding an irrelevant doc must not change the top result," "scaling all prices by 2x doubles the total." Metamorphic relations turn an unknowable correct answer into a checkable consistency rule.
-   **Chaos / Fault-Injection** (`chaos-fault-injection.skill`): Verify resilience by *deliberately injecting failures* — kill processes, drop network packets, inject latency, exhaust disk/memory, return 500s from dependencies — and assert the system degrades gracefully (circuit breakers trip, retries back off, no data loss). Tests the failure paths that happy-path suites never touch; tools include Toxiproxy, Chaos Mesh, and `pytest`-level dependency stubs that raise on demand.
-   **Mutation Testing** (`mutation-testing.skill`): Measures *test-suite quality* rather than code behavior. A mutation tool (e.g. **mutmut** for Python, Stryker for JS) introduces small faults ("mutants") into the source — flip a `<` to `<=`, swap `+` for `-`, drop a statement — and re-runs the tests. A mutant that survives means no test detected the change, exposing a coverage blind spot. The **mutation score** (killed mutants ÷ total mutants) is a far stronger signal of test effectiveness than line coverage, which the "100% Coverage" Fallacy below warns against.

Tests verify determinism; **evals** score probabilistic quality — see `eval-driven-development.skill`.

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

## Output Format
-   Generate a `TEST_PLAN.md` using `templates/coding/TEST_PLAN_TEMPLATE.md`.
-   Configure CI/CD pipelines to run tests in the correct order (Fastest -> Slowest).

## Constraints
- The plan states for each critical path which test level covers it.
- Coverage percentage is a floor, not the goal: assertion-free tests do not count.

## Limits and safety
- Reject a plan with no integration or end-to-end coverage of the critical paths (login, permissions, payments, data export).
- Mask production data before it enters test environments or hosted test services; ask the human before recommending a service that receives project data.
- Where possible the tests for security-relevant code are written in a separate pass (another persona, prompt or model) from the code they test.
- Tier the CI runs: fast tests on every commit, slow end-to-end tests on pull requests or nightly; state the expected run time.
- Recommend tools the project already uses or that `AGENTS.md` lists; for a new tool check that it is maintained.
- Prefer confidence in critical paths to a coverage percentage.
