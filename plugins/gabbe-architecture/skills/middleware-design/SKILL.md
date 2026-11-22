---
name: middleware-design
description: "Request pipeline design with a fixed order — request id, CORS, rate limit, authentication, authorization, parsing, validation, error handler. Use when adding or reviewing middleware for a web API."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/middleware-design.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "low"
---
# middleware-design Skill

## Goal
This skill guides the creation of the request processing pipeline ("The Onion Architecture").

## Steps
## 1. The Standard Pipeline (Order Matters)

1.  **Request ID**: Generate `trace_id` immediately. (Before logs).
2.  **CORS**: Allow/Block origins. (Before processing).
3.  **Rate Limiter**: Token Bucket algorithm. (Stop abuse cheaply).
4.  **Authentication**: Verify JWT/Session. (Who is it?).
5.  **Authorization**: Check Roles/Scopes. (Can they do it?).
6.  **Body Parser**: JSON/Form parsing. (Limit size to prevent DoS; runs only after the checks above).
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

## Constraints
- Middleware stays generic: no business queries.
- Pipeline order is fixed as in section 1.

## Output Format
The middleware order list and the middleware code or configuration for the project's framework.

## Limits and safety
- Rate limiting, authentication and authorization run before the body is parsed.
- The final error handler catches everything and strips stack traces, SQL errors and internal addresses.
- Strip or overwrite forwarded headers (`X-Forwarded-For`, `X-User-Role`) from outside unless a trusted proxy sets them.
- Authentication checks expiry and not-before claims, and the revocation list where logout or revocation exists.
- One concern per middleware; with more than one instance, keep rate-limit counters in shared storage, not process memory.
