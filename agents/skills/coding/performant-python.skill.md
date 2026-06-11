---
name: performant-python
description: Strategies for high-performance Python systems (FastAPI, Asyncio, UVloop, Memory Optimization).
triggers: [python, fastapi, performance, asyncio, uvloop, pydantic, scalability, profiling]
tags: [coding, python, architecture]
context_cost: medium
---
# Performant Python Skill

## Goal
Building high-concurrency, low-latency Python services by leveraging asynchronous patterns, optimized runtimes, and efficient memory management.

## Capabilities

### 1. Asynchronous Mastery (Asyncio & FastAPI)
- **Non-blocking I/O**: Use `async`/`await` for all network and disk I/O. Use `run_in_executor` for CPU-bound tasks to avoid blocking the event loop.
- **Event Loop Tuning**: Use `uvloop` as the drop-in replacement for the default asyncio loop for significant speedups.
- **Concurrent Execution**: Use `asyncio.gather()` or `asyncio.TaskGroup` (Python 3.11+) for parallel I/O operations.

### 2. Database & Data Handling
- **Async Drivers**: Use `asyncpg` for PostgreSQL or `aiomysql`. Use SQLAlchemy/Tortoise with async support.
- **Serialization**: Use `ORJSONResponse` or `UJSONResponse` in FastAPI for faster JSON encoding/decoding.
- **Efficient Models**: Use Pydantic v2 for its Rust-based speed. Use `.model_dump(include={...})` to minimize data transfer.

### 3. Memory & Resource Optimization
- **Slot Classes**: Use `__slots__` in frequently instantiated classes to reduce memory footprint and increase attribute access speed.
- **Generator Patterns**: Use `generators` and `yield` for processing large datasets to keep memory usage constant (O(1)).
- **Garbage Collection**: Tune `gc` thresholds if necessary, but prioritize object reuse to minimize pressure.

### 4. Deployment & Performance Runtimes
- **Process Management**: Use Gunicorn with `UvicornWorker` to scale across CPU cores.
- **Connection Pooling**: Always implement pooling for DB and HTTP clients (e.g., `httpx` instead of `requests`).
- **Middleware Overhead**: Audit and minimize middleware; each layer adds latency to every request.

### 5. Profiling & Monitoring
- **Deterministic Profiling**: Use `cProfile` for code path analysis.
- **Sampling Profiling**: Use `Py-Spy` or `Scalene` for production-safe, low-overhead profiling.
- **APM**: Integrate with Prometheus/Grafana or Datadog for real-time latency and throughput tracking.

## Steps
1. **Identify Blockers**: Use `Py-Spy` to find the hot paths in a running process.
2. **Async Audit**: Ensure no synchronous libraries (like `requests` or standard `psycopg2`) are used in an async context.
3. **Pydantic Check**: Upgrade to V2 and optimize model validation constraints.
4. **Benchmark**: Use `Locust` or `k6` to verify speed improvements under load.

## Deliverables
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Analysis of blocking calls and memory architecture.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Roadmap for converting sync logic to async.
- `BENCHMARK_REPORT_TEMPLATE.md`: Response time comparisons (Before/After load testing).

## Security & Guardrails

### 1. Async Hazards
- **Race Conditions**: Be cautious with shared state (globals) in async contexts; use `asyncio.Lock` where necessary.
- **Loop Blocking**: Never run `time.sleep()` or heavy math in the main thread of an async app.

### 2. Data Security
- **Parameterization**: Ensure all DB queries are parameterized, especially when using raw SQL via async drivers.

### 3. Agent Guardrails
- **No Over-optimization**: Don't use `cython` or `numba` unless the pure Python/FastAPI path is fully optimized and still proves insufficient.
- **Versioning**: Ensure compatibility with Python 3.9+ for modern async features.
