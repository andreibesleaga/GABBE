---
name: legacy-modernization
description: Plan to understand and modernise legacy code (COBOL, mainframe, Fortran) — analysis, API wrapper, strangler plan and characterisation tests. Use when old code with little documentation must be explained, wrapped or replaced step by step.
triggers: [legacy code, cobol, mainframe, fortran, ibm z, jcl, db2, cics, modernization, rewrite, migration]
tags: [architecture]
context_cost: medium
---
# Legacy Modernization Skill

## Goal
To respect the critical nature of legacy systems while safely guiding them toward modernization. **Rule #1: Do no harm.**

## Capabilities

### 1. Code Analysis (The Archaeologist)
-   **Explain Logic**: Translate COBOL/Fortran business logic into plain English or Pseudocode.
-   **Identify Risks**: Spot `GOTO` spaghetti, hardcoded dates (Y2K style), and tight coupling.
-   **Data Mapping**: Map VSAM/Copybooks to JSON/SQL schemas.

### 2. Modernization Patterns
-   **API Wrapping (The Facade)**: Create a REST/gRPC wrapper around the legacy core.
-   **Strangler Fig**: Incrementally replace functions with microservices.
-   **Replatform**: Lift-and-shift to cloud emulators (AWS Mainframe Modernization).

### 3. Testing Legacy
-   **Characterization Tests**: "Lock down" current behavior before changing ANYTHING.
-   **Golden Master**: Capture inputs/outputs of the old system to verify the new one.

## Steps
For existing code without tests, start with `existing-project-onboarding.skill`, then `characterization-tests.skill`; follow `guides/processes/brownfield-lifecycle.md`.

1.  **Assume Importance**: If it's running, it's making money. Treat legacy code with reverence.
2.  **No Big Bang**: Never suggest a full rewrite from scratch unless the system is < 10k LOC.
3.  **Document First**: most legacy failures happen because nobody knows *what* the code does.

## Output Format
-   `legacy-analysis.md`: Explanation of flow.
-   `wrapper-api.yaml`: OpenAPI spec for the legacy system.
-   `strangler-plan.md`: Step-by-step migration path.

## Constraints
- Do no harm: pin current behaviour before changing anything.
- Document first; no full rewrite from scratch.

## Limits and safety
- Golden-master data from legacy systems usually holds live personal or financial data: mask it before it enters version control and check each file.
- Work from exports or copies; never run against production. The wrapper's service credentials come from a secret store at runtime, never from the translation layer.
- Legacy code often hides authorization checks inside business logic: list each one found and confirm the new endpoint repeats it.
- Code you do not understand goes on a "needs human review" list; do not translate it by guess.
- Changing the routing between old and new systems needs the human's approval.
