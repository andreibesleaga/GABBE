# FHIR & Health Data Integration Template

**System Name:** [Name of the Health App / Integration]
**FHIR Version:** [e.g., R4 (Current Stable)]
**Date:** [YYYY-MM-DD]
**Architect / Agent:** [Agent Name]

## 1. Integration Objective
[Describe what clinical data is being moved, and why. e.g., "Pulling lab results from an Epic EHR to display in a patient-facing mobile application."]

## 2. Resource Mapping
*Map internal app data models to standard FHIR resources.*

| Internal Data Entity | FHIR Resource | Supported Search Parameters | Profile / Implementation Guide |
| :--- | :--- | :--- | :--- |
| User Profile | `Patient` | `_id`, `name`, `birthdate` | US Core Patient |
| Doctor Visit | `Encounter` | `patient`, `date` | Standard R4 |
| Lab Result | `Observation` | `patient`, `category=laboratory` | US Core Laboratory Result |
| Prescription | `MedicationRequest` | `patient`, `status` | Standard R4 |

## 3. Communication Patterns
- [ ] **RESTful API**: Standard synchronous CRUD operations over HTTP.
- [ ] **Subscriptions (Webhooks)**: Asynchronous notifications when a resource changes (e.g., an EHR pinging your app when a new lab result is ready).
- [ ] **Messaging / Bulk Data**: Managing gigabytes of population health data via NDJSON (Flat FHIR).

## 4. Security & Compliance (SMART on FHIR)
- **Authentication**: OAuth2.0 standard flow.
- **Authorization Scopes**: [Define exact clinical scopes required, e.g., `patient/Observation.read`, `patient/Patient.read`. Do not use wildcard `*` scopes.]
- **Audit Logging**: [Describe how access to PHI is logged and retained for 7 years to meet HIPAA/GDPR requirements.]

## 5. Terminology & Coding Systems
*Clinical data relies on standard vocabularies.*
- **Diagnoses / Conditions**: ICD-10 or SNOMED CT
- **Lab Tests / Observations**: LOINC
- **Medications**: RxNorm (US) or SNOMED (International)

## 6. Sample Payload (Mock Data)
```json
{
  "resourceType": "Patient",
  "id": "example-1",
  "active": true,
  "name": [
    {
      "use": "official",
      "family": "Smith",
      "given": [ "John" ]
    }
  ],
  "gender": "male",
  "birthDate": "1970-01-01"
}
```
