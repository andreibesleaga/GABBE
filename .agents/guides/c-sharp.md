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

*This guide will be expanded in future versions.*
