---
name: error-handling-strategy
description: Centralized error handling (RFC 7807), circuit breakers, and user-facing fallbacks.
role: prod-architect, eng-backend
triggers:
  - error handling
  - exception
  - try catch
  - rfc 7807
  - fallback
  - circuit breaker
---

# error-handling-strategy Skill

Errors are inevitable. Handling them must be consistent, predictable, and safe.

## 1. Unified API Error Format (RFC 7807)
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
