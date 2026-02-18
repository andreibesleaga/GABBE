# Enterprise Integration Patterns & Modernization

Integrating modern AI/Cloud applications with legacy Enterprise systems (ERP, Mainframe, Monoliths) requires specific patterns to ensure stability, data integrity, and decoupling.

## 1. Modernization Patterns

### Strangler Fig Pattern
**Goal**: Incrementally migrate a legacy system by replacing specific functionality with new services, "strangling" the old system over time.
-   **Method**: Place a facade (API Gateway) in front of the legacy system. Route specific traffic to the new microservice.
-   **Benefit**: Low risk. Immediate value. No "Big Bang" rewrite.

### Anti-Corruption Layer (ACL)
**Goal**: Prevent the legacy system's confusing (or archaic) data model from polluting your clean modern domain model.
-   **Method**: Create a translation layer (Service or Class) that converts Legacy Data Structures <-> Modern Domain Entities.
-   **Rule**: NEVER let a legacy data object leak into your core business logic.

### Change Data Capture (CDC)
**Goal**: React to data changes in a legacy DB without modifying the legacy app.
-   **Method**: Read the database Transaction Log (WAL). Stream changes to Kafka.
-   **Tools**: Debezium.

## 2. Integration Styles

### 1. File Transfer (Batch)
-   **Use case**: Nightly sync with Mainframe/Banking systems.
-   **Pros**: Simple, Decoupled.
-   **Cons**: High latency (data is old).

### 2. Shared Database
-   **Use case**: "Quick and dirty" reporting.
-   **Pros**: Fast.
-   **Cons**: **HIGH RISK**. Strong coupling. Performance contention. **Avoid whenever possible.**

### 3. Remote Procedure Invocation (API)
-   **Use case**: Real-time action (e.g., "Check Inventory").
-   **Pros**: Real-time.
-   **Cons**: Tight coupling (if API is down, you are down). Requires Circuit Breakers.

### 4. Messaging (Event-Driven)
-   **Use case**: State synchronization (e.g., "Order Placed").
-   **Pros**: Decoupled. Resilient. Data is eventual consistent.
-   **Cons**: Complexity.

## 3. Resilience in Integration

### Circuit Breaker
Stop calling a failing system to prevent cascading failure.
-   **Open**: Fast fail (don't call).
-   **Half-Open**: Try one call to see if it's back.
-   **Closed**: Normal operation.

### Bulkhead
Isolate resources (thread pools) so that one slow integration doesn't exhaust the whole system.

### Dead Letter Queue (DLQ)
Where messages go when they cannot be processed after N retries. **Must be monitored.**
