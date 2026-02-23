---
name: legacy-modernization
description: Analyze, document, and modernize legacy systems (COBOL, Mainframe, Fortran).
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
1.  **Assume Importance**: If it's running, it's making money. Treat legacy code with reverence.
2.  **No Big Bang**: Never suggest a full rewrite from scratch unless the system is < 10k LOC.
3.  **Document First**: most legacy failures happen because nobody knows *what* the code does.

## Deliverables
-   `legacy-analysis.md`: Explanation of flow.
-   `wrapper-api.yaml`: OpenAPI spec for the legacy system.
-   `strangler-plan.md`: Step-by-step migration path.

## Security & Guardrails

### 1. Skill Security (Legacy Modernization)
- **Golden Master Secrecy**: When the agent assists in creating "Golden Master" tests (capturing inputs/outputs of the old system), it must recognize that mainframe/legacy databases often lack modern column-level encryption. The captured test fixtures will likely contain live PII or financial data. The agent must mandate strict data masking/anonymization before the Golden Master is saved to modern version control.
- **API Wrapper Credential Injection**: When implementing the "Facade/API Wrapper" (Step 2), the modern microservice often needs a highly privileged service account to interface with the legacy system (e.g., a "God Mode" DB2 user). The agent must verify this credential is injected via a secure Secret Manager at runtime, never encoded in the modernization translation layer.

### 2. System Integration Security
- **Bypass of Legacy Business Logic Guards**: Legacy systems (like COBOL programs) often intertwine business logic with security validation (e.g., checking if a user's department matches the account prefix within a massive `GOTO` loop). The agent must ensure that the new Strangler Fig endpoints replicate or improve these explicit, undocumented authorization checks, not just the "happy path" data transformation.
- **Strangler Fig Route Hijacking**: During the migration phase, the routing layer (e.g., an API Gateway) decides whether traffic goes to the Legacy or Modern system. The agent must secure this routing configuration, as unauthorized manipulation could route sensitive transactions to a partially implemented, insecure modern endpoint that lacks full auditing.

### 3. LLM & Agent Guardrails
- **Automated Refactoring Blindspots**: If the LLM is asked to translate COBOL to Python, it might drop or mistranslate "arcane" or confusing legacy logic that is actually a critical, decades-old security patch for an edge-case exploit. The agent must flag complex, misunderstood blocks for manual human review rather than guessing their intent.
- **Hallucinated Protocol Security**: The LLM might assume that integrating with a mainframe via standard TN3270 or raw socket connections is inherently secure because it's behind a firewall. The agent must advocate for securing the legacy transit layer (e.g., using IPSec or tunneling) to prevent internal lateral movement from sniffing unencrypted Mainframe traffic.
