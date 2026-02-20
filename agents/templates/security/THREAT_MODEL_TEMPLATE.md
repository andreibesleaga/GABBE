# Threat Model: [Feature/Component Name]
<!-- Created by: threat-model.skill BEFORE implementation begins -->
<!-- Store in: docs/security/threat-models/[feature]-threat-model.md -->
<!-- Date: [date] | Author: [agent/human] -->

---

## 1. Feature Overview

**Feature being modeled:** [Name from PRD.md]
**System diagram reference:** [link to C4 Component diagram or describe components]
**Scope:** [What IS and IS NOT included in this threat model]

---

## 2. System Architecture for This Feature

```
[Draw the data flow — who sends data, where it goes, what stores it]

User Browser
    |
    | HTTPS (TLS 1.3)
    v
API Gateway / Load Balancer
    |
    v
[Your Service] ←────── Auth Service (JWT validation)
    |
    +──> Database (PostgreSQL)
    |
    +──> Cache (Redis)
    |
    +──> External Service (SendGrid, Stripe, etc.)
```

---

## 3. Trust Boundaries

| Boundary | Description | What crosses it |
|---|---|---|
| Internet → API | Public internet to your API | HTTP requests, user input |
| API → Database | Application to data store | SQL queries, connection string |
| API → External | Application to third party | API calls, webhooks |
| Admin → System | Privileged access | Admin operations, config changes |

---

## 4. Assets to Protect

| Asset | Classification | What happens if compromised |
|---|---|---|
| User passwords | Restricted | Account takeover |
| User PII (email, name) | Confidential | Privacy violation, GDPR liability |
| Payment data | Restricted | Financial fraud, PCI-DSS violation |
| Session tokens / JWT | Restricted | Account takeover |
| [Other assets] | [classification] | [impact] |

---

## 5. STRIDE Threat Analysis

### Spoofing (S) — Can an attacker impersonate something/someone?

| Threat | Likelihood (L/M/H) | Impact (L/M/H) | Priority | Mitigation |
|---|---|---|---|---|
| Stolen JWT allows user impersonation | H | H | Critical | Short expiry (15min), refresh rotation, token revocation list |
| API key theft allows service impersonation | M | H | High | API key hashing in storage, rate limiting per key, rotation policy |
| [threat] | | | | |

### Tampering (T) — Can an attacker modify data without authorization?

| Threat | Likelihood | Impact | Priority | Mitigation |
|---|---|---|---|---|
| IDOR: user modifies another user's record via /api/users/{id} | H | H | Critical | Verify ownership: request.userId === record.userId before update |
| SQL injection via search parameter | M | H | High | Parameterized queries only (never string concatenation in SQL) |
| Request body tampering (mass assignment) | H | M | High | Explicit allowlist of updatable fields (never update all body fields) |
| [threat] | | | | |

### Repudiation (R) — Can an attacker deny performing an action?

| Threat | Likelihood | Impact | Priority | Mitigation |
|---|---|---|---|---|
| User denies making a financial transaction | M | H | High | Immutable audit log with user ID, timestamp, action |
| Admin denies making a configuration change | L | H | Medium | Admin action logging with identity proof |
| [threat] | | | | |

### Information Disclosure (I) — Can an attacker access data they shouldn't?

| Threat | Likelihood | Impact | Priority | Mitigation |
|---|---|---|---|---|
| Verbose error reveals internal paths/DB structure | H | M | High | Sanitize error messages in production (generic 500 message) |
| PII in server logs accessible to unauthorized staff | M | H | High | Remove PII from logs, restrict log access |
| SSRF allows reading internal services | L | H | Medium | URL allowlist for any user-controlled URL fetching |
| [threat] | | | | |

### Denial of Service (D) — Can an attacker degrade service availability?

| Threat | Likelihood | Impact | Priority | Mitigation |
|---|---|---|---|---|
| Brute force on login endpoint | H | H | Critical | Rate limit: 5 attempts/min per IP, 3 per account, lockout |
| Large file upload overwhelms storage | M | M | Medium | File size limit (10MB), type validation, async processing |
| Expensive query abuse via API | M | M | Medium | Query timeout (30s), pagination required (max 100 records) |
| [threat] | | | | |

### Elevation of Privilege (E) — Can an attacker gain more access than allowed?

| Threat | Likelihood | Impact | Priority | Mitigation |
|---|---|---|---|---|
| Horizontal privilege escalation via IDOR | H | H | Critical | Resource ownership check on every authenticated endpoint |
| JWT algorithm confusion attack | L | H | High | Enforce algorithm in JWT verification (HS256, reject "none") |
| Role check bypass via parameter manipulation | M | H | High | Server-side role check from auth token, never from request body |
| [threat] | | | | |

---

## 6. Risk Summary

| Priority | Count | Must fix before? |
|---|---|---|
| Critical | [N] | Feature ships |
| High | [N] | Within 7 days of discovery |
| Medium | [N] | Within 30 days |
| Low | [N] | Next sprint |

---

## 7. Mitigations Implemented

<!-- Track implementation status of each mitigation -->

| Mitigation | Status | Task ID | Implemented in |
|---|---|---|---|
| JWT short expiry (15min) | NOT_STARTED | T-[NNN] | — |
| IDOR ownership check | NOT_STARTED | T-[NNN] | — |
| Rate limiting on login | NOT_STARTED | T-[NNN] | — |
| [mitigation] | [status] | | |

---

## 8. Security Invariants Added to CONSTITUTION.md

<!-- New security rules discovered during threat modeling that should be constitutionalized -->

```
Article [N] — [Topic]
WHEN [condition]
THE SYSTEM SHALL [security control].
```

---

## 9. Residual Risks

<!-- Threats we accept without full mitigation — requires human sign-off -->

| Threat | Why accepted | Risk owner | Review date |
|---|---|---|---|
| [threat] | [business reason for accepting the risk] | [role] | [date] |

---

## 10. Review & Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Security | [name] | [APPROVED / PENDING] | [date] |
| Tech Lead | [name] | [APPROVED / PENDING] | [date] |

**Approval required before implementing any security-sensitive feature.**
