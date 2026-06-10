# Rust Project Guide

> **Audience:** agents writing or reviewing Rust services/tools. **Scope:**
> current edition, idioms, structure, testing, performance, and pitfalls for
> 2026. Versions verified 2026-06-10 (see sources at the end).

## Recommended stack (2026)

- **Toolchain:** latest stable Rust on **edition 2024** (stabilized in Rust
  1.85.0, 2025-02-20). Set `edition = "2024"` in `Cargo.toml`. Pin with
  `rust-toolchain.toml`.
- **Async runtime:** **Tokio** (de-facto standard) — multi-threaded scheduler,
  timers, I/O, sync primitives.
- **Web:** **Axum** (Tower-based, ergonomic) or Actix-Web (max throughput).
- **Data:** **SQLx** (async, compile-time-checked SQL) or SeaORM/Diesel for an
  ORM. `serde` + `serde_json` for serialization.
- **Errors:** `thiserror` for library error enums; `anyhow` for application-level
  error context. Avoid `unwrap()`/`expect()` outside tests and provably-infallible spots.
- **Testing:** built-in `#[test]` + `assert_*`; `tokio::test` for async;
  `proptest` for property tests; `criterion` for benchmarks; `testcontainers` for
  integration.
- **Quality:** `cargo clippy -- -D warnings`, `cargo fmt`, `cargo deny` (license/
  advisory), and `cargo audit` for the RustSec advisory DB.

## Idioms (edition 2024)

- **Ownership & borrowing** drive the design: prefer owned data at boundaries,
  borrow for reads; reach for `Arc`/`Mutex` only when shared mutable state is
  unavoidable. Favor message passing (`tokio::mpsc`) over shared locks.
- Model domain states with `enum`s and exhaustive `match`; use the newtype
  pattern for type-safe identifiers.
- `Result<T, E>` + the `?` operator for fallible flows; convert errors with
  `From`/`thiserror`. Use `Option` combinators (`map`, `and_then`, `ok_or`).
- **Async closures** (`async || {}`) are stable as of edition 2024 — use them for
  combinator-style async code.
- `unsafe` only behind a safe, documented abstraction with an explicit invariant
  comment; edition 2024 requires `unsafe extern` blocks and `unsafe` attributes.

## Project structure

```
Cargo.toml          [workspace] for multi-crate; edition = "2024"
src/
  main.rs | lib.rs  binary vs library crate root
  domain/           pure types + logic (no I/O)
  infra/            db, http clients, adapters
  api/              axum routers/handlers
tests/              integration tests (separate crate)
benches/            criterion benchmarks
```

Split a workspace into a `lib` crate (testable core) + thin `bin` crate.

## Performance & ops

- Build with `--release`; tune `[profile.release]` (`lto = "thin"`,
  `codegen-units = 1`, `panic = "abort"` for smallest/fastest binaries).
- Profile before optimizing (`cargo flamegraph`, `perf`); avoid premature
  `clone()`; prefer borrowing and `&str`/`&[T]` in hot paths.
- Observe with `tracing` + `tracing-opentelemetry`; structured spans over `println!`.

## Common pitfalls

- Fighting the borrow checker by sprinkling `clone()`/`Arc<Mutex<…>>` — usually a
  design smell; restructure ownership instead.
- Blocking calls inside async tasks — use `tokio::task::spawn_blocking`.
- `.unwrap()` in library/production code; panics across FFI boundaries.
- Holding a `MutexGuard` across an `.await` (can deadlock) — drop it first.

## Sources (verified 2026-06-10)
- Rust 1.85.0 + 2024 edition announcement: <https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/>
- Rust 2024 edition guide: <https://doc.rust-lang.org/edition-guide/rust-2024/index.html>
- RustSec advisory DB (`cargo audit`): <https://rustsec.org/>
