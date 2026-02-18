# Enterprise API Standards & Governance

Consistent APIs are the backbone of a scalable enterprise. This guide defines the standards for all internal and external APIs.

## 1. API Architecture Styles

| Style | Use Case | Pros | Cons |
|---|---|---|---|
| **REST** | General purpose, Public APIs | Standard, Cacheable, Simple | Over-fetching, N+1 issues |
| **GraphQL** | Frontend-Heavy, Complex Graphs | Flexible queries, Single round-trip | Complexity, Caching hard |
| **gRPC** | Internal Microservices | High perf, Type-safe | Human-unreadable, Browser support |
| **AsyncAPI** | Event-Driven / Webhooks | Models events explicitly | Newer tooling ecosystem |

## 2. Resource Naming (REST)
-   **Plural Nouns**: `/users`, `/orders`.
-   **Kebab-case URLs**: `/product-categories` (NOT `/productCategories`).
-   **Nesting**: limit to 2 levels. `/users/123/orders` (Good). `/users/123/orders/456/items/789` (Bad -> flatten to `/orders/456/items`).

## 3. Versioning Strategy
**Rule**: Making a breaking change? You MUST introduce a new version.

### Methods
1.  **URI Versioning** (Standard): `GET /v1/users`
    -   *Pros*: Explicit, Easy to debug/cache.
    -   *Cons*: "Pollutes" URI.
2.  **Header Versioning**: `Accept: application/vnd.company.v1+json`
    -   *Pros*: Clean URI. Implementation hiding.
    -   *Cons*: Harder to test in browser.

## 4. Standard Response Envelope
Consistency allows shared client libraries.

### Success
```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}
```

### Error (RFC 7807)
```json
{
  "error": {
    "code": "resource_not_found",
    "message": "User 123 not found",
    "traceId": "abc-123"
  }
}
```

## 5. Security & Governance
-   **Authentication**: Bearer Token (JWT) in Header.
-   **Rate Limiting**: Return `429 Too Many Requests` with `Retry-After` header.
-   **Idempotency**: `POST` requests should accept `Idempotency-Key` header to prevent double-billing on network retry.
-   **Documentation**: OpenAPI 3.0+ required for ALL APIs.

## 6. Deprecation Policy
1.  Mark endpoint `Deprecated: true` in OpenAPI.
2.  Add `Warning: 299 - "Deprecated API"` header.
3.  Sunset period: Minimum 6 months for internal, 12 months for public APIs.
