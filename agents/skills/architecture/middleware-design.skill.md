---
name: middleware-design
description: Designing robust middleware chains (Auth, Rate Limiting, Logging).
triggers: [middleware design]
tags: [architecture]
role: eng-backend
---
# middleware-design Skill

## Goal
This skill guides the creation of the request processing pipeline ("The Onion Architecture").

## Steps
## 1. The Standard Pipeline (Order Matters)

1.  **Request ID**: Generate `trace_id` immediately. (Before logs).
2.  **CORS**: Allow/Block origins. (Before processing).
3.  **Body Parser**: JSON/Form parsing. (Limit size to prevent DoS).
4.  **Rate Limiter**: Token Bucket algorithm. (Stop abuse cheaply).
5.  **Authentication**: Verify JWT/Session. (Who is it?).
6.  **Authorization**: Check Roles/Scopes. (Can they do it?).
7.  **Validation**: Zod/Pydantic schema check. (Is input valid?).
8.  **Controller**: Business Logic.
9.  **Error Handler**: Catch exceptions, format JSON, scrub sensitive data.

## 2. Implementation Rules
- **Fail Fast**: If Rate Limit check fails, return 429 immediately. Do not parse body.
- **Context Passing**: Pass `user` and `trace_id` via Context (Go/React) or Request Object (Express/FastAPI).
- **No Business Logic**: Middleware should be generic. Don't query `SELECT * FROM orders` in middleware.

## 3. Specific Patterns

### Rate Limiting
- **Global**: 1000 req/min/IP.
- **Route-Specific**: Login = 5 req/min/IP.
- **Storage**: Use Redis. Local memory rate limiting doesn't work in clustered apps.

### Response Interceptors
- Use for consistent response formatting.
- `data: { ... }`, `meta: { trace_id: ... }`.

### Error Handling Middleware
- **NEVER** return raw stack trace to client in Production.
- **ALWAYS** log raw stack trace to logger.

## Security & Guardrails

### 1. Skill Security (Middleware Design)
- **Bypass via Pipeline Ordering**: The agent is strictly commanded to never deviate from the defined security ordering (e.g., `RateLimiter -> Authentication -> Authorization`). Placing the `BodyParser` or a complex GraphQL execution context *before* the `RateLimiter` or `Authentication` layer allows unauthenticated attackers to exhaust CPU and RAM parsing massive payloads.
- **Error Handler Data Leakage**: The agent must mathematically ensure the final `ErrorHandler` middleware catches all uncaught downstream exceptions. Crucially, the handler must strip raw stack traces, database schema names, SQL syntax errors, and internal IP addresses before formatting the RFC 7807 response for the client in production mode.

### 2. System Integration Security
- **Forged Context Defeat**: The agent must ensure that HTTP headers (like `X-Forwarded-For` or `X-User-Role`) injected by external reverse proxies are aggressively stripped or overwritten by the entry-point middleware if they cannot be cryptographically verified. Trusting spoofed headers allows attackers to gain arbitrary privileges in the `Authorization` middleware.
- **Auth Token Replay and Expiration**: The `Authentication` middleware must not only validate the cryptographic signature of a JWT but also strictly verify the `exp` (expiration) and `nbf` (not before) claims. If the integration utilizes distributed cache invalidation (like logging out), the middleware must also check a high-speed blacklist (e.g., Redis) to prevent the replay of revoked tokens.

### 3. LLM & Agent Guardrails
- **Hallucinated "Catch-All" Security**: The LLM might propose a single, massive middleware function that attempts to handle Auth, Logging, and Rate Limiting simultaneously. The agent must reject this spaghetti design, enforcing the Unix philosophy: distinct, highly-focused middleware focused on exactly one security concern (The Onion Architecture).
- **False Density in Rate Limiting**: If the LLM suggests using basic array structures or local memory (`{}`) for the `RateLimiter` in a Node/Python app, the agent must override this with a distributed storage solution (like Redis). Local memory rate limiting provides a false sense of security in Kubernetes/Load-Balanced environments where traffic is distributed across multiple pods.
