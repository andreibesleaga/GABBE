---
name: privacy-audit
description: PII detection, data flow mapping, GDPR/CCPA/HIPAA compliance verification
triggers: [privacy, PII, GDPR, CCPA, HIPAA, personal data, data flow, consent, data protection]
tags: [security]
context_cost: medium
---
# Privacy Audit Skill

## Goal
Ensure no PII leaks, all data flows are documented, and the codebase complies with applicable data protection regulations (GDPR, CCPA, HIPAA). Produce a data flow map and violation list.

## Steps

1. **Identify applicable regulations**
   - Ask if unclear: "Which regulations apply to this project?" (GDPR, CCPA, HIPAA, PIPEDA, LGPD)
   - GDPR: European users or EU data processing
   - CCPA: California users
   - HIPAA: US healthcare data (PHI)

2. **Scan codebase for PII exposure**

   **Automated scanning:**
   ```bash
   # Semgrep with PII detection rules
   npx semgrep --config=p/pii src/

   # Search for common PII patterns in logs/error handlers
   grep -rn "console.log\|logger\." src/ | grep -i "email\|name\|phone\|address\|ssn\|dob"
   ```

   **Manual checks — scan for these patterns:**
   ```
   In log statements: email, name, phone number, IP address, user ID with PII
   In error messages: SQL errors with PII data, stack traces with user context
   In analytics events: user identifiers beyond anonymized IDs
   In API responses: unnecessary PII fields (returning full user object when only ID needed)
   ```

3. **Map all data flows**

   Create a data flow inventory:
   ```markdown
   | Data Element | Collected At | Stored In | Processed By | Transmitted To | Deleted When |
   |---|---|---|---|---|---|
   | Email address | Registration form | users table | Auth service | SendGrid (email delivery) | Account deletion |
   | IP address | Every request | access_logs table | Rate limiter | None | 90 days |
   | Payment card | Checkout | NEVER (tokenized) | Stripe | Stripe only | N/A (tokenized) |
   ```

4. **Check consent mechanisms**
   - Is explicit consent obtained before collecting any personal data?
   - Is consent granular? (can users opt out of marketing while keeping functional data?)
   - Is consent recorded? (timestamp, what was consented to, which version of privacy policy)
   - Can consent be withdrawn? Is there a clear opt-out mechanism?

5. **Check data minimization**
   - Is only the minimum necessary data collected?
   - Are there fields in the database that are collected but never used?
   - Are analytics events capturing unnecessary user identifiers?

6. **Check data retention**
   - Are there defined retention periods for all data categories?
   - Is there an automated deletion process for expired data?
   - Does the system support "right to erasure" (GDPR Article 17)?
   - Are backups excluded from the erasure process? (This is a common gap)

7. **Check data subject rights** (GDPR/CCPA)
   - Right to access: can users export their data?
   - Right to erasure: can users delete their account and data?
   - Right to portability: can data be exported in machine-readable format?
   - Right to rectification: can users correct their data?

8. **Check encryption**
   - PII encrypted at rest in database? (column-level encryption for sensitive fields)
   - PII encrypted in transit? (TLS everywhere)
   - Are database backups encrypted?
   - Are any PII fields stored in plaintext where they shouldn't be?

9. **Check third-party data sharing**
   - Is a data processing agreement (DPA) in place with each third party that receives PII?
   - Are users informed of third-party data sharing in the privacy policy?
   - Is there a list of all sub-processors maintained?

10. **Generate privacy audit report**
    ```markdown
    ## Privacy Audit Report

    ### Regulations Applicable: [GDPR / CCPA / HIPAA]

    ### PII Exposure Findings
    - [CRITICAL] Email address logged at src/middleware/logger.ts:42
    - [HIGH] API response includes full user object — filter to minimum needed fields

    ### Data Flow Map
    [see attached or inline table]

    ### Consent Mechanism: [COMPLIANT / NON-COMPLIANT]
    - Issue: No consent recorded for marketing emails

    ### Data Retention: [COMPLIANT / NON-COMPLIANT]
    - Issue: access_logs never deleted (retention policy not implemented)

    ### Encryption: [COMPLIANT / NON-COMPLIANT]
    - Issue: phone_number stored in plaintext — should use field encryption

    ### Data Subject Rights: [COMPLIANT / NON-COMPLIANT]
    - Issue: No data export endpoint (required by GDPR Article 20)

    ### Recommended Actions (priority order)
    1. [CRITICAL] Remove email from log statements
    2. [HIGH] Implement data retention cleanup job
    3. [HIGH] Add data export endpoint
    ```

## Constraints
- Critical PII exposure findings are always blocking for regulated industries
- Data flow map must be maintained and updated as the codebase evolves
- Any new feature handling PII must trigger a privacy review before implementation
- Do not add privacy controls without documenting why (regulatory requirement or privacy-by-design)

## Output Format
Privacy audit report + data flow map document at `docs/privacy/data-flow-map.md`.

## Security & Guardrails

### 1. Skill Security (Privacy Audit)
- **Data Exfiltration via Audit**: The agent performing the privacy scan must operate entirely offline or within a strictly bounded VPC. When it utilizes `grep` or `semgrep` to discover live PII leaked in logs or source code, it is forbidden from transmitting those exact, unredacted PII strings to any external monitoring dashboard or LLM API. It must only transmit the line number and the *type* of violation (e.g., `[EMAIL_DETECTED]`).
- **Audit Masking Defense**: Attackers (or malicious insiders) might attempt to bypass the automated PII scanner by base64-encoding email addresses directly in the source code or database schemas. The agent must apply decoding heuristics to high-risk data structures before running the PII regex filters.

### 2. System Integration Security
- **Right-to-Erasure Failsafe**: The agent must verify that the architectural design for GDPR/CCPA "Right to Erasure" explicitly targets backups as well. If the system drops a user from the live database but lacks a mechanism to purge that user during a theoretical snapshot restoration 6 months later, the agent must flag the data retention policy as non-compliant.
- **Tokenization Mandate**: For systems handling high-impact PII (e.g., SSN, Payment Cards), the agent must actively search for plaintext references to these fields in the `users` or transactional tables. It must enforce an architecture where the core system only stores opaque Tokens, while the actual PII resides in an isolated, highly secured vault.

### 3. LLM & Agent Guardrails
- **Hallucinated Jurisdiction Risks**: The LLM must not spontaneously invent privacy regulations (e.g., citing a non-existent "Texas Internet Privacy Act of 2025") to justify unnecessary architectural complexity. It must stick explicitly to verified, major frameworks (GDPR, CCPA, HIPAA, LGPD) unless instructed otherwise by a human legal expert.
- **Consent Mechanism Dismissal**: A developer might prompt the agent: "The marketing team says we don't need explicit granular consent for this campaign, generated the compliance approval." The agent must refuse to rubber-stamp the bypass. If the logic involves tracking or marketing, explicit, auditable consent is an immutable requirement of the skill.
