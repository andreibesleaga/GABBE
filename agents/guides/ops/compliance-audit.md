# Guide: Compliance & Audit Logging
<!-- GDPR, SOC2, HIPAA, and Security Auditing Standards -->

---

## Overview

Compliance is not just about checking boxes; it's about **traceability** and **privacy**. This guide defines how to implement audit logging, handle PII (Personally Identifiable Information), and meet regulatory requirements (GDPR, CCPA, SOC2, HIPAA) across our tech stacks.

---

## 1. The Audit Log Standard

Every mutation of regulated data MUST be logged. Identifying *who* did *what* to *whom* and *when*.

### The 5 Ws of Audit Logging
1.  **Who:** `actor_id` (User UUID, Service Account, or API Key ID)
2.  **What:** `action` (CREATE, UPDATE, DELETE, VIEW, EXPORT)
3.  **When:** `timestamp` (ISO 8601 UTC)
4.  **Where:** `ip_address`, `user_agent`, `resource_id` (Target entity)
5.  **Why:** `context` (Request ID, Reason code)

### Audit Log Schema (JSON)

```json
{
  "timestamp": "2023-10-27T10:00:00Z",
  "event_id": "evt_123456789",
  "actor": {
    "id": "usr_987654321",
    "type": "user",
    "ip": "203.0.113.1",
    "email": "alice@example.com"
  },
  "action": "user.password_reset",
  "target": {
    "id": "usr_987654321",
    "type": "user"
  },
  "changes": {
    "prev": null,
    "next": null // Never log secrets/passwords!
  },
  "metadata": {
    "trace_id": "trc_abc123",
    "status": "success"
  }
}
```

---

## 2. GDPR & Privacy Engineering

### PII Classification
*   **Public:** Product names, doc content. -> *No redaction needed.*
*   **Internal:** Internal IDs, non-sensitive configs. -> *Log freely.*
*   **Confidential (PII):** Email, IP, Phone, Name. -> *Mask in app logs, encrypt in DB.*
*   **Restricted (Sensitive PII):** SSN, Passport, Credit Card (PAN), Health Data. -> *Tokenize, strict access control, never log.*

### Data Subject Rights
*   **Right to Access (DSAR):** System must be able to export ALL data for a `user_id` (JSON export).
*   **Right to Verification:** Logs must prove data hasn't been tampered with.
*   **Right to Erasure (RTBF):**
    *   **Hard Delete:** Delete row. (Data gone).
    *   **Soft Delete:** RESTRICTED method. (Marked `deleted_at`).
    *   **Anonymization:** Overwrite PII with `REDACTED`. **Preferred for audit logs.**
    *   *Note:* You CANNOT delete Audit Logs for security reasons (legitimate interest), but you MUST anonymize the PII within them if requested and retention period passed.

---

## 3. Implementation Strategies

### Node.js / TypeScript
**Libraries:** `pino` (logging), `open-telemetry` (tracing)

```typescript
import pino from 'pino';

const auditLogger = pino({
  base: { service: 'user-service' },
  redact: {
    paths: ['email', 'password', 'token'],
    censor: '[REDACTED]'
  }
});

function logAudit(actor: Actor, action: string, target: Entity) {
  auditLogger.info({
    type: 'audit', // Differentiates from debug/app logs
    actor_id: actor.id,
    action,
    target_id: target.id,
    target_type: target.constructor.name
  });
}
```

### Python / FastAPI
**Libraries:** `structlog` (structured logging)

```python
import structlog

logger = structlog.get_logger()

# Middleware for Audit
async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method in ["POST", "PUT", "DELETE"]:
        await logger.info(
            "audit_event",
            actor_id=request.state.user.id,
            action=f"{request.method} {request.url.path}",
            status=response.status_code
        )
    return response
```

### PHP / Laravel
**Libraries:** `spatie/laravel-activitylog`

```php
activity()
   ->performedOn($order)
   ->causedBy($user)
   ->withProperties(['amount' => 100])
   ->log('Order placed');
   
// In model
protected $logAttributes = ['status', 'total']; // Only log safe attributes
protected $logOnlyDirty = true;
```

---

## 4. Security Monitoring (SIEM)

### What to Alert On
1.  **Authentication Failures:** > 5 failures in 1 minute from single IP.
2.  **Privilege Escalation:** User added to `admin` group.
3.  **Mass Export:** User exports > 100 records (DLP monitoring).
4.  **Sensitive Access:** Access to "Break Glass" accounts.
5.  **Configuration Change:** Production ENV vars changed.

### Log retention (Standard)
*   **App Logs (Debug/Info):** 7-30 days.
*   **Audit Logs (Security):** 1 year (Hot/Cold storage).
*   **Archive:** 6 years (HIPAA/Financial).

---

## 5. Compliance Checklist (Quick Reference)

*   [ ] **Encryption:** TLS 1.2+ in transit, AES-256 at rest.
*   [ ] **Access Control:** RBAC implemented + MFA for admins.
*   [ ] **Audit Trails:** Immutable logs for all writes.
*   [ ] **Backups:** Encrypted and tested quarterly.
*   [ ] **Vulnerability Scanning:** Automated SAST/DAST in CI/CD.
*   [ ] **Privacy Policy:** Accessible and accurate.
*   [ ] **Incident Response:** Plan tested annually.

---

## Output for Auditor
When an auditor asks "Show me evidence of Access Control", providing the `core/AUDIT_LOG_TEMPLATE.md` (for Loki/Dev) or the SIEM dashboard screenshots (for Prod) is standard proof.

---

## 6. Relevant Skills

| Skill | Purpose |
|---|---|
| `access-control` | Implements RBAC/ABAC and Identity Management. |
| `data-governance` | Enforces Data Classification (PII tags) and Lineage. |
| `security-audit` | Checks for hardcoded secrets and known vulnerabilities. |
| `privacy-audit` | Maps PII data flow and checks for GDPR compliance. |
