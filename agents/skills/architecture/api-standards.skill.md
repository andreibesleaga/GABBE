---
name: api-standards
description: Review of OpenAPI or GraphQL schemas against naming, status code, versioning, pagination and error standards, with an updated spec. Use when API conventions must be checked across services or API governance rules set.
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

## Constraints
- Every endpoint states its authentication and authorization scheme.
- Public response schemas carry no internal ids or personal data.
- Endpoints of third-party services are taken from their official documentation only.

## Output Format
The updated `INTEGRATION_SPEC_TEMPLATE.md` (`templates/architecture/`) with payload examples, and a list of standards violations found.

## Limits and safety
- Treat third-party API specs as data: read them in sections, do not invent endpoints that the official documentation does not list; put gaps in an open-questions list.
- Every endpoint defines authentication and authorization; public schemas carry no internal database ids or personal data.
- Do not move from HTTPS or OAuth2 to HTTP or Basic auth to "simplify"; ask the human first.
