# Node.js & Advanced TypeScript Mastery

> **Source Origin**: Distilled from Matteo Collina's expert capabilities (`fastify`, `nodejs-core`, `typescript-magician`, `node`, `oauth`, `linting-neostandard-eslint9`).

This guide enforces the highest tier of architecture, performance, and type-safety standards for Node.js development in the GABBE environment.

---

## 1. Fastify & Architecture Best Practices

Fastify is optimized for speed and low overhead. When working with Fastify:

-   **Encapsulation**: Leverage Fastify's plugin system (`fastify-plugin`) to logically separate routes, decorators, and hooks. Never attach global state tightly.
-   **Schema-First Design**: Always define JSON Schemas (`typebox` or `fluent-json-schema`) for route validation (body, querystring, params, headers) and serialization (response). Fastify compiles these to highly optimized code.
-   **Async/Await Hooks**: Utilize `onRequest`, `preParsing`, `preValidation`, `preHandler`, etc., avoiding legacy callbacks.
-   **Inject Testing**: Test HTTP completely in-memory using `app.inject()`. Never run a live server on a port for unit or integration testing of route handlers.
-   **Logging**: Use `pino` (Fastify's default). Avoid `console.log` in production routines.
-   **Error Handling**: Create centralized custom error handlers (`fastify.setErrorHandler`). Do not leak stack traces in 5xx HTTP responses.

## 2. Node.js Core & Internals

Deep structural knowledge is critical for scaling.

-   **Event Loop Mechanics**: Understand the phases (timers, pending callbacks, idle/prepare, poll, check, close callbacks). Do not block the event loop (avoid `fs.readFileSync` or CPU-heavy sync crypto).
-   **Worker Threads**: Use `worker_threads` for CPU-bound tasks, not for I/O. Use `SharedArrayBuffer` with `Atomics` for high-performance intra-thread communication.
-   **V8 & Memory Management**:
    -   Keep object shapes (hidden classes) stable to enable V8 TurboFan optimizations (Inline Caching).
    -   Avoid memory leaks by managing closures properly and nullifying large unused references.
    -   Use `v8` heap snapshots and `llnode` or Chrome DevTools for native memory analysis.
-   **Native Addons**: When writing C++ addons, always use `N-API` (`node-addon-api`) to achieve ABI stability across Node versions. Mind memory transitions across the JS/C++ boundary.
-   **Streams**: Favor the Pipeline API (`stream/promises`) for backpressure management instead of `.pipe()`.

## 3. TypeScript "Magician" Level (Zero `any`)

TypeScript is a superpower, not a constraint. `any` must be completely eradicated.

-   **No `any`**: If a type is unknown at runtime, use `unknown` and narrow it via type guards (`typeof`, `instanceof`, or custom type predicates like `isMyType(val: unknown): val is MyType`).
-   **Advanced Generics**: Leverage generic constraints (`T extends B`), conditional types (`T extends U ? X : Y`), and `infer` keyword to pull types out of complex structures.
-   **Utility Types**: Master `Awaited<T>`, `Parameters<T>`, `ReturnType<T>`, `Record<K, V>`, `Omit<T, K>`, and `Pick<T, K>`.
-   **Mapped & Template Literal Types**: Use `[K in keyof T]: ...` and `\${string}_\${string}` for stringent state modeling.
-   **Discriminated Unions**: Model states explicitly (e.g., `{ status: 'success', data: Data } | { status: 'error', error: Error }`) rather than optional properties.
-   **Opaque / Brand Types**: Differentiate simple primitives (like IDs) logically at compile time (e.g., `type UserId = string & { readonly __brand: unique symbol }`).

## 4. OAuth & Security Workflow

-   **Strict RFC Compliance**: Strictly implement OAuth 2.0/2.1 flows (PKCE for SPAs/mobile, Client Credentials for machine-to-machine).
-   **Token Handling**: Never store access tokens in `localStorage`. Use secure, `HttpOnly`, `SameSite=Strict` cookies or transient in-memory states.
-   **Validation**: Validate all JWT scopes, audiences (`aud`), and issuers (`iss`) at the API edge natively through Fastify hooks.

## 5. Modern Linting

-   **ESLint v9 + Neostandard**: Utilize Flat Config (`eslint.config.js`).
-   Enforce stylistic guarantees automatically and treat linting issues as build failures (warnings are errors in CI).

---
*For AI Agents: By reading this guide, you are contractually bound under the project CONSTITUTION.md to enforce strict typing (zero any), Fastify schemas, and non-blocking I/O.*
