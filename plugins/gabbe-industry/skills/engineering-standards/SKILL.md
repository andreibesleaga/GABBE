---
name: engineering-standards
description: "Compliance review against ISO/IEC/IEEE 42010 and 12207, SWEBOK and the ACM Code of Ethics, written as a report. Use when a project must show conformance to IEEE, ACM or ISO standards."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/industry/engineering-standards.skill.md"
  tags: "engineering, standards, ieee, acm, iso"
  core: "false"
  context_cost: "medium"
---
# engineering-standards

## Goal
To elevate the software engineering process to meet rigorous international academic and professional standards, specifically adhering strictly to IEEE (Institute of Electrical and Electronics Engineers), ACM (Association for Computing Machinery), and ISO/IEC frameworks.

## Steps
1. **Identify the Scope**: Determine whether the agent is auditing the software's architecture (ISO/IEC/IEEE 42010), the Software Development Life Cycle (ISO/IEC 12207), or the professional ethics and requirements (ACM Code of Ethics, SWEBOK).
2. **Apply Standards**:
   - **ISO/IEC/IEEE 42010 (Architecture Description)**: Ensure the architecture explicitly documents Stakeholders, Concerns, Viewpoints, and Views, maintaining clear separation between the model and the stakeholder perspective.
   - **ISO/IEC/IEEE 12207 (Software Life Cycle)**: Verify that the process includes defined Acquisition, Supply, Development, Operation, and Maintenance processes.
   - **IEEE SWEBOK**: Guide technical decisions based on the 18 Knowledge Areas of SWEBOK V4 (e.g., Software Configuration Management, Software Quality).
   - **ACM Code of Ethics**: Ensure the system does not harm human life, respects privacy, and honors confidentiality.
3. **Output**: Generate the academic/industry compliance report using `agents/templates/industry/ENGINEERING_STANDARDS_REVIEW_TEMPLATE.md`.

## Constraints
- Findings name the standard and the clause they rest on.
- Opinions not grounded in the standard are labelled as opinions.

## Output Format
`ENGINEERING_STANDARDS_REVIEW_TEMPLATE.md` (`agents/templates/industry/`) filled in.

## Limits and safety
- Cite a standard's clause or number only from text you have read; otherwise write "unverified".
- For life-critical systems require traceability from requirement to test and code (IEEE 1012), and say that conformance needs an independent assessor.
- Assess against the published standard, not against fashion (no microservices-versus-monolith opinions unless the standard sets the constraint).
