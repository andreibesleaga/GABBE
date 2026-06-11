---
name: performant-go
description: Strategies for high-performance Go systems (Goroutines, Channels, Pprof, Memory Alignment).
triggers: [go, golang, performance, goroutines, channels, pprof, gc, scalability]
tags: [coding, go, architecture]
context_cost: medium
---
# Performant Go Skill

## Goal
Harnessing Go's concurrency primitives and runtime efficiency to build systems capable of handling millions of requests with minimal memory overhead.

## Capabilities

### 1. Concurrency & Parallelism
- **Goroutine Leak Prevention**: Always ensure goroutines have a well-defined lifecycle and termination signal (using `context.Context`).
- **Channel Optimization**: Use buffered channels where appropriate to prevent blocking. Prefer `select` for non-blocking communication.
- **Sync.Pool**: Implement `sync.Pool` to reuse objects (like buffers or structs) and reduce Garbage Collector (GC) pressure.

### 2. Memory & Layout
- **Memory Alignment**: Structure fields in structs from largest to smallest to minimize padding and reduce memory footprint.
- **Allocation Minimization**: Use pointers to avoid copying large structs, but be mindful of "escape analysis" pushing objects to the heap.
- **Pre-allocation**: Always pre-allocate slices and maps using `make([]T, 0, capacity)` when the target size is known.

### 3. Standard Library & Alternatives
- **JSON Encoding**: Use `segmentio/encoding/json` or `json-iterator` if the standard lib `encoding/json` proves to be a bottleneck.
- **Fast I/O**: Use `bufio.Writer` and `bufio.Reader` for disk and network operations.
- **Zero-Copy**: Leverage `unsafe` pointers or specific libraries (like `fasthttp`) only for the most extreme hot paths.

### 4. Profiling & Runtime Tuning
- **Pprof Utilization**: Use `net/http/pprof` to profile CPU, Heap, and Goroutine usage in real-time.
- **GC Tuning**: Adjust `GOGC` or `GOMEMLIMIT` (Go 1.19+) for memory-intensive applications.
- **PGO (Profile-Guided Optimization)**: Collect production profiles and use them during build time (`go build -pgo=...`) for automatic optimizations.

### 5. Architectural Patterns
- **Worker Pools**: Implement worker pool patterns to limit concurrency and prevent resource exhaustion.
- **Streaming**: Process data using `io.Reader` and `io.Writer` interfaces to handle large payloads with constant memory.

## Steps
1. **Baseline Benchmarks**: Write sub-benchmarks using `testing.B` for critical functions.
2. **Heap Audit**: Run `go tool pprof -alloc_objects` to find the biggest allocators.
3. **Escape Analysis**: Run `go build -gcflags="-m"` to see what variables move to the heap.
4. **Identify Contention**: Use the Race Detector (`-race`) and look for Mutex contention in pprof.

## Deliverables
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Visualizations and analysis of CPU/Memory bottlenecks.
- `BENCHMARK_REPORT_TEMPLATE.md`: Results from `go test -bench . -benchmem`.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Strategy for minimizing heap allocations and scaling goroutines.

## Security & Guardrails

### 1. Concurrency Safety
- **Race Conditions**: MUST run tests with the `-race` flag. Never share memory without synchronization (Mutex/Channels).
- **Deadlock Detection**: Ensure no circular dependencies between channels or locks.

### 2. CGO Cautions
- **Overhead**: Be aware that CGO calls are significantly slower than native Go. Avoid calling C code in tight loops.

### 3. Agent Guardrails
- **No Premature Fasthttp**: Do not recommend `fasthttp` over `net/http` unless the standard library is proven insufficient, as `fasthttp` breaks many HTTP features.
- **Simplicity First**: Favor clean, readable Go over "clever" pointer arithmetic or `unsafe` hackery unless absolutely necessary.
