---
name: performance-optimization
description: Optimize systems for speed and scale (Caching, Sharding, Async).
triggers: [performance, optimization, scaling, caching, sharding, profiling, latency, slow]
tags: [ops]
context_cost: medium
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
1.  **Stop Guessing**: Use a profiler (pprof, Flamegraphs) before optimizing.
2.  **N+1 Problem**: Watch for loops triggering DB queries.
3.  **Database First**: 99% of bottlenecks are in the data layer.

## Deliverables
-   `profiling-report.md`: Analysis of hotspots.
-   `caching-strategy.md`: Redis/Memcached plan.
-   `load-test-plan.md`: k6/JMeter script design.

## Security & Guardrails

### 1. Skill Security (Performance Optimization)
- **Safe Profiler Execution**: Profiling tools executed by the agent must be strictly isolated to the target container or process. The agent must not have root access on the host node, preventing an attacker from using a profiling tool to dump the memory of adjacent applications.
- **Optimization Artifact Integrity**: The generated `profiling-report.md` must be cryptographically signed by the auditing agent to prevent unauthorized parties from tampering with the reported hotspots to mislead the engineering team.

### 2. System Integration Security
- **Stale Auth Data Prevention**: When implementing Cache-Aside or Write-Through caching strategies, the agent must guarantee that authentication and authorization lookups (e.g., permission checks, session validation) are either NOT cached, or use incredibly short, verifiable TTLs to prevent privilege escalation.
- **Queue Poisoning Defense**: When decoupling heavy work using Message Queues (e.g., Kafka, RabbitMQ), the optimizing agent must design the queue consumers to gracefully handle "Poison Pills" (malformed or excessively large messages) without crashing, avoiding a Denial of Service attack vector.

### 3. LLM & Agent Guardrails
- **Premature Optimization Trap**: The LLM must be equipped with a generic threshold (e.g., "p99 latency < 100ms is acceptable"). It must actively refuse user prompts to over-engineer caching or sharding for low-traffic endpoints, avoiding unnecessary architectural complexity and security surface area.
- **Index Hijacking Warning**: If asked to "just index everything to make it fast," the agent must warn that excessive indexing drastically slows down `INSERT`/`UPDATE` operations and consumes massive disk space, which can be weaponized in a disk-exhaustion DoS attack.
