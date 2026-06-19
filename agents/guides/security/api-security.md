# Guide: API Security Standards (2025)
<!-- OWASP API Top 10, Authentication, Authorization, Rate Limiting -->

---

## 1. Authentication & Identity
Never roll your own crypto or identity provider. Use established standards.

### Standards
- **User Authentication**: OpenID Connect (OIDC) via Auth0, Okta, or Keycloak.
- **Machine-to-Machine**: OAuth 2.0 Client Credentials flow.
- **Session Tokens**: JWT (JSON Web Tokens) with short lifespans (< 15 mins) and refresh tokens (sliding windows, rotating).

### JWT Best Practices
- **Algorithm**: Enforce `alg: RS256` (or EdDSA). NEVER allow `alg: none`.
- **Payload**: Never store PII or sensitive data in the JWT payload (it's base64 encoded, not encrypted).
- **Validation**: Always validate `exp` (expiration), `iss` (issuer), and `aud` (audience).

## 2. Authorization (Access Control)
Authentication proves *who* you are; Authorization proves *what* you can do.

- **BOLA (Broken Object Level Authorization)**: Always verify that the authenticated user owns the object they are requesting (e.g., `GET /api/users/123/financials` should check if the current user ID is 123 or an admin).
- **RBAC vs ABAC**: Use Role-Based Access Control (Admin, User) for broad permissions. Use Attribute-Based Access Control for fine-grained permissions (e.g., "Can edit document if document.owner == user.id").
- **Zero Trust**: Never assume a request is safe because it comes from an internal network. Authenticate and authorize every internal microservice call (mTLS + JWT).

## 3. Input Validation & Output Encoding
Validate strictly on the way in; encode strictly on the way out.

- **Schema Validation**: Use strict schemas (Zod in TS, Pydantic in Python) to validate type, length, format, and range. Reject extra fields.
- **SQL Injection**: Always use ORMs or parameterized queries. NEVER concatenate strings into SQL.
- **XSS (Cross-Site Scripting)**: Sanitize output before rendering it in a browser, or rely on modern frameworks (React/Vue/Angular) which auto-escape by default.

## 4. Rate Limiting & Abuse Prevention
Assume your API will be attacked by bots.

- **Rate Limiting**: Apply global headers (`X-RateLimit-Remaining`).
- **Throttling**: Slow down responses for IPs/Tokens hitting limits before outright blocking them.
- **Authentication Routes**: Apply extremely strict limits to `/login` and `/forgot-password` to prevent credential stuffing and brute force.

## 5. OWASP API Top 10 Overview
Ensure these vulnerabilities are mitigated in every PR:
1. **Broken Object Level Authorization (BOLA)**
2. **Broken Authentication**
3. **Broken Object Property Level Authorization** (Mass Assignment)
4. **Unrestricted Resource Consumption** (Lack of Rate Limiting/Pagination)
5. **Broken Function Level Authorization** (Users hitting Admin routes)
6. **Unrestricted Access to Sensitive Business Flows**
7. **Server Side Request Forgery (SSRF)**
8. **Security Misconfiguration**
9. **Improper Inventory Management** (Zombie/Shadow APIs)
10. **Unsafe Consumption of APIs** (Trusting 3rd party APIs unconditionally)
