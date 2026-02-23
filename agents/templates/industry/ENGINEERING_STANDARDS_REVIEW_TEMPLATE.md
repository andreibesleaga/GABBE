# IEEE, ACM & ISO Engineering Standards Review

**Project/System Name:** [System Name]
**Target Standard(s):** [e.g., ISO/IEC 12207, IEEE 42010, ACM Ethics]
**Date:** [YYYY-MM-DD]
**Auditing Agent:** [Agent Name]

## 1. Architecture Description Verification (ISO/IEC/IEEE 42010)
*Evaluates if the architecture is formally documented according to global engineering standards.*

| Requirement | Evidence in Project | Status (Pass/Fail) |
| :--- | :--- | :--- |
| **Stakeholders Identified** | [Who cares about this architecture?] | |
| **Concerns Documented** | [What are the NFRs, risks, and goals?] | |
| **Viewpoints Selected** | [e.g., Logical, Physical, Process views] | |
| **Views Created** | [Are the diagrams present that conform to the Viewpoints?] | |
| **Rationale Documented** | [Are ADRs stored locally? See `adr-writer.skill.md`] | |

## 2. Software Life Cycle Processes (ISO/IEC/IEEE 12207)
*Evaluates if the SDLC is mature, predictable, and measurable.*

- **Requirements Analysis**: Are requirements unambiguously documented? (SWEBOK KA: Software Requirements)
- **Software Construction**: Is there a defined coding standard applied via CI/CD linting? (SWEBOK KA: Software Construction)
- **Software Configuration Management**: Are all artifacts (code, docs, tests) version-controlled? (SWEBOK KA: SCM)
- **Software Quality**: Is test-driven development or high-coverage test automation enforced? (SWEBOK KA: Software Quality)

## 3. ACM Code of Ethics and Professional Conduct
*The moral and ethical implications of the software.*

### 3.1 Contribute to Society and Human Well-being
- Does the system respect the rights of all end-users? [Evaluate accessibility and inclusion]
- Does the software algorithm minimize bias? [Identify any ML/AI decision-making logic]

### 3.2 Avoid Harm
- **Data Privacy**: Are user telemetry and PII securely hashed/encrypted? [Check against `privacy-data-protection.skill.md`]
- **System Failure Contingency**: If this system goes offline, what is the human impact? [Evaluate failover states]

### 3.3 Honor Confidentiality
- Does the system employ Principle of Least Privilege (PoLP) for internal access?

## 4. Specific Technical Standards (If Applicable)
- **IEEE 754 (Floating-Point Arithmetic)**: [If building a financial or scientific system, verify that decimal rounding is not prone to floating-point truncation errors. Use `BigDecimal` or equivalent safe types.]
- **IEEE 1012 (Verification and Validation)**: [Is there a formal Traceability Matrix linking Code -> Tests -> Requirements?]
