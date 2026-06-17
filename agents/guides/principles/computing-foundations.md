# Computing Foundations for Software Engineering

Most engineering decisions that feel like "experience" or "taste" are really computing fundamentals applied
without ceremony. Why a cache helps, why an async design beats threads here but not there, why an API that
chats over the network is slow, why one algorithm scales and another falls over — each traces back to how
computers, operating systems, networks, and language runtimes actually work. This guide maps the core
computer-science topics that the SWEBOK v4 "Computing Foundations" knowledge area treats as essential onto
the engineering decisions they drive. It is a foundations framing reference: it explains *why* the principle
matters and then points you at the execution skill that does the work.

## Computer architecture and the memory hierarchy

Modern hardware is a hierarchy of memories trading speed for size: registers, L1/L2/L3 caches, main memory,
SSD, and network/disk storage, each roughly an order of magnitude slower and larger than the one above it.
CPUs are fast; *waiting for data* is the dominant cost, and access patterns that respect locality (reuse data
that is already close, walk memory sequentially) win.

Engineering decision: this is the physical justification for **caching at every level**. A cache exists to
move hot data up the hierarchy so you pay the fast access cost instead of the slow one — and that is exactly
the territory of `caching-strategy.skill` (what to cache, where, eviction, invalidation). The same principle
explains why cache-friendly data layouts and sequential access show up in the `performant-*` skills
(`performant-python.skill`, `performant-go.skill`, `performant-nodejs.skill`, `performant-php.skill`,
`performant-laravel.skill`, `performant-ai.skill`): contiguous, predictable memory access is often a larger
win than micro-optimizing the code itself.

## Operating systems and concurrency models

The OS multiplexes finite hardware across many tasks: processes (isolated memory) and threads (shared
memory), scheduling, context switches, and the synchronization primitives (locks, semaphores, atomics) that
keep shared state consistent. Concurrency is about *structure* (dealing with many things at once); parallelism
is about *simultaneous execution*. The two big hazards are blocking on I/O and corrupting shared mutable
state.

Engineering decision: this is what governs **realtime and async design**. An event-loop / async model excels
at I/O-bound, high-concurrency workloads because it avoids the cost and contention of one thread per
connection; a thread or process pool fits CPU-bound work that must run truly in parallel. Choosing between
them — and reasoning about backpressure, ordering, and delivery for live connections — is the work of
`realtime-comm.skill`. Understanding context-switch cost, lock contention, and shared-state hazards is also
what keeps the `performant-*` skills from "fixing" a contention problem by adding more threads.

## Computer networks (OSI / TCP-IP)

Networking is layered: the link, internet (IP), transport (TCP/UDP), and application (HTTP and friends)
layers each add their own latency, failure modes, and guarantees. The defining truths are that the network is
*slow* relative to local memory, *unreliable* (packets drop, connections reset), and *unordered* unless a
layer like TCP restores order — and that each round trip costs real time.

Engineering decision: this is the foundation of **API and distributed-system design**. Knowing that every
network hop adds latency and a new failure mode is why chatty APIs (many small round trips) underperform
coarse ones, why batching and pagination exist, and why timeouts, retries with backoff, and idempotency are
not optional in distributed calls — the design side lives in `api-design.skill`. The eight fallacies of
distributed computing ("the network is reliable", "latency is zero", "bandwidth is infinite", and so on) are
the cautionary distillation of this layer.

## Data structures and algorithms

The classic structures (arrays, linked lists, hash tables, trees, heaps, graphs) and algorithm families
(sorting, searching, traversal, dynamic programming) each have characteristic time and space costs. The right
structure makes an operation cheap; the wrong one makes the same operation a bottleneck.

Engineering decision: this is the direct lever on **performance**. Picking a hash map over a linear scan, or
an index over a full table walk, is choosing a better asymptotic class — and reasoning about which growth
rate survives your real input sizes is owned by `time-complexity.skill`, with language-specific application in
the `performant-*` skills. The structures also recur everywhere else: hash tables under caches, trees under
indexes and file systems, graphs under dependency and routing analysis.

## Compilers, interpreters, and runtimes

Between your source and the CPU sits a translation layer: a compiler (ahead-of-time to machine code), an
interpreter, a bytecode VM with a JIT, plus a runtime providing memory management (often garbage collection),
scheduling, and a standard library. These choices shape startup time, steady-state speed, memory behavior,
and the pauses (GC, JIT warm-up) you will observe.

Engineering decision: knowing that a JIT needs warm-up explains misleading cold benchmarks; knowing how a
garbage collector works explains latency spikes and informs allocation-conscious code; knowing that an
interpreter pays per-instruction overhead explains why pushing hot loops into compiled or vectorized paths
helps. This understanding underpins the `performant-*` skills and is also why honest measurement (warm-up
control, steady state) matters — which connects to the measurement discipline rather than guesswork.

## Honest scope note

This is a foundations *framing* reference, not a tutorial in architecture, operating systems, networking,
algorithms, or compilers. Its job is to connect each fundamental to the engineering decision it drives and
then hand you to the skill that executes — `caching-strategy.skill`, `realtime-comm.skill`,
`api-design.skill`, `time-complexity.skill`, and the `performant-*` family. For the underlying theory and
mechanisms in depth, consult dedicated computer-science texts; this guide is here so you reach for the right
execution skill for the right reason.
