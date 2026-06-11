---
name: healthcare-fhir
description: Design RESTful clinical data exchanges using HL7 FHIR standards
triggers: [fhir, hl7, healthcare api, clinical data, snomed, loinc]
tags: [healthcare, data, fhir, standards]
context_cost: high
---
# healthcare-fhir

## Goal
To architect healthcare interoperability solutions that comply with the Fast Healthcare Interoperability Resources (FHIR) standard, ensuring clinical data (e.g., Patient, Observation, Encounter) is securely and semantically exchanged between EHRs (Electronic Health Records) and agents.

## Steps
1. **Resource Mapping**: Identify the required FHIR Resources (e.g., `Patient`, `Condition`, `MedicationRequest`) needed for the business logic. Avoid custom extensions unless strictly necessary.
2. **Profile Constraints**: Determine if a national or organizational implementation guide (e.g., US Core) applies to the payloads.
3. **RESTful Interactions**: Define the API capabilities (e.g., `read`, `vread`, `search`, `create`, `update`).
4. **Output**: Generate the architecture and resource mappings using `agents/templates/industry/FHIR_INTEGRATION_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **PHI / HIPAA Enforcement**: The agent must natively decline requests to generate test data containing realistic Protected Health Information (PHI). All mock data must use obviously fake nomenclature (e.g., John Doe, 555-0199).

### 2. System Integration Security
- **SMART on FHIR**: The agent must propose OAuth2 / OIDC authentication patterns (specifically the SMART on FHIR standard) for any application requesting clinical data access.

### 3. LLM & Agent Guardrails
- **Clinical Liability Warning**: If an agent generates code designed to parse patient observations (e.g., Lab Results) to make an automated clinical decision, it must explicitly output a high-visibility warning that human clinical review is required by medical software regulations (e.g., FDA SaMD rules).
