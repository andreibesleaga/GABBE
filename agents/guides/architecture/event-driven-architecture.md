# Event-Driven Architecture (EDA) Guide

A dominant pattern for 2025 systems requiring high scalability and decoupling.

## 1. Core Concept
Components communicate by emitting **events** (facts that happened) rather than sending **commands** (requests to do something).
-   **Command**: "Create Order" (Expects response, tight coupling).
-   **Event**: "Order Created" (Fire and forget, loose coupling).

## 2. Key Components
-   **Producer**: Emits events (e.g., Checkout Service).
-   **Broker**: Transports events (e.g., Kafka, RabbitMQ, SNS/SQS).
-   **Consumer**: Reacts to events (e.g., Shipping Service, Inventory Service).

## 3. Patterns

### Event Notification
-   Producer sends a minimal event: `{"order_id": 123, "event": "created"}`.
-   Consumer calls back updates state: `GET /orders/123`.
-   **Pros**: Low payload size.
-   **Cons**: Chatty (callback required).

### Event-Carried State Transfer
-   Producer sends full state: `{"order_id": 123, "items": [...], "customer": ...}`.
-   Consumer updates its own local cache/DB.
-   **Pros**: Decoupled (no callback needed), high resilience.
-   **Cons**: Data replication/consistency challenges.

### Event Sourcing
-   Store the *events* as the source of truth, not the current state.
-   The current state is derived by replaying events.
-   **Pros**: Perfect audit trail, temporal queries, easy debugging.
-   **Cons**: High complexity, snapshots required for performance.

## 4. Best Practices
-   **Idempotency**: Consumers must handle receiving the same event twice safely.
-   **Schema Registry**: Rigidly define event schemas (Avro, Protobuf, JSON Schema) to prevent breaking consumers.
-   **Dead Letter Queues (DLQ)**: Where failed events go to die (and be analyzed).
-   **Async First**: EDA is asynchronous. Don't try to force synchronous request-response flow over messaging.
