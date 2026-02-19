# Java Project Guide

> **Status:** Placeholder / Basic Guide
> **Version:** 1.0

## Recommended Stack (2026)

-   **Runtime:** Java 21+ (LTS)
-   **Build Tool:** Gradle (Kotlin DSL) or Maven
-   **Web Framework:** Spring Boot 3.x or Quarkus
-   **Testing:** JUnit 5 + Mockito + Testcontainers
-   **Linting:** Checkstyle + SpotBugs

## Standard Commands

```bash
# Install / Restore
./gradlew build --refresh-dependencies

# Test
./gradlew test

# Run
./gradlew bootRun

# Format
./gradlew spotlessApply
```

## Architecture Patterns

-   **Hexagonal Architecture** (Ports & Adapters) is recommended for long-lived Java applications.
-   Use **Records** for DTOs and immutable value objects.
-   Prefer **Composition** over Inheritance.

*This guide will be expanded in future versions.*
