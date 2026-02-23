# Global Standards & Public-Sector Audit Template

**Project/System Name:** [System Name]
**Target Sector/Deployment:** [e.g., EU Gov, UN NGO, Public Enterprise]
**Date:** [YYYY-MM-DD]
**Auditor / Agent:** [Agent Name]

## 1. United Nations Sustainable Development Goals (SDGs)
*How does this software impact the broader global community?*

| SDG Mandate | Software Application / Output | Compliance Check |
| :--- | :--- | :--- |
| **Goal 9: Industry & Infrastructure** | [Does the software provide open APIs? Is it resilient to internet outages?] | [Pass/Fail] |
| **Goal 10: Reduced Inequalities** | [Does the UI adhere to WCAG 2.1 AA+? Is there multi-language support?] | [Pass/Fail] |
| **Goal 12: Responsible Consumption**| [Has a Green Software SCI report been generated? See Green Tech skill] | [Pass/Fail] |

## 2. ITU-T Telecommunication Standards
*Verify protocols that cross international borders.*

- **X.509 (PKI / Security)**:
  - Are all TLS certificates using currently approved cyphers (e.g., no SHA-1 signatures)? [Yes/No]
  - Is mutual TLS (mTLS) required for inter-service communication? [Yes/No]
- **E.164 (Numbering)**:
  - Are all database columns storing phone numbers enforcing E.164 format (e.g., `+447123456789`)? [Yes/No]
- **H-Series / Audio-Visual**:
  - [Specify codecs used if manipulating media files (e.g., H.265/HEVC)]

## 3. Global Open Source (OSI & OpenSSF)
*Verify the supply chain and legal standing of the software.*

### 3.1 License Compatibility (OSI Approved)
- **Primary Codebase License**: [e.g., Apache 2.0 / Proprietary]
- **Dependency Risk**: Are there any strict Copyleft dependencies (e.g., AGPLv3) compiled into this proprietary codebase that could force open-sourcing the parent project? [Yes/No/Mitigated]

### 3.2 Supply-Chain Levels for Software Artifacts (SLSA)
- **Source Build**: Is the build process fully scripted and running on a hardened CI/CD runner? (SLSA L1/L2)
- **Provenance**: Does the build system generate an unforgeable attestation statement? (SLSA L3)
- **Two-Person Review**: Is branch protection enabled requiring multiple approvals before merging to Main? [Yes/No]

## 4. International Privacy Addendum
- Has the architecture been reviewed against the strictest common denominators for global privacy?
  - GDPR (European Union)
  - CCPA (California)
  - HIPAA (US Healthcare) if applicable
*Note: If specific regional compliance is needed, invoke the `compliance-review` skill.*
