---
name: data-governance
description: Data lineage, classification (PII/Confidential), and integrity checks (checksums).
triggers: [data governance]
tags: [data]
role: biz-compliance, eng-data
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

## Security & Guardrails

### 1. Skill Security (Data Governance)
- **Classification Tampering Prevention**: Restrict permissions to modify data classification tags (Public, Internal, Confidential, PII). Only authorized governance roles should alter these definitions.
- **Immutability of Audit Logs**: Ensure that data lineage and access logs are stored in append-only, immutable storage to prevent tampering by malicious actors.

### 2. System Integration Security
- **Encryption Enforcement**: Systems integrating with governed data must enforce Encryption at Rest for any data classified as Restricted/PII.
- **Access Control Verification**: Governance tools must integrate with identity providers (IAM/SSO) to continuously verify that only users with the correct clearance access sensitive datasets.
- **Automated Compliance Checks**: Implement automated scanning in CI/CD pipelines to block deployments that violate data retention or geographical residency rules (e.g., GDPR data leaving the EU).

### 3. LLM & Agent Guardrails
- **Data Exfiltration Prevention**: Agents analyzing data lineage or governance policies must be blocked from exporting raw PII or Confidential data in their outputs or external API calls.
- **Context Boundary Enforcement**: When an LLM queries metadata or schemas, ensure the context window does not inadvertently ingest actual user data or sensitive records.
- **Hallucination Mitigation for Compliance**: LLM-generated compliance reports must be verified against hardcoded rules. An agent must not "hallucinate" compliance approval for a system failing legal checks.
