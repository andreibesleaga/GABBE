---
name: privacy-data-protection
description: Map personal data, minimise it, protect it, and design deletion and export for GDPR or CCPA duties. Use when designing a feature that stores personal or payment data.
triggers: [privacy by design, data minimisation, pseudonymisation, dsar, right to erasure, protect pii]
tags: [security]
context_cost: medium
---
# privacy-data-protection

## Goal
Implement Data Privacy by Design. Ensure PII and PCI data are properly isolated, encrypted, minimal, and subject to Data Subject Access Requests (DSARs).

## Where it fits
Phase and gate: S01 (privacy requirements), S02 (data classification), S07 (review), S13 (disposal). Evidence: the data map in `docs/privacy/data-flow-map.md`. Guide: `guides/security/privacy-data-protection.md`.

## Steps
1. **Data Mapping**: Scan schemas using the `DATA_PIPELINE_TEMPLATE.md` to map exactly where PII resides.
2. **Minimization**: Flag unnecessary PII collection fields and suggest removal.
3. **Protection Mechanisms**: Ensure row-level encryption, dynamic masking, or pseudo-anonymization is applied to sensitive columns.
4. **Verification**: Document the processes for user deletion (Right to be Forgotten) and data export.

## Constraints
- Collect only data a stated purpose needs.
- Every personal field in the data map has a retention period and a deletion path.

## Output Format
The data map (`docs/privacy/data-flow-map.md`), the list of fields to remove or protect, and the deletion and export procedure.

## Limits and safety
- Use masked or synthetic data when you scan schemas. Report column names and types, not values.
- Deletion and export designs cover backups and logs. Propose deletion jobs; run them on real data only after the human confirms.
- Which law applies is for the human or counsel to decide. Ask; do not assume.
- Do not add a new personal-data field without the human's yes.
