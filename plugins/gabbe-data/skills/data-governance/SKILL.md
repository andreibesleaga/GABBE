---
name: data-governance
description: "Data classification, lineage, integrity and retention rules with a deletion workflow. Use when handling personal or confidential data, or when asked where a value came from or how long data may be kept."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/data/data-governance.skill.md"
  tags: "data"
  core: "false"
  context_cost: "low"
---
# data-governance Skill

## Goal
Data must be classified, tracked, and verifiable.

## Steps
## 1. Classification
Before storing any field, tag it:
- **Public**: Safe to release (e.g., Product Descriptions).
- **Internal**: Employee-only (e.g., Org Charts).
- **Confidential**: Business secrets (e.g., Sales Forecasts).
- **Restricted/PII**: SSN, Credit Cards, Medical Records. **Must be Encrypted at Rest**.

## 2. Integrity Patterns
- **Checksums**: Store `md5/sha256` of files to detect bit-rot or tampering.
- **Foreign Keys**: Enforce referential integrity in the DB. No orphans.
- **Versioning**: Never overwrite critical data. Use `v1`, `v2` or Event Sourcing `AppendedOnly`.

## 3. Lineage
- Answer: "Where did this specific value in the dashboard come from?"
- Track: Source System -> ETL Job -> Warehouse -> BI Tool.

## 4. Retention & Deletion (GDPR/CCPA)
- **TTL**: Auto-delete logs after X days.
- **Right to be Forgotten**: Implementation of a `HardDeleteUser` workflow that purges PII from all tables/backups (crypto-shredding).

## Constraints
- Every field is classified before it is stored.
- Critical data is versioned, never overwritten.

## Output Format
A field classification table, a lineage map (source, job, warehouse, report) and the retention and deletion rules, in the project's docs folder.

## Limits and safety
- Only governance roles change classification tags; the agent proposes changes.
- Work from metadata and schemas; do not load real records, and do not copy personal or confidential values into outputs.
- Restricted and personal fields are encrypted at rest; lineage and access logs go to append-only storage where the platform has it.
- A deletion workflow (purge of personal data from tables and backups) is proposed as a plan; the human approves it before anything runs.
- A compliance report says what was checked and what was not; never mark a system compliant without running the rule check.
