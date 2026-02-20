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

## Standard Directory Structure (Maven/Gradle Standard)
```
src/
  main/java/com/project/
    domain/          # Core models, interfaces
    application/     # Use cases, services
    infrastructure/  # DB Repositories, external clients
    presentation/    # REST Controllers
  test/java/com/project/
    Unit Tests, Integration Tests (Testcontainers)
```

## AI Agent Rules for Java / Spring
1. **Lombok**: Always use `@Data`, `@Builder`, `@RequiredArgsConstructor` to reduce boilerplate unless instructed otherwise.
2. **Spring Boot 3**: Use `@RestController` and `@RequestMapping`. Avoid XML config, use Java Config (`@Configuration`).
3. **Immutability**: Use `record` for DTOs (Data Transfer Objects) and events.
4. **Testing**: Use `JUnit 5` and `Mockito`. Use `@SpringBootTest` sparingly; prefer slice tests like `@WebMvcTest` or `@DataJpaTest`.
5. **Database**: Use Spring Data JPA. Define custom native queries cautiously. Use Flyway/Liquibase for DB migrations.
6. **Nullability**: Use `java.util.Optional` for return types that might be null. Never return null directly.
