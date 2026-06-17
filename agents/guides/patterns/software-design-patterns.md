# Software Design & Architecture Patterns — Classical Catalog

The foundational (non-agentic) patterns for designing code and systems. These are
what the agent's *generated code* and *system designs* should use; the agentic
patterns in the `agentic-design-patterns` guide sit on top of them. Each entry
notes when to use it and the GABBE skill that implements it.

## How to read this catalog

A pattern names a recurring problem + a proven solution shape. Prefer the simplest
pattern that fits; patterns are a vocabulary, not a checklist to maximize. Reach for
an agentic pattern only where deterministic logic can't express the decision.

---

## (a) Object & code design — Gang of Four (GoF)

Implemented by `design-patterns.skill`. Group by intent:

**Creational** — control object creation, decouple "what" from "how it's made":
- **Factory Method / Abstract Factory** — create families of objects without binding to concrete classes.
- **Builder** — construct complex objects step by step (good for many optional params).
- **Prototype** — clone a configured instance instead of rebuilding.
- **Singleton** — one shared instance (use sparingly; it is global state — prefer dependency injection).

**Structural** — compose objects/classes into larger structures:
- **Adapter** — make an incompatible interface usable. **Bridge** — split abstraction from implementation.
- **Composite** — treat trees of objects uniformly. **Decorator** — add behavior without subclassing.
- **Facade** — a simple front over a complex subsystem. **Flyweight** — share fine-grained objects to save memory. **Proxy** — stand-in controlling access (lazy load, remote, protection).

**Behavioral** — assign responsibilities + communication:
- **Strategy** — swap algorithms behind one interface (removes conditionals).
- **State** — behavior changes with internal state (a clean state machine).
- **Observer** — publish/subscribe within a process. **Command** — encapsulate an action as an object (undo, queues).
- **Template Method** — fixed skeleton, overridable steps. **Iterator**, **Mediator**, **Chain of Responsibility**, **Visitor**, **Memento**, **Interpreter**.
- Smell-to-pattern: many `if/switch` on a type → Strategy/State; tangled producer↔consumer → Observer/Mediator; need undo/replay → Command/Memento.

---

## (b) Architectural patterns (system shape)

- **Layered / n-tier** — responsibilities split into presentation/application/domain/infrastructure layers; the safe default for most line-of-business apps. → `monolith.skill`, `systems-architecture.skill`
- **Modular monolith** — one deployable with strong internal module boundaries; the right default *before* distributing. → `monolith.skill`
- **Microservices** — independently deployable services around business capabilities; adopt for team-scaling/independent-deploy needs, not by default (distribution has real cost). → `microservices.skill`
- **Hexagonal (Ports & Adapters) / Clean / Onion** — domain core isolated from I/O via ports + adapters; framework-independent and highly testable. → `arch-patterns.skill`, `domain-model.skill`
- **Event-driven** — components decouple via events (pub/sub), with **event sourcing** (state as an event log) and **CQRS** (separate read/write models) as variants. → `event-driven-architecture.skill`, `state-management.skill`
- **Pipes & filters / streaming** — stage-by-stage data transformation. → `arch-patterns.skill`
- **Space-based / actor model** — partitioned in-memory state + message passing for elastic scale. → `realtime-comm.skill`, `state-management.skill`
- **Serverless / FaaS** — event-triggered functions, managed scaling. → `cloud-deploy.skill`

---

## (c) Domain-Driven Design (DDD)

Strategic + tactical modeling of complex domains: **bounded contexts**, **context
mapping**, **ubiquitous language**; **aggregates**, **entities**, **value objects**,
**domain events**, **repositories**, **domain services**. Use when the domain (not the
tech) is the hard part. → `domain-model.skill`

---

## (d) Enterprise integration & distributed-systems patterns

- **Saga** — manage a distributed transaction as a sequence of local steps + compensations.
- **Outbox / Inbox** — reliable event publishing alongside a DB write.
- **Circuit Breaker** — stop calling a failing dependency; fail fast and recover.
- **Bulkhead** — isolate resource pools so one failure can't sink the whole system.
- **Retry with backoff + jitter**, **Timeout**, **Rate Limiting**, **Idempotency key**.
- **Strangler Fig** — incrementally replace a legacy system. → `enterprise-migration-scenario.skill`, `legacy-modernization.skill`
- **API Gateway**, **Backend-for-Frontend**, **Sidecar**, **Anti-Corruption Layer**, **Service Mesh**.
- Implemented by `enterprise-patterns.skill`, `error-handling-strategy.skill`, `middleware-design.skill`, `api-design.skill`.

---

## (e) Reliability & resilience patterns

Circuit Breaker, Bulkhead, Timeout, Retry-with-jitter, Rate Limiting, Load Shedding,
Graceful Degradation, Health Check, Backpressure, Redundancy/failover. → `reliability-sre.skill`,
`reliability-engineering.skill`, `error-handling-strategy.skill`

---

## (f) Concurrency & data patterns

- **Concurrency** — producer/consumer, thread pool, future/promise, read-write lock, immutable data, actor. → `performant-*` skills, `state-management.skill`
- **Data** — repository, unit of work, identity map, optimistic/pessimistic locking, sharding, read replicas, CQRS read models, caching (cache-aside/write-through). → `data-engineering.skill`, `sql-optimization.skill`, `caching-strategy.skill`, `db-migration.skill`

---

## Selection cheat-sheet

| Problem | Reach for |
|---|---|
| Too many `if/switch` on a type code | Strategy / State (GoF) |
| Add behavior without touching a class | Decorator / Proxy |
| One deployable, clear modules, ship fast | Modular monolith |
| Independent team deploys / selective scaling | Microservices + API Gateway |
| Domain logic is the hard part, keep it testable | Hexagonal + DDD |
| Decouple producers/consumers, audit history | Event-driven + event sourcing |
| Split heavy reads from writes | CQRS |
| Distributed transaction without 2PC | Saga + Outbox |
| Protect against a failing dependency | Circuit Breaker + Timeout + Retry |
| Replace a legacy system safely | Strangler Fig + Anti-Corruption Layer |

> Honest note: patterns are tools, not goals. Over-applying them (pattern-itis) adds
> accidental complexity. Start simple; introduce a pattern when a real force demands it.
