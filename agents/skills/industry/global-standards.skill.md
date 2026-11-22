---
name: global-standards
description: Audit against UN SDG, ITU-T and open source (OSI, OpenSSF) requirements, written as a report. Use when a public-sector or open source project needs a standards or licence check.
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

## Constraints
- Scope first: infrastructure, social impact or open source dependence.
- Licence findings state which licences were compared.

## Output Format
`GLOBAL_STANDARDS_AUDIT_TEMPLATE.md` (`agents/templates/industry/`) filled in.

## Limits and safety
- Licence checks are guidance, not legal advice; tell the human to take legal counsel for copyleft combinations such as AGPL in a proprietary base.
- Flag unmaintained or single-maintainer dependencies.
- Reject deprecated algorithms (MD5, SHA-1, DES) in certificate and key designs.
- Cite an ITU-T or SDG item only from text you have read; otherwise write "unverified".
