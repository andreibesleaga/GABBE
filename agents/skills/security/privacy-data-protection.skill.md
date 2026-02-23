---
name: privacy-data-protection
description: Elicit and enforce GDPR, CCPA, and general privacy by design rules
triggers: [design privacy system, audit gdpr conformity, protect pii]
tags: [security]
context_cost: medium
---
# privacy-data-protection

## Goal
Implement Data Privacy by Design. Ensure PII and PCI data are properly isolated, encrypted, minimal, and subject to Data Subject Access Requests (DSARs).


## Steps
1. **Data Mapping**: Scan schemas using the `DATA_PIPELINE_TEMPLATE.md` to map exactly where PII resides.
2. **Minimization**: Flag unnecessary PII collection fields and suggest removal.
3. **Protection Mechanisms**: Ensure row-level encryption, dynamic masking, or pseudo-anonymization is applied to sensitive columns.
4. **Verification**: Document the processes for user deletion (Right to be Forgotten) and data export.

## Security & Guardrails

### 1. Skill Security
- **Data Exfiltration Safety**: When the agent scans schemas for PII, it must never output sample plaintext records from the database to the chat interface. It only operates on schema structure.
- **Log Overflow**: Prevent the agent from generating excessively large mapping documents that break context limits if scanning a very large ERP database.

### 2. System Integration Security
- **Masking at the Edge**: PII unmasking must only occur at the absolute periphery (e.g., the front-end view) or explicitly authorized service borders; logs and analytics pipelines must receive obfuscated/hashed fields.
- **De-Identification**: Enforce strong pseudo-anonymization (using salted hashes) over weak techniques when storing analytics data.

### 3. LLM & Agent Guardrails
- **Legal Advice Veto**: The agent must state that it provides technical architectural patterns for privacy, not formal legal or compliance defense.
- **Implicit Consent Bias**: The LLM must not architect systems that assume user tracking/consent is granted by default (opt-out). It must strictly enforce opt-in architectures.
