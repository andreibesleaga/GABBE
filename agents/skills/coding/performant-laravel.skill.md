---
name: performant-laravel
description: Strategies for high-performance, scalable Laravel systems (Octane, DB Optimization, Redis, Microservices).
triggers: [laravel, performance, scalability, octane, frankenphp, redis, eloquent, microservices]
tags: [coding, laravel, architecture]
context_cost: medium
---
# Performant Laravel Skill

## Goal
Optimize Laravel applications for high-throughput, sub-100ms response times, and horizontal scalability using modern runtimes and efficient data patterns.

## Capabilities

### 1. Database Performance (Eloquent & Query Builder)
- **Zero N+1 Policy**: Mandatory use of eager loading (`with()`) for all relationships. Use `preventLazyLoading()` in development.
- **Data Selection**: Use `select()` to retrieve only required columns. Never use `*` for large tables.
- **Large Dataset Handling**: Use `chunk()` or `lazy()` for processing large records. Use `cursorPaginate()` for infinite scroll or high-offset pagination.
- **Indexing Strategy**: Ensure all foreign keys and columns used in `WHERE`, `ORDER BY`, and `GROUP BY` are appropriately indexed.

### 2. High-Performance Runtimes
- **Laravel Octane**: Power applications with Swoole or RoadRunner to eliminate the boot overhead of traditional PHP-FPM.
- **FrankenPHP**: Use the modern PHP app server (Go-based) with 103 Early Hints and worker mode support.
- **OPcache & Preloading**: Ensure OPcache is tuned and use PHP 7.4+ preloading to keep the framework in memory.

### 3. Caching & State
- **Granular Caching**: Use the `Cache` facade with Redis/Memcached. Favor `tags()` for complex invalidation.
- **Infrastructure Caching**: Always run `php artisan config:cache`, `route:cache`, and `view:cache` in production deployments.
- **Stateless Design**: Avoid session-based state for APIs; use JWT or Sanctum with token caching.

### 4. Background Processing & Scalability
- **Horizontal Scaling**: Use Laravel Horizon for managing Redis queues with auto-scaling workers.
- **Event-Driven Microservices**: Decouple heavy operations (Image processing, Exports) using queues. Implement the Outbox pattern for reliable cross-service communication.
- **Cloud-Native Integration**: Leverage CDN for static assets and object storage (S3) for file management.

### 5. Architectural Patterns
- **Service Layers**: Extract business logic from controllers into dedicated Services or Actions.
- **Repository Pattern**: Abstract data access for easier testing and optimization.
- **Hexagonal/DDD**: Structure large Laravel apps to separate the domain from infrastructure (Eloquent).

### 6. Observability & Monitoring
- **Laravel Telescope**: Use for local debugging of queries, requests, and entries.
- **APM Integration**: Integrate with New Relic, Datadog, or Blackfire for production bottleneck analysis.
- **Slow Query Logging**: Enable and monitor slow query logs (`DB::listen`).

## Steps
1. **Benchmark Baseline**: Use `k6` or `ab` to get the current Request/Second and p99 latency.
2. **Standardize Autoloading**: Ensure `composer install --optimize-autoloader --no-dev` is used.
3. **Audit Eloquent**: Use Telescope to identify N+1 queries and high memory consumption.
4. **Tune Environment**: Configure Redis for session/cache and ensure OPcache is optimized.

## Deliverables
- `BENCHMARK_REPORT_TEMPLATE.md`: Bottleneck analysis and Octane/FPM load comparisons.
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Definition of cached keys and invalidation logic.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Queue worker strategy and database replica plan.

## Security & Guardrails

### 1. Skill Security
- **Safe Evaluation**: Be cautious with raw SQL (`DB::raw`). Ensure all user inputs are parameterized.
- **Cache Poisoning**: Validate and sanitize data before storing it in the cache to prevent injection.

### 2. System Integration Security
- **Rate Limiting**: Use Laravel's `RateLimiter` to protect APIs from abuse and DoS.
- **Secrets Management**: Never use `env()` outside of config files. Ensure all secrets are pulled from the environment.

### 3. LLM & Agent Guardrails
- **No Premature Octane**: Do not recommend Laravel Octane for simple, low-traffic apps due to the complexity of managing persistent state.
- **Index Balance**: Warn against over-indexing which degrades write performance.
- **Legacy Awareness**: When optimizing older Laravel apps, check compatibility before using modern primitives like `cursorPaginate`.
