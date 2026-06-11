---
name: arch-patterns
description: Recommends and analyzes system architecture patterns (Microservices, EDA, Serverless, etc.) based on requirements.
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

3.  **Recommend**:
    -   Propose 1-2 patterns.
    -   Justify with "Pros vs Cons" relative to the specific project.
    -   Use `ARCH_DECISION_FRAMEWORK.md` to document the choice.

## Best Practices
-   **Start Simple**: Modular Monolith is often the best default.
-   **Defer Complexity**: Don't use Microservices until you have a specific problem they solve.
-   **Evolutionary Arch**: Design for change. Use "Fitness Functions" to measure architectural drift.

## Security & Guardrails

### 1. Skill Security (Architecture Patterns)
- **Security Pattern Coupling**: The agent must inextricably link security patterns to their corresponding structural patterns. If proposing `Microservices`, it MUST propose `API Gateway + mTLS` for inter-service auth. If proposing `Event-Driven (EDA)`, it MUST propose `Message Signing + Payload Encryption` to prevent Kafka/RabbitMQ spoofing.
- **Serverless Blast Radius**: When recommending `Serverless`, the agent must emphasize that while operational security overhead decreases, the IAM (Identity and Access Management) complexity explodes. Every Lambda/Function must have a surgically precise, least-privilege execution role, strongly advised against in the `arch-patterns` recommendation.

### 2. System Integration Security
- **State-Based vs. Event-Based Threats**: The agent must recognize the differing threat vectors. For *State-Based* (CRUD Monoliths), the primary threat is SQLi/BOLA. For *Event-Based* (Space-Based, CQRS), the primary threats are Replay Attacks, Poison Pill messages, and Eventual Consistency exploits (e.g., double-spending before the read-model updates).
- **Synchronous vs. Asynchronous DoS**: The agent must highlight how the chosen pattern handles Denial of Service. A layered monolith might fall over immediately, while an EDA pattern might gracefully queue the load but exhaust disk space. The recommendation must include the matching resiliency pattern (Circuit Breaker vs. Backpressure).

### 3. LLM & Agent Guardrails
- **Pattern Dogmatism Defense**: The agent must not treat any architectural pattern as a "Silver Bullet." If a user requests a Microservices architecture for a simple 3-page CRUD app, the agent must challenge the decision using cost, complexity, and security surface area as primary arguments.
- **Hallucinated "Secure-by-Default" Claims**: The LLM might falsely claim that a specific pattern (e.g., Serverless) makes the application immune to traditional attacks like XSS or SQLi. The agent must correct this; application-layer vulnerabilities exist entirely independently of the underlying execution architecture.
