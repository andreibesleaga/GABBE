---
name: api-security
description: Audit and harden REST or GraphQL endpoints against broken object-level authorisation, weak authentication and resource abuse. Use when adding or reviewing an API, tokens or rate limits.
triggers: [secure api, audit api security, implement jwt auth, api security, bola, idor, rate limiting]
tags: [security]
context_cost: medium
---
# api-security

## Goal
Ensure APIs are fortified against common vulnerabilities like BOLA/IDOR, broken authentication, rate limiting bypasses, and massive assignment.

## Where it fits
Phase and gate: S03 (auth and validation contracts in the spec), S05, S07. Evidence: a list of endpoints with the auth rule for each, and tests that an unauthorised call is rejected. Guide: `guides/security/api-security.md`.

## Steps
1. **Audit Endpoints**: Scan all exposed controllers and routers.
2. **Check the OWASP API Security Top 10, 2023 edition** (api-security.owasp.org, checked 2026-11-21): API1 Broken Object Level Authorization, API2 Broken Authentication, API3 Broken Object Property Level Authorization, API4 Unrestricted Resource Consumption, API5 Broken Function Level Authorization, API6 Unrestricted Access to Sensitive Business Flows, API7 Server Side Request Forgery, API8 Security Misconfiguration, API9 Improper Inventory Management, API10 Unsafe Consumption of APIs. Write PASS, FAIL or N/A with evidence for each.
3. **Patch Implementation**: Implement specific guards (e.g., strict payload parsing, scoped JWTs, role-based decorators).
4. **Verification**: Write tests (or run a DAST scan against a test environment) that show an unauthorised call is rejected. Done when each endpoint in the list has one.
5. **Output**: the endpoint list with its auth rule and test, in `docs/security/API_REVIEW.md`.

## Constraints
- Every endpoint has an auth rule and a test.
- Inputs are parsed against a schema; unknown fields are rejected.

## Output Format
`docs/security/API_REVIEW.md` and the tests.

## Limits and safety
- Dynamic scans send read requests only, unless the target is an ephemeral test environment. No mutating requests against shared or production systems.
- Do not print a key you find. Write the type, file and line.
- Do not write custom token signing or hashing; use the framework's or a maintained library.
- A possible BOLA or IDOR finding stays open until the human has reviewed the authorisation logic.
