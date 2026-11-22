---
name: error-handling-strategy
description: Design of one error model for a service — RFC 9457 problem details, global handler, retries with jitter, circuit breakers and fallbacks. Use when error responses are inconsistent or one dependency takes the service down.
triggers: [error handling strategy, problem details, rfc 9457, global exception handler, circuit breaker, retry with backoff]
tags: [architecture]
role: prod-architect, eng-backend
context_cost: low
---
# error-handling-strategy Skill

## Goal
Errors are inevitable. Handling them must be consistent, predictable, and safe.

## Steps
## 1. Unified API Error Format (RFC 9457, which obsoletes RFC 7807)
Never return raw stack traces or ad-hoc JSON strings. Use `Problem Details`:

```json
{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "status": 403,
  "detail": "Current balance is 30, but cost is 50.",
  "instance": "/account/12345/msgs/abc",
  "traceId": "00-5c14d5-..."
}
```

## 2. Centralized Exception Handling
- **Do Not**: Catch exceptions in every controller method.
- **Do**: Use a Global Exception Handler (Middleware / Filter).
  - Map `DomainException` → 422 Unprocessable Entity.
  - Map `NotFoundException` → 404 Not Found.
  - Map `SecurityException` → 401/403.
  - Map `CatchAll` → 500 Internal Server Error (and log trace ID).

## 3. Resilience Patterns
- **Circuit Breaker**: Detect cascading failures. If 50% of requests to Service B fail, open the circuit (fail fast) for 30s.
- **Bulkhead**: Thread pool isolation. Service A crashing shouldn't take down Service B.
- **Retry**: Only retry *transient* errors (Network, 503). Never retry 4xx errors. Backoff: Exponential + Jitter.

## 4. User-Facing Fallbacks
- **Graceful Degradation**: If the "Recommendations" service is down, don't crash the homepage. Show "Popular Items" (static) instead.
- **Friendly Messages**: "Something went wrong" is bad. "We couldn't load your cart, but your items are safe. Try refreshing." is better.

## Constraints
- Never return raw stack traces or ad-hoc JSON error strings.
- Retry only transient errors, never 4xx.

## Output Format
A short design note in the project's architecture docs (`docs/architecture/` by default) with the error format, the exception-to-status mapping, the resilience settings and the fallbacks.

## Limits and safety
- Production responses never carry stack traces, SQL errors or environment values, at any stage; log them with the trace id instead.
- Trace ids are opaque random values: no sequential ids, addresses or readable timestamps.
- Unexpected errors fail closed: 401, 403 or a generic 500, never continue as if nothing happened.
- Authentication errors stay generic ("invalid username or password"); no hints about account state.
- Retries are bounded, with backoff and jitter; an open circuit breaker must not lock out routes it does not protect.
