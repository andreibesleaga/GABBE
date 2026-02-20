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

## Standard Directory Structure
```
Cargo.toml
src/
  main.rs         # Setup, Axum Router
  lib.rs          # Module exposure
  error.rs        # Centralized AppError
  domain/         # Core data structures
  handlers/       # Axum route handlers
  db/             # Database access / repositories
tests/
  integration_test.rs
```

## AI Agent Rules for Rust
1. **Error Handling**: Implement `IntoResponse` for your custom `AppError` type to automatically translate `Result<T, AppError>` into HTTP responses.
2. **Axum**: Use Axum's `State` extractor for passing around DB connection pools and configuration.
3. **Cloning vs References**: Default to passing references (`&T`). Only `clone()` when strictly necessary for ownership, like moving into `tokio::spawn`.
4. **Macros**: Avoid writing custom `macro_rules!` unless solving a problem that features or generics cannot.
5. **Testing**: Prefer `rust core` testing for logic. Use `testcontainers-rs` to spin up a Postgres instance for repository integration tests.
6. **Linting**: No PR should fail `cargo clippy -- -D warnings`. Ensure all structs are properly documented via `///`.
