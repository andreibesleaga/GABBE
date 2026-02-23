# IEEE, ACM, & ISO Engineering Standards Guide

## 1. Introduction
While Agile methodologies revolutionized the speed of software delivery, the foundational bedrock of Computer Science and Software Engineering is defined by global bodies such as the **IEEE** (Institute of Electrical and Electronics Engineers), the **ACM** (Association for Computing Machinery), and the **ISO** (International Organization for Standardization).

Incorporating these standards elevates software from a "startup hack" to an academically and industrially verified engineered system.

## 2. ISO/IEC/IEEE 42010 (Architecture Description)
This standard defines how system architectures should be communicated. The GABBE kit is fundamentally aligned with this standard.
- **Architectures vs. Architecture Descriptions**: The architecture is the system itself; the AD is the artifact (like a C4 model).
- **Stakeholders & Concerns**: Every diagram or document must exist to address a specific concern (e.g., Security, Performance) held by a specific Stakeholder (e.g., the CISO, the End User).
- **Viewpoints & Views**: A viewpoint is the *rules* for the diagram (e.g., "UML Sequence Diagram rules"). A view is the actual diagram applied to your system.

## 3. ISO/IEC/IEEE 12207 (Software Life Cycle Processes)
This is the international standard for software lifecycle processes. It defines all tasks required for developing and maintaining software.
- It moves beyond just "coding" to emphasize formal **Verification** (Are we building the product right?) and **Validation** (Are we building the right product?).
- It strongly mandates rigorous Software Configuration Management (SCM)—meaning every requirement, test case, code change, and deployment manifest must be rigidly version-controlled and traceable.

## 4. IEEE SWEBOK (Software Engineering Body of Knowledge)
Compiled by the IEEE Computer Society, SWEBOK defines the 15 Knowledge Areas (KAs) that a professional software engineer must understand.
When building systems in GABBE, agents will cross-reference architectural decisions against SWEBOK categories, particularly:
- **KA 2: Software Design** (Enforcing cohesion and minimizing coupling)
- **KA 4: Software Testing** (Unit, Integration, and System testing boundaries)
- **KA 10: Software Quality** (Static analysis, metrics, and technical debt measurement)

## 5. ACM Code of Ethics and Professional Conduct
Software engineering has profound societal impacts. The ACM Code is the Hippocratic Oath of software developers.
1. **Contribute to society and human well-being**, acknowledging that all people are stakeholders in computing.
2. **Avoid harm**, taking action to prevent unintended consequences.
3. **Be honest and trustworthy**, preventing deception in UX architectures (e.g., Dark Patterns).
4. **Respect privacy and honor confidentiality**.

## 6. Agentic Implementation
If your project is mission-critical, requires academic publication, or is being audited by a heavily regulated body (e.g., Aviation, Defense, Healthcare), invoke the `engineering-standards` skill.

The agent will systematically audit your codebase, design documentation, and CI/CD pipelines against these frameworks, producing an `ENGINEERING_STANDARDS_REVIEW_TEMPLATE.md` to prove standard compliance.
