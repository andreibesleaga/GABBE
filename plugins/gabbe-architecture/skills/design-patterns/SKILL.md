---
name: design-patterns
description: "Match a design problem to a standard pattern (strategy, adapter, facade, observer, circuit breaker) and refactor to it. Use when code has long if/else chains, tangled integrations or repeated construction logic."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/design-patterns.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "low"
---
# Design Patterns Skill

## Goal
To improve code maintainability, flexibility, and readability by applying proven solutions to common design problems.

## Supported Patterns (2025 Context)

### Creational
-   **Factory / Builder**: For complex object construction (e.g., configuring LLM clients).
-   **Singleton**: Use sparingly (e.g., for Database connections or Logging service).

### Structural
-   **Adapter**: Connecting legacy code or external APIs (e.g., standardizing different LLM APIs).
-   **Facade**: Simplifying complex subsystems (e.g., a simple `WebScraper` class wrapping Puppeteer).
-   **Composite**: For tree structures (e.g., parsing code ASTs).

### Behavioral
-   **Strategy**: Swappable algorithms (e.g., switching between 'Fast' and 'Smart' search).
-   **Observer**: Event handling (e.g., updating UI when data changes).
-   **State**: Managing complex entity lifecycles (e.g., Order status: Pending -> Paid -> Shipped).

### Modern / Cloud
-   **Circuit Breaker**: Preventing cascading failures in distributed calls.
-   **Sidecar**: Offloading infra concerns (logging, proxying) to a separate process/container.
-   **BFF (Backend for Frontend)**: API layer tailored to specific UIs.

## Steps
1.  **Identify the Problem**: "I have a lot of `if/else` statements for different payment methods."
2.  **Match Pattern**: "This looks like a use case for the **Strategy Pattern**."
3.  **Refactor**:
    -   Define the Interface.
    -   Implement Concrete Strategies.
    -   Inject the Strategy into the Context.
4.  **Document**: Add a comment or use `DESIGN_PATTERN_USAGE.md` if complex.

## Anti-Patterns to Avoid
-   **God Object**: Class that does everything.
-   **Golden Hammer**: Using the same pattern everywhere (e.g., everything is a Singleton).

## Constraints
- Apply a pattern only to a named problem in the code.
- Avoid the Golden Hammer: one pattern everywhere.

## Output Format
The refactored code and, for complex cases, `DESIGN_PATTERN_USAGE.md` (`templates/architecture/`).

## Limits and safety
- A wrapper (adapter, facade, proxy) must keep the authentication and input checks of the call chain it wraps; compare before and after.
- A shared single instance (pool, singleton) has explicit size and timeout limits and is created thread-safely in multi-threaded languages; check against the language documentation.
- If a sidecar or BFF carries a security function, confirm that the backend accepts traffic only from it.
- Events sent to observers carry no secrets or personal data.
- Use the simplest pattern; do not stack patterns for a problem one `if` would solve.
