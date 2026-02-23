# Healthcare Interoperability & FHIR Guide

## 1. Introduction
The Fast Healthcare Interoperability Resources (FHIR) standard is the modern framework for exchanging electronic health records (EHR). It was developed by HL7 (Health Level Seven International) combining the best features of previous standards (v2, v3, CDA) with modern web APIs.

## 2. Why FHIR?
Historically, clinical data exchange relied on rigid, difficult-to-parse EDI messages (HL7 v2) or complex XML documents (CDA).
FHIR utilizes HTTP RESTful APIs, JSON/XML, and OAuth2, drastically lowering the barrier to entry for developers building clinical apps. Every major EHR vendor (Epic, Cerner, Meditech) now supports FHIR, mandated by global regulations (like the US 21st Century Cures Act).

## 3. Core Concepts

### Resources
FHIR is built on "Resources"—modular, standardized building blocks of clinical data.
- **Patient**: Demographics (Name, Gender, BirthDate, Contact).
- **Observation**: A single data point (Blood Pressure, Lab Result, Social History).
- **Condition**: A clinical diagnosis.
- **Encounter**: A visit between a patient and a practitioner.
- **MedicationRequest**: A prescription.

### Profiles & Implementation Guides
The base FHIR standard is too broad: a "Patient" in the US requires a Race extension, but "Race" is illegal to track in France.
To solve this, FHIR uses **Profiles** which constrain the base resource. An **Implementation Guide (IG)** is a collection of profiles (e.g., US Core, UK Core, IPS). Your application must adhere to the specific IG of the region it operates in.

## 4. Architectural Integration Models
- **RESTful API Endpoint**: Your application queries the EHR on-demand (e.g., `GET /Patient/123`).
- **SMART on FHIR**: A specific profile of OAuth2 allowing third-party apps to securely authorize against an EHR, embedding directly into the clinician's workflow without sharing passwords.
- **FHIR Subscriptions**: Pub/Sub model where the EHR sends a webhook payload to your system when a specific event occurs (e.g., ADT - Admission/Discharge/Transfer).

## 5. Using the Skill
When tasked with integrating medical systems or interpreting clinical data schemas, use the `healthcare-fhir` skill. This ensures:
1. Patient privacy (PHI) is explicitly handled.
2. Clinical codes (SNOMED/LOINC) are used appropriately.
3. The resulting `FHIR_INTEGRATION_TEMPLATE.md` maps local databases to globally compliant standards.
