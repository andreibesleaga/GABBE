---
name: arch-patterns
description: Shortlist of one or two architecture patterns (modular monolith, microservices, event-driven, serverless, CQRS) with pros and cons for the project. Use when someone asks which architecture style fits the requirements.
triggers: [architecture, system design, scalability, microservices, event-driven, serverless]
tags: [architecture]
context_cost: medium
---
# Architecture Patterns Skill

## Goal
To help the user or agent select the most appropriate system architecture based on improved Non-Functional Requirements (NFRs) like scalability, cost, maintainability, and latency.

## Steps
When designing a system or component:

1.  **Analyze NFRs**: Identify the key constraints.
    -   *High Scalability?* -> Consider Microservices or Space-Based.
    -   *Complex Domain?* -> Consider Domain-Driven Design (DDD) with Modular Monolith.
    -   *Real-time Data?* -> Consider Event-Driven Architecture (EDA).
    -   *variable Workloads?* -> Consider Serverless.

2.  **Evaluate Patterns**:
    -   **Layered (N-Tier)**: Standard for simple web apps. separation of concerns.
    -   **Modular Monolith**: Best starting point for most startups. High cohesion, low deployment complexity.
    -   **Microservices**: For large teams and distinct scaling needs. High operational complexity.
    -   **Event-Driven (EDA)**: For decoupled, reactive systems.
    -   **Space-Based**: For extreme concurrency (in-memory data grids).
    -   **CQRS**: For separate read/write scaling profiles.
    -   **Local-first / offline-first**: see `adaptive-architecture.skill`.

3.  **Recommend**:
    -   Propose 1-2 patterns.
    -   Justify with "Pros vs Cons" relative to the specific project.
    -   Use `ARCH_DECISION_FRAMEWORK.md` to document the choice.

## Best Practices
-   **Start Simple**: Modular Monolith is often the best default.
-   **Defer Complexity**: Don't use Microservices until you have a specific problem they solve.
-   **Evolutionary Arch**: Design for change. Use "Fitness Functions" to measure architectural drift.

## Constraints
- Propose one or two patterns, each with pros and cons for this project.
- A modular monolith is the default unless a stated requirement needs more.

## Output Format
The choice documented with `ARCH_DECISION_FRAMEWORK.md` (`templates/architecture/`).

## Limits and safety
- Pair each pattern with its security and resilience part: microservices with service authentication, event-driven with message authenticity, replay and poison-message handling and backpressure, serverless with a least-privilege role per function.
- Never claim a pattern removes application flaws such as XSS or SQL injection.
- For a small system, challenge a heavy pattern with cost and complexity; if the human insists, record the choice in an ADR.
