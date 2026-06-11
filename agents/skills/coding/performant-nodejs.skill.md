---
name: performant-nodejs
description: Strategies for high-performance, scalable Node.js systems (Worker Threads, ESM, Observability, Clean Architecture).
triggers: [nodejs, performance, scalability, worker threads, clustering, esm, observability, hexagonal architecture]
tags: [coding, nodejs, architecture]
context_cost: medium
---
# Performant Node.js Skill

## Goal
Build and maintain high-throughput, low-latency, and horizontally scalable Node.js systems using modern primitives and architectural patterns.

## Capabilities

### 1. Concurrency & Parallelism
- **Clustering**: Scale vertically by spawning a process per CPU core using the `cluster` module.
- **Worker Threads**: Offload CPU-intensive tasks (encryption, compression, heavy logic) to separate threads using `worker_threads` to avoid blocking the Event Loop.
- **Event Loop Management**: Prevent starvation by avoiding long-running synchronous operations and heavy JSON parsing on the main thread.

### 2. Modern Standards & Async
- **ES Modules (ESM)**: Favor ESM for new projects for better tree-shaking, top-level await, and future-proofing.
- **AsyncLocalStorage**: Use for context propagation (trace IDs, user sessions) across asynchronous boundaries without manual passing.
- **Concurrency Control**: Use libraries like `p-limit` or custom semaphores to prevent resource exhaustion when calling external APIs or databases.

### 3. High-Performance Streams
- **Backpressure Handling**: Efficiently stream large files or data sets using `stream.pipeline` to manage memory usage.
- **HTTP Streaming**: Implement streaming responses for real-time data processing and low TTFB (Time To First Byte).

### 4. Observability & Monitoring
- **Structured Logging**: Use `pino` for low-overhead, JSON-based logging.
- **GC Insight**: Monitor Garbage Collection pauses and memory leaks using `v8` and `inspector` modules.
- **Distributed Tracing**: Implement OpenTelemetry for cross-service visibility.

### 5. Architectural Patterns
- **Hexagonal Architecture (Ports & Adapters)**: Decouple business logic from external dependencies (DB, APIs) for better testability and evolution.
- **CQRS (Command Query Responsibility Segregation)**: Separate read and write models for performance optimization.
- **Outbox/Saga Patterns**: Ensure eventual consistency in distributed systems without distributed transactions.

### 6. Security & Hardening
- **Helmet**: Use for setting secure HTTP headers (CSP, HSTS, etc.).
- **Input Validation**: Mandatory use of `zod` or `ajv` for schema-first validation.
- **Graceful Shutdown**: Properly handle `SIGTERM` and `SIGINT` to close DB connections and finish in-flight requests.

## Steps
1. **Profile First**: Use `node --inspect` or `0x` to generate flamegraphs before any optimization.
2. **Standardize**: Ensure ESM is used and dependencies are audited using `npm audit`.
3. **Analyze Concurrency**: Determine if the bottleneck is CPU-bound (needs Workers) or I/O-bound (needs better async flow/caching).
4. **Implement Observability**: Add structured logs and basic metrics as the first step of any performance task.

## Deliverables
- `BENCHMARK_REPORT_TEMPLATE.md`: Flamegraph analysis and latency baseline.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Strategy for clustering, sharding, or worker usage.
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Standardized logging, tracing configuration, and architecture review.

## Security & Guardrails

### 1. Skill Security
- **Worker Isolation**: Do not pass sensitive objects (like raw DB connections or secrets) directly to workers if they run untrusted code.
- **Stream Injection**: Validate input before piping to file systems or external sinks to prevent injection attacks.

### 2. System Integration Security
- **Rate Limiting**: Always implement at the gateway or app level to prevent DoS when scaling.
- **Schema-First**: Never trust raw JSON; always validate against a strict schema (e.g., Zod).

### 3. LLM & Agent Guardrails
- **Avoid Micro-optimizations**: Refuse to optimize code that isn't on the critical path or hasn't been profiled as a bottleneck.
- **Clustering awareness**: Remind the user that `cluster` and `worker_threads` change state management (no shared memory in clusters).
