---
name: performant-laravel
description: "Speed up Laravel apps: eager loading and indexes, queues, caching, Octane or FrankenPHP, measured with a load test. Use when a Laravel app has slow pages, N+1 queries or high load."
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

## Output Format
- `BENCHMARK_REPORT_TEMPLATE.md`: Bottleneck analysis and Octane/FPM load comparisons.
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Definition of cached keys and invalidation logic.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Queue worker strategy and database replica plan.

## Constraints
- Measure first (`k6` or `ab` baseline) and record before and after numbers.
- Index only what the queries need: every index slows writes.

## Limits and safety
- Pass user input to `DB::raw`, `whereRaw` and similar only as bindings, never by string interpolation.
- For per-user or per-tenant data, put the user or tenant in the cache key; check data before it goes into the cache.
- Use `env()` only in config files (it returns null outside them once config is cached); rate-limit APIs with `RateLimiter`.
- Recommend Octane only for a measured need: workers keep state between requests, so reset any per-request state.
- A new index on a large table is a migration: propose it and run it only after the human confirms; check the Laravel version before using newer methods such as `cursorPaginate`.
