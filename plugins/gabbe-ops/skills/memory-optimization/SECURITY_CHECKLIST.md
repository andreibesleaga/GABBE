# Security Checklist — Pre-Release Gate
<!-- Complete before every production deployment — security-audit.skill auto-fills this -->
<!-- Date: [date] | Auditor: [agent/human] | Release: [version/tag] -->

---

## How to Use

Run through each section. Mark items:
- `[x]` PASS — verified and compliant
- `[ ]` FAIL — must be fixed before release
- `[~]` N/A — not applicable to this project (document why)

**All FAIL items are blocking. Do not release until all are PASS or N/A (with documented reason).**

---

## 1. Authentication & Authorization

- [ ] No hardcoded credentials in source code or config files
- [ ] Passwords hashed with bcrypt (cost >= 12) or Argon2 — never MD5, SHA1, SHA256
- [ ] Session tokens are cryptographically random (>= 128 bits entropy)
- [ ] JWT tokens: algorithm enforced (HS256/RS256), expiry set (<= 15 min access token)
- [ ] Refresh token rotation implemented (old token invalidated on use)
- [ ] MFA required for admin/privileged access
- [ ] Login endpoint: rate limited (max 5 attempts/min per IP, lockout after 10 fails)
- [ ] Password reset: single-use token, expires in 24 hours, invalidated on use
- [ ] Account lockout with notification to user
- [ ] All authorization checks server-side (never trust client-supplied role)
- [ ] RBAC/ABAC implemented and consistent across all endpoints
- [ ] IDOR prevention: ownership verified for all resource access (`record.userId === session.userId`)

---

## 2. Input Validation & Output Encoding

- [ ] All user inputs validated at system boundaries (HTTP body, query params, headers)
- [ ] SQL injection prevention: parameterized queries only (no string concatenation in SQL)
- [ ] Command injection prevention: no `exec()`/`shell_exec()` with user input
- [ ] XSS prevention: HTML encoding for all user-controlled output in HTML context
- [ ] Path traversal prevention: filename inputs sanitized, no `../` sequences
- [ ] File upload: type validation (whitelist), size limit, stored outside web root
- [ ] Mass assignment protection: explicit field allowlist (never spread `req.body` to ORM)
- [ ] Request size limits configured (prevent large payload DoS)
- [ ] CSRF protection: SameSite=Strict/Lax cookie or CSRF token for state-changing requests

---

## 3. Data Protection

- [ ] Sensitive data (PII, health data, financial) encrypted at rest
- [ ] All connections use TLS 1.2+ (TLS 1.3 preferred); no HTTP for sensitive data
- [ ] Secrets stored in environment variables or secrets manager (not in code or git)
- [ ] `.env` files in `.gitignore`
- [ ] API keys, tokens, connection strings not in git history (run: `gitleaks detect`)
- [ ] PII not logged (no email, name, phone, IP, SSN in log statements)
- [ ] Payment card data not stored (use tokenization — e.g., Stripe token instead of PAN)
- [ ] Personal data deletion implemented (GDPR Article 17 / CCPA right to delete)
- [ ] Database backups encrypted

---

## 4. Dependency Security

- [ ] `npm audit --audit-level=moderate` — zero critical or high CVEs
- [ ] `composer audit` — zero critical or high CVEs (or documented false positives)
- [ ] `pip-audit` / `snyk test` — clean (or documented exceptions)
- [ ] No end-of-life (EOL) dependencies (check: endoflife.date)
- [ ] License compliance verified (no GPL in commercial product without review)
- [ ] `gitleaks detect` — no secrets in git history

---

## 5. Container Security (if applicable)

- [ ] Docker image built from specific version (not `:latest`)
- [ ] Container runs as non-root user
- [ ] No secrets in Dockerfile or docker-compose.yml
- [ ] Build artifacts (node_modules, .git) excluded from image
- [ ] `trivy image [image]` — zero critical or high CVEs
- [ ] Minimal base image (Alpine preferred over full Debian)
- [ ] Multi-stage build (dev dependencies not in production image)

---

## 6. API Security

- [ ] Rate limiting on all public endpoints (not just auth)
- [ ] CORS configured: origin allowlist, not `*` for credentialed requests
- [ ] Security headers set:
  - `Content-Security-Policy`
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains`
  - `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] Sensitive data not in URL parameters (tokens, passwords — use POST body or headers)
- [ ] API versioning implemented (`/api/v1/`) — breaking changes go to new version
- [ ] GraphQL: introspection disabled in production, query depth limiting
- [ ] Pagination enforced (no unbounded queries returning all records)

---

## 7. Error Handling & Logging

- [ ] No stack traces in HTTP responses in production
- [ ] Production errors return generic messages (500 Internal Server Error) — details only in logs
- [ ] No PII in log statements
- [ ] Security events logged: failed logins, access denied, input validation failures
- [ ] Log levels appropriate: no verbose debug logging in production
- [ ] Logs shipped to SIEM or centralized logging (not only on local disk)

---

## 8. Infrastructure & Configuration

- [ ] Default credentials changed on all systems (databases, admin panels, services)
- [ ] Production environment variables separate from dev/staging
- [ ] Directory listing disabled on web server
- [ ] Debugging endpoints disabled in production (e.g., `/debug`, `/phpinfo`, `/__debugbar`)
- [ ] Admin panels restricted by IP or VPN (not public internet)
- [ ] Backup and restore procedure tested (not just configured)

---

## 9. OWASP Top 10 — Final Check

| OWASP Category | Status | Notes |
|---|---|---|
| A01: Broken Access Control | [ ] | IDOR checks, auth enforcement |
| A02: Cryptographic Failures | [ ] | Password hashing, TLS, encryption at rest |
| A03: Injection | [ ] | SQL injection, command injection, XSS |
| A04: Insecure Design | [ ] | Threat model completed for new features |
| A05: Security Misconfiguration | [ ] | Headers, defaults, error handling |
| A06: Vulnerable Components | [ ] | Dependency audit clean |
| A07: Auth Failures | [ ] | Rate limiting, session management, MFA |
| A08: Data Integrity | [ ] | File upload validation, SRI hashes |
| A09: Logging & Monitoring | [ ] | Security events logged, SIEM configured |
| A10: SSRF | [ ] | URL fetching uses allowlist |

---

## 10. Release Sign-Off

| Category | Status | Verified by | Date |
|---|---|---|---|
| Authentication & Authorization | PASS / FAIL | [name] | [date] |
| Input Validation | PASS / FAIL | [name] | [date] |
| Data Protection | PASS / FAIL | [name] | [date] |
| Dependencies | PASS / FAIL | [name] | [date] |
| Container Security | PASS / FAIL / N/A | [name] | [date] |
| API Security | PASS / FAIL | [name] | [date] |
| Error Handling & Logging | PASS / FAIL | [name] | [date] |
| OWASP Top 10 | PASS / FAIL | [name] | [date] |

**OVERALL: APPROVED / NOT APPROVED**

*All items must be PASS or N/A (with documented reason) before production release.*
