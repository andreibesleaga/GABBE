# Rust Project Guide

> **Status:** Placeholder / Basic Guide
> **Version:** 1.0

## Recommended Stack (2026)

-   **Runtime:** Rust (Latest Stable)
-   **Build Tool:** Cargo
-   **Web Framework:** Axum or Actix-Web
-   **ORM:** SurrealDB, Diesel, or SeaORM
-   **Testing:** built-in `#[test]`, `testcontainers` for integration
-   **Linting:** `clippy`, `rustfmt`

## Standard Commands

```bash
# Install / Restore
cargo fetch

# Test
cargo test

# Run
cargo run

# Format
cargo fmt

# Lint
cargo clippy
```

## Architecture Patterns

-   **Clean Architecture** is viable but idiomatic Rust often prefers simpler layering.
-   **Features over Layers**: Group code by business feature rather than technical layer if possible.
-   **Error Handling**: Use `Result<T, AppError>` and `thiserror` / `anyhow`.

*This guide will be expanded in future versions.*
