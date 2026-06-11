---
name: engineering-standards
description: Enforce academic and industry engineering standards (IEEE, ACM, ISO/IEC)
triggers: [ieee standards, acm compliance, iso 12207, swebok, academic standards, ieee 42010]
tags: [engineering, standards, ieee, acm, iso]
context_cost: medium
---
# engineering-standards

## Goal
To elevate the software engineering process to meet rigorous international academic and professional standards, specifically adhering strictly to IEEE (Institute of Electrical and Electronics Engineers), ACM (Association for Computing Machinery), and ISO/IEC frameworks.

## Steps
1. **Identify the Scope**: Determine whether the agent is auditing the software's architecture (ISO/IEC/IEEE 42010), the Software Development Life Cycle (ISO/IEC 12207), or the professional ethics and requirements (ACM Code of Ethics, SWEBOK).
2. **Apply Standards**:
   - **ISO/IEC/IEEE 42010 (Architecture Description)**: Ensure the architecture explicitly documents Stakeholders, Concerns, Viewpoints, and Views, maintaining clear separation between the model and the stakeholder perspective.
   - **ISO/IEC/IEEE 12207 (Software Life Cycle)**: Verify that the process includes defined Acquisition, Supply, Development, Operation, and Maintenance processes.
   - **IEEE SWEBOK**: Guide technical decisions based on the 15 Knowledge Areas (e.g., Software Configuration Management, Software Quality).
   - **ACM Code of Ethics**: Ensure the system does not harm human life, respects privacy, and honors confidentiality.
3. **Output**: Generate the academic/industry compliance report using `agents/templates/industry/ENGINEERING_STANDARDS_REVIEW_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **Strict Citation**: The agent must not hallucinate standard clauses. If referencing a specific IEEE standard (e.g., IEEE 754 for floating-point arithmetic), the agent must cite its specific constraints accurately to prevent academic or catastrophic financial/scientific calculation errors.

### 2. System Integration Security
- **Safety Criticality**: When applying these standards to life-critical systems (like medical devices or avionics), the agent must enforce the highest rigor of traceability (linking every line of code back to a formal requirement as per IEEE 1012 V&V standards).

### 3. LLM & Agent Guardrails
- **Academic Neutrality**: The LLM must assess architectures neutrally against the published standard, avoiding trend-based opinions (e.g., not strictly favoring Microservices over Monoliths unless the standard specifically dictates a scaling constraint).
