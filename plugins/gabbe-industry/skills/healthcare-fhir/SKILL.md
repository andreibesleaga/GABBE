---
name: healthcare-fhir
description: "FHIR resource mapping, profiles and REST interactions for clinical data exchange. Use when integrating with an electronic health record system or building a healthcare API."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/industry/healthcare-fhir.skill.md"
  tags: "healthcare, data, fhir, standards"
  core: "false"
  context_cost: "high"
---
# healthcare-fhir

## Goal
To architect healthcare interoperability solutions that comply with the Fast Healthcare Interoperability Resources (FHIR) standard, ensuring clinical data (e.g., Patient, Observation, Encounter) is securely and semantically exchanged between EHRs (Electronic Health Records) and agents.

## Steps
1. **Resource Mapping**: Identify the required FHIR Resources (e.g., `Patient`, `Condition`, `MedicationRequest`) needed for the business logic. Avoid custom extensions unless strictly necessary.
2. **Profile Constraints**: Determine if a national or organizational implementation guide (e.g., US Core) applies to the payloads.
3. **RESTful Interactions**: Define the API capabilities (e.g., `read`, `vread`, `search`, `create`, `update`).
4. **Output**: Generate the architecture and resource mappings using `agents/templates/industry/FHIR_INTEGRATION_TEMPLATE.md`.

## Constraints
- Prefer standard resources and implementation guides over custom extensions.
- Name the implementation guide (for example US Core) when one applies.

## Output Format
`FHIR_INTEGRATION_TEMPLATE.md` (`agents/templates/industry/`) filled in with resource mappings and interactions.

## Limits and safety
- Test data is obviously fake (John Doe, 555-0199); if a file holds real patient data, stop and tell the human.
- Propose SMART on FHIR (OAuth2 and OIDC) for any access to clinical data.
- Code that turns observations into automated clinical decisions carries a visible warning that clinical review and regulation (for example FDA software-as-a-medical-device rules) apply; never claim approval.
- Use a sandbox FHIR server, never a live one with real patients.
