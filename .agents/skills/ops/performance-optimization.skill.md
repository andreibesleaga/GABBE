---
name: performance-optimization
description: Optimize systems for speed and scale (Caching, Sharding, Async).
context_cost: medium
---
# Performance Optimization Skill

## Triggers
- performance
- optimization
- scaling
- caching
- sharding
- profiling
- latency
- slow

## Purpose
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

## Instructions
1.  **Stop Guessing**: Use a profiler (pprof, Flamegraphs) before optimizing.
2.  **N+1 Problem**: Watch for loops triggering DB queries.
3.  **Database First**: 96% of bottlenecks are in the data layer.

## Deliverables
-   `profiling-report.md`: Analysis of hotspots.
-   `caching-strategy.md`: Redis/Memcached plan.
-   `load-test-plan.md`: k6/JMeter script design.
