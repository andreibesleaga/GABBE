---
name: performant-nodejs
description: "Speed up Node.js services: profile first, then worker threads, streams with backpressure, ESM, structured logging and tracing. Use when a Node.js service is slow, blocks the event loop or uses too much memory."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/performant-nodejs.skill.md"
  tags: "coding, nodejs, architecture"
  core: "false"
  context_cost: "medium"
---
# Performant Node.js Skill

## Goal
Build and maintain high-throughput, low-latency, and horizontally scalable Node.js systems using modern primitives and architectural patterns.

## Capabilities

### 1. Concurrency & Parallelism
- **Clustering**: Scale vertically by spawning a process per CPU core using the `cluster` module.
- **Worker Threads**: Offload CPU-intensive tasks (encryption, compression, heavy logic) to separate threads using `worker_threads` to avoid blocking the Event Loop.
- **Event Loop Management**: Prevent starvation by avoiding long-running synchronous operations and heavy JSON parsing on the main thread (for Node.js internals and Fastify see `nodejs-expert.skill`).

### 2. Modern Standards & Async
- **ES Modules (ESM)**: Favor ESM for new projects for better tree-shaking, top-level await, and future-proofing.
- **AsyncLocalStorage**: Use for context propagation (trace IDs, user sessions) across asynchronous boundaries without manual passing.
- **Concurrency Control**: Use libraries like `p-limit` or custom semaphores to prevent resource exhaustion when calling external APIs or databases.

### 3. High-Performance Streams
- **Backpressure Handling**: Efficiently stream large files or data sets using `stream.pipeline` to manage memory usage (see `file-processing.skill` for uploads and large files).
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

## Output Format
- `BENCHMARK_REPORT_TEMPLATE.md`: Flamegraph analysis and latency baseline.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Strategy for clustering, sharding, or worker usage.
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Standardized logging, tracing configuration, and architecture review.

## Constraints
- Profile first (`node --inspect` or `0x`); do not optimise code that is not shown to be a bottleneck.
- Never trust raw JSON; validate against a strict schema.

## Limits and safety
- Do not pass secrets or raw database connections to worker threads that run untrusted code.
- Validate input against a schema (`zod` or `ajv`) before piping it into the file system or any external sink.
- Rate-limit at the gateway or app level when scaling out.
- `cluster` processes and worker threads do not share memory: move in-process state (caches, sessions, rate-limit counters) to a shared store first.
