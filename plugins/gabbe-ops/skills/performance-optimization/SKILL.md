---
name: performance-optimization
description: "Choose and apply speed and scale fixes after profiling - caching, read replicas, sharding, indexes, queues, event-driven design. Use when measured latency or load needs a design change, not just a code tweak."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/performance-optimization.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# Performance Optimization Skill

## Goal
To ensure systems behave predictably under load and utilize resources efficiently.

## Capabilities

### 1. Caching Strategy
-   **Cache-Aside**: App reads DB, populates cache. (Best for read-heavy).
-   **Write-Through**: App writes to Cache + DB. (Data consistency).
-   **Edge Caching**: CDN for static assets (Images, JS).

### 2. Database Scaling
-   **Read Replicas**: Offload `SELECT` queries to secondary nodes.
-   **Sharding**: Horizontal partitioning by Key (User ID, Region).
-   **Indexing**: The #1 fix for slow queries.

### 3. Async Architectures
-   **Message Queues**: Decouple heavy work (Sending Emails) from request loop.
-   **Event-Driven**: Services react to changes instead of polling.

## Steps
1.  **Stop Guessing**: Use a profiler (pprof, Flamegraphs) before optimizing; for the measurement procedure and Web Vitals see `performance-audit.skill`, for cache design see `caching-strategy.skill`.
2.  **N+1 Problem**: Watch for loops triggering DB queries.
3.  **Database First**: 99% of bottlenecks are in the data layer.

## Deliverables
-   `profiling-report.md`: Analysis of hotspots.
-   `caching-strategy.md`: Redis/Memcached plan.
-   `load-test-plan.md`: k6/JMeter script design.

## Constraints
- No optimisation without a measured baseline and a target.
- Do not add caching, sharding or replicas to an endpoint whose measured load does not need them.

## Output Format
The files named under Deliverables (`profiling-report.md`, `caching-strategy.md`, `load-test-plan.md`) with measured before and after numbers.

## Limits and safety
- Run profilers against the target process or container only, not the host node.
- Do not cache authentication or authorisation lookups, or give them a very short TTL with a stated reason.
- Queue consumers must handle malformed or oversized messages without crashing; test with one.
- Index changes are proposed with the exact statement and write cost, and run only after the human confirms; "index everything" is refused.
- Do not add caching or sharding for low-traffic endpoints; state the measured threshold used.
