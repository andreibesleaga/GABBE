# C# / .NET Project Guide

> **Status:** Placeholder / Basic Guide
> **Version:** 1.0

## Recommended Stack (2026)

-   **Runtime:** .NET 10 (LTS)
-   **Build Tool:** dotnet CLI / MSBuild
-   **Web Framework:** ASP.NET Core (Minimal APIs)
-   **ORM:** Entity Framework Core
-   **Testing:** xUnit + FluentAssertions
-   **Linting:** Roslyn Analyzers, editorconfig

## Standard Commands

```bash
# Install / Restore
dotnet restore

# Test
dotnet test

# Run
dotnet run

# Format
dotnet format
```

## Architecture Patterns

-   **Vertical Slice Architecture** is highly recommended for .NET Core applications.
-   **Clean Architecture** is also common but avoid over-abstraction.
-   **MediatR**: Often used to decouple Requests from Handlers.

## Standard Directory Structure
```
src/
  Core/           # Domain Entities, Interfaces
  Application/    # Use cases, MediatR Handlers
  Infrastructure/ # EF Core, External APIs
  Web/            # ASP.NET APIs, Minimal API Endpoints
tests/
  UnitTests/      # xUnit tests with FluentAssertions
  Integration/    # Testcontainers
```

## AI Agent Rules for C# / .NET
1. **Always use Minimal APIs** for new endpoints unless requested otherwise.
2. **Entity Framework Core**: prefer Code-First approach. Use `IEntityTypeConfiguration` for fluent API configuration instead of data annotations.
3. **Dependency Injection**: Always use `IServiceCollection` extension methods per layer (e.g., `AddInfrastructure()`).
4. **Asynchronous Code**: Always use `async/await` down to the data access layer. Append `Async` to method names.
5. **Testing**: Use `xUnit` and `Moq`/`NSubstitute`. Follow AAA (Arrange, Act, Assert) pattern.
6. **Exception Handling**: Use `GlobalExceptionHandler` middleware rather than try-catch blocks in controllers.
