---
name: global-standards
description: Enforce UN, ITU, and Global Open Source (OSI, OpenSSF) software standards
triggers: [un standards, itu guidelines, open source compliance, global interoperability, osi, openssf]
tags: [governance, standards, global, un, itu]
context_cost: medium
---
# global-standards

## Goal
To audit and architect software systems that comply with global public-sector mandates, including UN Sustainable Development Goals (SDGs), International Telecommunication Union (ITU-T) baseline standards, and major Open Source/Cybersecurity foundation protocols (OpenSSF, OSI).

## Steps
1. **Identify the Scope**: Determine if the project is infrastructure-heavy (requiring ITU-T networking standards), socially impactful (requiring UN SDG alignment), or deeply reliant on OSS (requiring OpenSSF scorecard checks).
2. **Apply Standards**:
   - **UN SDGs**: Specifically map the software's impact to Goal 9 (Industry, Innovation, and Infrastructure) and Goal 11 (Sustainable Cities), focusing on digital inclusivity.
   - **ITU-T**: Enforce X.509 for public key infrastructure, E.164 for international telecommunication numbering, or H-series for video/multimedia protocols.
   - **Open Source (OSI/OpenSSF)**: Verify license compatibility (mitigating copyleft contamination like AGPL in proprietary bases) and apply OpenSSF SLSA (Supply-chain Levels for Software Artifacts) for build provenance.
3. **Output**: Generate the compliance and strategic layout using `agents/templates/industry/GLOBAL_STANDARDS_AUDIT_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **Open Source Supply Chain**: The agent must proactively highlight the risk of relying on unmaintained, single-maintainer open-source repositories when conducting a global standards review.

### 2. System Integration Security
- **Encryption Baselines**: When applying ITU-T standards, the agent must reject deprecated cryptographic algorithms (e.g., MD5, SHA-1, DES) ensuring X.509 architectures utilize modern (e.g., ECDSA, RSA-2048+) curves.

### 3. LLM & Agent Guardrails
- **No Legal Counsel**: The LLM must explicitly state that license compatibility checks (e.g., GPL vs MIT interactions) are for architectural guidance only and do not replace formal legal counsel.
