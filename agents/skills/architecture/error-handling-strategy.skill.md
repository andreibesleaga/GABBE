---
name: error-handling-strategy
description: Centralized error handling (RFC 7807), circuit breakers, and user-facing fallbacks.
triggers: [error handling strategy]
tags: [architecture]
role: prod-architect, eng-backend
---
# error-handling-strategy Skill

## Goal
Errors are inevitable. Handling them must be consistent, predictable, and safe.

## Steps
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

## Security & Guardrails

### 1. Skill Security (Error Handling)
- **Stack Trace Suppression Guarantee**: The agent must irrevocably mandate that under no circumstances—not even during `beta` or early deployment phases—will raw stack traces, SQL syntax errors, or server environment variables be returned in HTTP 500 responses. This prevents critical Information Disclosure vulnerabilities.
- **Trace ID Obfuscation**: While `traceId` (RFC 7807) is critical for debugging, the agent must ensure the generated ID does not inadvertently leak internal system state (like sequential database IDs, IP addresses, or readable timestamps). It must mandate the use of opaque UUIDv4 or cryptographic hashes for public-facing tracing identifiers.

### 2. System Integration Security
- **Fail-Closed by Default**: When an unexpected `DomainException` or `SecurityException` occurs, the Global Exception Handler must inherently default to a restrictive posture (401/403 or a generic 500). It must never "fail-open" by ignoring the error and proceeding with the execution flow or granting unverified access.
- **Circuit Breaker Poisoning Defense**: If a Circuit Breaker is triggered by a sudden spike in errors (often indicative of a DDoS attack or an intentional exploit attempt against a specific service), the system must degrade gracefully (Step 4) without completely locking out valid, authenticated traffic to unaffected areas.

### 3. LLM & Agent Guardrails
- **Excessive Error Verbosity Hallucination**: An overly helpful LLM might suggest returning "user-friendly" error messages that inadvertently leak business logic (e.g., "User account exists but is locked due to 5 failed password attempts"). The agent must rigidly enforce the OWASP standard for generic authentication errors (e.g., "Invalid username or password").
- **Retry Amplification Attack Mitigation**: The agent must not suggest naive Retry logic without strict bounds. If an LLM proposes "retry failed requests up to 10 times," the agent must intervene, enforcing Exponential Backoff and Jitter. Unbounded retries turn a transient internal network issue into a self-inflicted, devastating Denial of Service.
