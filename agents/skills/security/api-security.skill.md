---
name: api-security
description: Design and enforce REST/GraphQL API Security paradigms
triggers: [secure api, audit api security, implement jwt auth]
tags: [security]
context_cost: medium
---
# api-security

## Goal
Ensure APIs are fortified against common vulnerabilities like BOLA/IDOR, broken authentication, rate limiting bypasses, and massive assignment.


## Steps
1. **Audit Endpoints**: Scan all exposed controllers and routers.
2. **Enforce OWASP API Top 10**: Check for Broken Object Level Auth (BOLA), excessive data exposure, and security misconfigurations.
3. **Patch Implementation**: Implement specific guards (e.g., strict payload parsing, scoped JWTs, role-based decorators).
4. **Verification**: Suggest explicit unit tests (or DAST scans) verifying unauthorized access is successfully rejected.

## Security & Guardrails

### 1. Skill Security
- **Execution Confinement**: When scanning APIs dynamically, do not send destructive or mutative payloads (e.g., `DELETE /users/1`) to any non-ephemeral environment.
- **Hardcoded Secret Scanners**: Ensure the agent does not explicitly print detected API secrets / API keys in the plaintext markdown output or logging trace.

### 2. System Integration Security
- **Token Handling Validation**: Agents must strictly mandate short-lived, signed JWTs (RS256) paired with opaque HttpOnly/Secure refresh tokens; never store JWTs in local storage.
- **BOLA Defense**: Explicitly mandate verifying ownership (`userId == req.params.userId`) on every resource access, mitigating systemic IDOR flaws.

### 3. LLM & Agent Guardrails
- **Roll-Your-Own Crypto Veto**: If requested to create a custom token signature or hashing function, the agent must fiercely refuse and import standard, verified libraries (like Argon2 or Passport.js).
- **False Positive Dismissal**: The agent must not confidently dismiss potential BOLA/IDOR findings without explicit human auditing of the domain authorization logic.
