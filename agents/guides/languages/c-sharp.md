# C# / .NET Project Guide

> **Audience:** agents writing or reviewing C#/.NET services. **Scope:** current
> stack, idioms, structure, testing, performance, and pitfalls for 2026.
> Versions verified 2026-06-10 (see sources at the end).

## Recommended stack (2026)

- **Runtime:** **.NET 10 (LTS)** — released 2025-11, supported through Nov 2028.
  Target `net10.0`; nullable reference types and implicit usings **on**.
- **Build:** `dotnet` CLI / MSBuild; `Directory.Build.props` for shared settings;
  Central Package Management (`Directory.Packages.props`) for version pinning.
- **Web:** ASP.NET Core **Minimal APIs** for services; MVC/Razor/Blazor where a
  UI or controller surface is warranted.
- **Data:** EF Core (LINQ + migrations) or Dapper for hot paths.
- **Testing:** xUnit + FluentAssertions + NSubstitute/Moq; **Testcontainers** for
  integration; `WebApplicationFactory` for in-process API tests.
- **Quality:** nullable enabled, `TreatWarningsAsErrors`, Roslyn analyzers +
  `dotnet format`; EditorConfig for style.

## Idioms (current C#)

- **Records** and `record struct` for value/DTO types; `required` members +
  primary constructors to enforce construction invariants.
- **Pattern matching** (`switch` expressions, list/property patterns) over
  type-checking chains; `is not null`.
- `async`/`await` end-to-end — never `.Result`/`.Wait()` (deadlocks);
  `CancellationToken` flows through every async boundary; `IAsyncEnumerable<T>`
  for streaming.
- `System.Text.Json` (source-generated `JsonSerializerContext` for AOT/perf).
- Prefer `Span<T>`/`Memory<T>` and pooled buffers on allocation-sensitive paths.

## Project structure (Clean Architecture)

```
src/
  Domain/          entities, value objects, domain events (no dependencies)
  Application/     use-cases, ports/interfaces, validation
  Infrastructure/  EF Core, external clients, implementations of ports
  Api/             Minimal API endpoints, DI composition root
tests/             Unit (fast) + Integration (Testcontainers)
```

Dependencies point inward; the API project is the composition root.

## Performance & ops

- **Native AOT** for fast cold start / small footprint (CLIs, serverless,
  high-density services) — validate trimming and that reflection-heavy libs are
  AOT-compatible.
- Use the built-in DI, `IOptions<T>` for config, `ILogger<T>` structured logging,
  and **OpenTelemetry** (`System.Diagnostics.Activity`) for traces/metrics.
- Health checks via `Microsoft.Extensions.Diagnostics.HealthChecks`.

## Common pitfalls

- Sync-over-async (`.Result`) and missing `ConfigureAwait` in libraries.
- Capturing `DbContext` across threads (it is **not** thread-safe) or leaking it
  beyond a scoped lifetime.
- Ignoring nullable warnings; over-using exceptions for control flow.
- N+1 from lazy loading; forgetting `AsNoTracking()` on read-only queries.

## Sources (verified 2026-06-10)
- What's new in .NET 10: <https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview>
- .NET support policy (LTS = 3 years): <https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core>
- Native AOT: <https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/>
