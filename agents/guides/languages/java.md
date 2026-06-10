# Java Project Guide

> **Audience:** agents writing or reviewing Java services. **Scope:** current
> stack, idioms, structure, testing, performance, and pitfalls for server-side
> Java in 2026. Versions verified 2026-06-10 (see sources at the end).

## Recommended stack (2026)

- **Runtime:** **Java 25 (LTS)** — released 2025-09-16; the current long-term
  support release. Java 21 (LTS) remains widely deployed; target 25 for new
  work, 21 as the minimum floor. (Java 26 is the latest non-LTS feature release.)
- **Build:** Gradle (Kotlin DSL) for new projects; Maven where the org standard.
- **Web:** Spring Boot 3.x (broadest ecosystem) or Quarkus / Helidon (fast
  startup, low memory, GraalVM-friendly).
- **Persistence:** Spring Data JPA / Hibernate; jOOQ when you want type-safe SQL.
- **Testing:** JUnit 5 + AssertJ + Mockito; **Testcontainers** for real
  databases/brokers in integration tests.
- **Quality:** Checkstyle + SpotBugs (or Error Prone) + `./gradlew check`; format
  with Spotless (google-java-format / Palantir).

## Concurrency — use the modern model

- **Virtual threads** (finalized in Java 21, JEP 444): for I/O-bound work, run
  each task on a virtual thread instead of pooling platform threads. With Spring
  Boot, enable `spring.threads.virtual.enabled=true`; otherwise use
  `Executors.newVirtualThreadPerTaskExecutor()`. Write straightforward blocking
  code — the runtime unmounts the carrier thread on blocking I/O.
- **Structured concurrency** (`StructuredTaskScope`) and **scoped values**
  continue to mature across 21→25; prefer them over `ThreadLocal` and ad-hoc
  fan-out for request-scoped concurrency and propagation.
- Do **not** pool virtual threads, and avoid pinning them inside `synchronized`
  blocks that perform blocking I/O — use `ReentrantLock` there.

## Language idioms (21–25)

- **Records** for immutable data carriers; **sealed** interfaces + **pattern
  matching for `switch`** (incl. record deconstruction) for closed type
  hierarchies and exhaustive handling.
- Prefer immutability and `Optional` over nulls at API boundaries; never use
  `Optional` for fields or method parameters.
- Use enhanced `switch` expressions and text blocks for readability.

## Project structure

```
src/main/java/<group>/<app>/    domain · application · infrastructure · api   (Clean/Hexagonal)
src/main/resources/             application.yml, db/migration (Flyway/Liquibase)
src/test/java/                   unit (fast) + integration (Testcontainers)
build.gradle.kts | pom.xml
```

Keep the domain free of framework annotations; depend inward (the dependency rule).

## Performance & ops

- Start with the G1 GC; consider ZGC/Shenandoah for low-pause, large-heap
  services. Set explicit `-Xmx` / container memory limits.
- Prefer **CDS / AppCDS** and, for fast cold start, **GraalVM Native Image**
  (Spring AOT / Quarkus) — but verify reflection config and run the native test
  suite.
- Observe with Micrometer → OpenTelemetry; expose health/readiness via Actuator.

## Common pitfalls

- Blocking inside a reactive (`WebFlux`) pipeline — pick one model per service.
- N+1 queries from lazy JPA associations — fetch-join or use projections.
- Catch-and-swallow exceptions; leaking checked exceptions across layers.
- Mutable static state; non-thread-safe `SimpleDateFormat` (use `java.time`).

## Sources (verified 2026-06-10)
- Java version history & LTS cadence: <https://en.wikipedia.org/wiki/Java_version_history>
- JDK 25 (LTS) features: <https://openjdk.org/projects/jdk/25/> · <https://www.infoq.com/news/2025/09/java25-released/>
- Virtual threads (JEP 444): <https://openjdk.org/jeps/444>
