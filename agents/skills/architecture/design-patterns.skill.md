---
name: design-patterns
description: Identifies, implements, and refactors code using standard Design Patterns (GoF + Modern).
triggers: [design pattern, refactor pattern, strategy pattern, observer pattern, factory pattern, singleton]
tags: [architecture]
context_cost: low
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

## Security & Guardrails

### 1. Skill Security (Design Patterns)
- **Pattern Implementation Integrity**: When the agent generates code for complex patterns like `Facade` or `Adapter`, it must not inadvertently bypass existing security checks. For example, if an `Adapter` wraps an older API, the agent must ensure it does not accidentally strip out authentication headers or input sanitization routines present in the original call chain.
- **Singleton State Exhaustion**: If the agent implements a `Singleton` for a shared resource (like a DB connection pool), it must explicitly define maximum bounds and timeout values. An unbound Singleton can be exploited to cause a Denial of Service (DoS) by exhausting memory or connections globally across the application.

### 2. System Integration Security
- **Proxy/Sidecar Bypass**: When the architecture uses a `Sidecar` or `BFF` for security concerns (like TLS termination or global rate limiting), the agent must physically or logically isolate the backend service so it ONLY accepts traffic from the Sidecar/BFF. Any network configuration allowing a direct request to the backend service bypasses the security pattern entirely.
- **Observer Data Leakage**: In the `Observer` pattern, state changes are broadcast to all subscribed listeners. The agent must verify that sensitive data (e.g., unhashed passwords, PII) is scrubbed from the event payload *before* it is broadcast, ensuring that an arbitrary internal listener cannot silently capture regulated data.

### 3. LLM & Agent Guardrails
- **Complexity-Driven Vulnerabilities**: The LLM might propose an overly convoluted combination of `Strategy`, `Factory`, and `Decorator` patterns to solve a simple problem. This extreme abstraction (the "Lasagna Architecture") makes it nearly impossible for human reviewers to trace the execution flow and identify authorization bugs. The agent must prioritize the "Keep It Simple, Stupid" (KISS) principle for security-critical pathways.
- **Hallucinated Thread-Safety**: The agent must definitively know the concurrency model of the target language. If the agent generates a `Singleton` in a multi-threaded language (like Java or Go), it is strictly forbidden from generating naive, thread-unsafe initializations which could lead to race conditions and unpredictable authorization state.
