# Comprehensive Testing Strategy Guide (2026)

Testing is not just about "finding bugs" — it's about **confidence at speed**. This guide outlines modern testing strategies for robust applications.

## 1. Core Models: Where to focus?

### The Testing Pyramid (Classic)
**Shape**: Wide base of Unit tests, middle layer of Integration, tiny tip of E2E.
-   **Best for**: Backend monoliths, Libraries, Complex Algorithms.
-   **Why**: Unit tests are millisecond-fast. If your complexity is in the logic, test the logic.

### The Testing Trophy (Modern)
**Shape**: "Static" base, small "Unit" neck, **HUGE "Integration" belly**, small "E2E" head.
-   **Best for**: Frontend apps, Microservices, CRUD apps.
-   **Why**: "Write tests. Not too many. Mostly integration." (Kent C. Dodds).
-   **Logic**: In modern apps, the complexity is often in how components *interact*, not in the components themselves.

## 2. Test Levels Defined

### Level 0: Static Analysis (The Base)
Catch typos and type errors before code runs.
-   **Tools**: TypeScript, ESLint, Prettier.
-   **Cost**: Nearly zero (running in editor).

### Level 1: Unit Testing
Verify a single function/class in isolation.
-   **Mocking**: Heavily mocked dependencies.
-   **Speed**: < 10ms per test.
-   **Goal**: Does `add(1, 2)` return `3`?

### Level 2: Integration Testing
Verify that units work together.
-   **Frontend**: Does clicking the button trigger the form submit handler? (Render the component, but mock the network).
-   **Backend**: Does the API endpoint return 200/400 correctly? (Spin up the server, use an in-memory DB).
-   **Cost**: Medium.

### Level 3: Contract Testing (Microservices)
Verify that Service A can talk to Service B.
-   **Problem**: E2E tests are slow/flaky. Integration tests often mock too much.
-   **Solution**: **Pact**.
    -   *Consumer* defines a contract ("I expect field `user_id`").
    -   *Provider* verifies it honors that contract in its CI.

### Level 4: End-to-End (E2E) Testing
Verify the whole system as a user sees it.
-   **Tools**: Playwright, Cypress.
-   **Environment**: Real browser, real database (or realistic seed), real network.
-   **Cost**: High (Slow, Flaky).
-   **Strategy**: Smoke tests only. Test "Critical User Journeys" (Login, Checkout).

### Level 5: Evaluation-Driven (for agentic / LLM work)
When the system *is* an agent (or uses one), correctness is probabilistic, so the
acceptance bar must be defined **before** the agent is built and must **co-evolve**
with it. This level is a pointer: the **authoritative eval taxonomy** (the Tier-1–Tier-4
Eval Pyramid) lives in [`evaluation-strategy.md`](evaluation-strategy.md); the points
below summarize how it plugs into the test strategy.
-   **Evals before implementation**: write the success criteria / eval set at the spec stage (S01–S02), not after — they are the executable form of the spec (golden thread).
-   **Component-level evals**: evaluate each persona/gate/sub-step on its own, not only end-to-end. One sub-agent's slightly-wrong output becomes the next one's hopelessly-wrong input, so end-to-end checks alone hide where it broke.
-   **Regression evals**: keep a growing fixture set of past failures; re-run on every change (ties to `CONTINUITY.md` and `self-heal`).
-   **Judge/verifier pass**: for high-stakes output, an independent verifier/judge persona scores against the rubric before human sign-off (see `coordination/persona-selector.skill` voting + `core/final-review.skill`).
-   **Metric shift**: measure decision quality, cost-efficiency, and reliability — not lines of code.

## 2b. Beyond Examples: Advanced Testing Techniques (2026)

Example-based unit and integration tests only cover the cases a human imagined. Four
advanced tiers close the remaining gaps and now sit alongside the pyramid/trophy:
-   **Property-Based Testing (PBT)**: declare invariants and let a generator (Hypothesis,
    fast-check) fuzz thousands of inputs and shrink failures to a minimal counterexample —
    ideal for parsers, codecs (round-trips), and pure logic. See `pbt-strategy.skill`.
-   **Metamorphic Testing**: when there is no exact oracle (ML, ranking, LLM pipelines),
    assert *relations between related inputs* instead of absolute outputs. See
    `metamorphic-testing.skill`.
-   **Chaos / Fault-Injection**: deliberately inject failures (latency, dropped packets,
    dependency 500s, killed processes) and assert graceful degradation. See
    `chaos-fault-injection.skill`.
-   **Mutation Testing**: inject small faults into the source (mutmut, Stryker) and measure
    the **mutation score** (killed ÷ total mutants) as a test-quality metric far stronger
    than line coverage.

Crucially, **tests verify determinism; evals score probabilistic quality.** Deterministic
code earns a green/red test; agentic and LLM-driven behavior is graded by evals against a
rubric (see Level 5 above and `eval-driven-development.skill`). Use both — never substitute
a passing test suite for an eval on probabilistic output, or vice versa.

## 3. Visual Regression Testing
For frontend, "code correctness" doesn't mean "visual correctness".
-   **Tools**: Percy, Chromatic, Playwright visual comparisons.
-   **Goal**: Catch CSS regressions (e.g., button turned invisible).

## 4. Test Data Management
-   **Seeding**: Creating a known state before tests run.
-   **Factories**: Using libraries (like `faker`) to generate realistic random data.
-   **Cleanup**: ensuring tests don't leave garbage data that breaks other tests.

## 5. CI/CD Pipeline Strategy
1.  **Commit Hook**: Lint + Type Check.
2.  **Pull Request**: Unit + Integration Tests.
3.  **Merge to Main**: Smoke E2E Tests + Contract Tests.
4.  **Release candidate**: Full Regression Suite.
