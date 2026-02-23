---
name: api-standards
description: Enforce REST/GraphQL API design and governance standards
triggers: [design api, review api standards, enforce api governance]
tags: [architecture]
context_cost: medium
---
# api-standards

## Goal
Design, enforce, and validate enterprise API standards (REST, GraphQL, gRPC), ensuring consistent versioning, pagination, and error handling.


## Steps
1. **Analyze Schema**: Review existing OpenAPI/GraphQL schemas.
2. **Apply Standards**: Enforce naming conventions, HTTP status codes, and hypermedia (HATEOAS) links if required.
3. **Verify Governance**: Ensure backwards compatibility via standard versioning rules (e.g., URI versioning or header versioning).
4. **Output**: Generate or update the `INTEGRATION_SPEC_TEMPLATE.md` with explicit payload examples.

## Security & Guardrails

### 1. Skill Security
- **Schema Poisoning**: Validate all external API specs (Swagger/OpenAPI files) against strict parsers before digesting them into context.
- **Resource Exhaustion**: Cap the size of API spec files the agent is allowed to process to prevent out-of-memory crashes.

### 2. System Integration Security
- **Auth Enforcement**: Every designed endpoint *must* explicitly define its Authentication (e.g., JWT) and Authorization (RBAC/ABAC) schemes.
- **Data Exposure**: Prevent the accidental inclusion of internal database IDs or PII fields in public API response schemas.

### 3. LLM & Agent Guardrails
- **Hallucinated Endpoints**: The LLM must not invent API endpoints for third-party services that don't exist in the official documentation.
- **Protocol Downgrade**: If asked to "simplify" security, the LLM must refuse to transition from secure protocols (HTTPS/OAuth2) to insecure ones (HTTP/Basic Auth).
