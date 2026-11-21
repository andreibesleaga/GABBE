---
name: performant-go
description: "Profile and speed up Go services: goroutine lifecycle, allocations, struct layout, pprof, GC settings, benchmarks. Use when a Go service is slow, uses too much memory, leaks goroutines or needs a benchmark."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/performant-go.skill.md"
  tags: "coding, go, architecture"
  core: "false"
  context_cost: "medium"
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

## Output Format
- `ARCHITECTURE_REVIEW_TEMPLATE.md`: Visualizations and analysis of CPU/Memory bottlenecks.
- `BENCHMARK_REPORT_TEMPLATE.md`: Results from `go test -bench . -benchmem`.
- `SCALABILITY_ANALYSIS_TEMPLATE.md`: Strategy for minimizing heap allocations and scaling goroutines.

## Constraints
- Every goroutine has a termination signal (`context.Context`).
- Prefer clear Go over pointer tricks; optimise only what a benchmark or profile shows.

## Limits and safety
- Run the tests with `-race` after any change to concurrent code; a reported race is a failure.
- Expose `net/http/pprof` only on a local or authenticated admin port, never on the public listener.
- Reset a pooled object before it goes back into `sync.Pool`, so data from one request cannot reach another.
- Use `unsafe`, cgo, `fasthttp` or a replacement JSON library only when a benchmark shows the standard library is the bottleneck; keep the benchmark.
