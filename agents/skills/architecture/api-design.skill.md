---
name: api-design
description: API contract (OpenAPI, GraphQL SDL or proto) written before code, with resources, errors, pagination and authentication. Use when a new endpoint or API is needed or the contract of an existing one must change.
triggers: [API, endpoint, REST, GraphQL, OpenAPI, API contract, API design, HTTP endpoint, grpc, soap]
tags: [architecture]
core: true
context_cost: medium
---
# API Design Skill

## Goal
Design and document API contracts before writing implementation code. API-first development ensures consumers (frontend, mobile, third-party) have stable contracts and implementation details don't leak into the interface.

## Steps

1. **Clarify the API requirements**
   - Who are the consumers? (frontend SPA, mobile app, third-party, internal service)
   - Protocol? (REST, GraphQL, gRPC, AsyncAPI)
   - Auth? (JWT, API key, OAuth2, mTLS)
   - Rate limiting & Quotas?

2. **Design the resource model**
   ```yaml
   # Identify resources (nouns, not verbs)
   Resources:
     - /users            -> User resource
     - /orders           -> Order resource

   # Operations
   GET    /users          -> list users (pagination required)
   POST   /users          -> create user (idempotency key required)
   ```

3. **Define request/response schemas**
   - Use explicit schemas — no "any" types.
   - **Versioning**: URI Versioning (`/v1/...`) or Header Versioning (`Accept: application/vnd.app.v1+json`).
   - **Fields**: camelCase for JSON, snake_case for query params (standard choice).

4. **Define error responses (RFC 9457 Problem Details, which obsoletes RFC 7807)**
   ```json
   {
     "type": "https://example.com/probs/out-of-credit",
     "title": "You do not have enough credit.",
     "status": 403,
     "detail": "Your current balance is 30, but that costs 50.",
     "instance": "/account/12345/msgs/abc"
   }
   ```

5. **Write the Spec**
   - **REST**: OpenAPI 3.1 (YAML preferred).
   - **GraphQL**: Schema Definition Language (SDL); see `graphql-schema.skill`.
   - **gRPC**: Protocol Buffers (.proto).

6. **Security considerations**
   - All endpoints require authentication unless explicitly public.
   - **Scopes**: OAuth2 scopes (`read:users`, `write:orders`).
   - Sensitive fields (passwords, PII) never in responses.

7. **Pagination and filtering**
   - **Cursor-based**: `?cursor=xyz` (Preferred for infinite scroll/data export).
   - **Offset-based**: `?page=1` (OK for admin dashboards).

8. **Validate the design**
   - Can all use cases from the PRD be satisfied?
   - **N+1 Check**: Does the client need to make 100 calls to get a list? (If so, use `expand` or GraphQL).

9. **Store and share**
   - Save spec to: `docs/api/`.
   - Lint with Spectral.
   - For standards that apply across many APIs, see `api-standards.skill`.

## Constraints
- **Breaking Changes**: Strictly forbidden without version bump.
- **IDs**: Use UUIDv4 or nanoID (never auto-increment integers externally).
- **Dates**: ISO 8601 UTC always (`2024-01-01T12:00:00Z`).

## Output Format
API Spec file + summary of design decisions.

## Limits and safety
- No `any` or free-form JSON types in the contract: every payload is typed and bounded (maximum sizes and array lengths).
- Every endpoint that takes a resource id documents who may access that id (owner or role); no admin or wildcard scopes.
- Rate limits and the 429 response are in the spec before the design is final.
- Hidden or obscure URLs are not access control: every endpoint has authentication and authorization.
- A GraphQL design carries depth, cost and pagination limits (see `graphql-schema.skill`).
