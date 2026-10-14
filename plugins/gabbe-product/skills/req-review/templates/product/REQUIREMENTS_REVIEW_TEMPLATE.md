# Requirements Review Report — [System / Feature Name]
<!-- Created by: req-review.skill -->
<!-- Standard: IEEE 29148 / ISO/IEC 29148:2018 quality criteria -->

---

## Meta

| Field | Value |
|---|---|
| **System / Feature** | [name] |
| **Document reviewed** | [filename, version, date] |
| **Review date** | [YYYY-MM-DD] |
| **Reviewer** | [agent / human name] |
| **Scope** | [full system / feature X / module Y] |

---

## Executive Summary

**Overall Quality**: GREEN / YELLOW / RED

| Dimension | Score | Issues |
|---|---|---|
| Correct | GREEN/YELLOW/RED | N |
| Complete | GREEN/YELLOW/RED | N |
| Consistent | GREEN/YELLOW/RED | N |
| Unambiguous | GREEN/YELLOW/RED | N |
| Testable | GREEN/YELLOW/RED | N |
| Feasible | GREEN/YELLOW/RED | N |
| Necessary | GREEN/YELLOW/RED | N |
| Traceable | GREEN/YELLOW/RED | N |

**Recommendation**: [PROCEED / PROCEED WITH CONDITIONS / REWORK REQUIRED]

[2-3 sentence summary of the state of these requirements and the key action needed]

---

## Critical Findings — Must Fix Before Design Begins

| ID | Requirement ID | Criterion | Finding | Recommendation |
|---|---|---|---|---|
| RF-001 | [FR-012] | Testable | "The system shall respond quickly" — no measurable threshold | Change to: "WHEN [actor] performs [action], the system SHALL respond within [N]ms" |
| RF-002 | | Complete | No requirements for error handling of [scenario] | Add requirements for: [specific missing scenario] |
| RF-003 | | Consistent | FR-007 and FR-019 contradict: FR-007 requires X but FR-019 requires not-X | Resolve by: [resolution approach] |

---

## Minor Findings — Should Fix

| ID | Requirement ID | Criterion | Finding | Recommendation |
|---|---|---|---|---|
| RF-010 | [FR-045] | Unambiguous | "Appropriate notification" — what counts as appropriate? | Define notification types and timing explicitly |
| RF-011 | | Necessary | This requirement appears to be an implementation decision, not a need | Rephrase as a capability need, or remove if truly an implementation detail |

---

## EARS Compliance Issues

| Requirement ID | Current Text | Issue | Suggested EARS Rewrite |
|---|---|---|---|
| [FR-003] | "Users should be able to log in" | No trigger, no "shall", subject is "users" | "WHEN an unauthenticated user submits valid credentials, the system SHALL grant a session token" |
| [FR-007] | "The system must handle errors" | Vague — what errors? what handling? | Split into specific unwanted behavior scenarios |

**EARS Compliance Rate**: [N]% of requirements comply with EARS format

---

## Coverage Analysis

### Missing Functional Requirements

| Area | Missing Coverage | Risk if Missing |
|---|---|---|
| [Error handling] | [No requirements for [specific failure mode]] | [System behavior undefined; inconsistent implementation likely] |
| [Admin functions] | [No requirements for [admin capability]] | [Administrators have no defined workflow] |
| [Integration] | [Integration with [system X] has no requirements] | [Interface may be incompatible] |

### Missing Quality Requirements

| Quality Attribute | Current Status | Recommendation |
|---|---|---|
| Performance | [Only latency specified; no throughput or capacity] | Add: concurrent user load, data volume expectations |
| Reliability | [No availability target defined] | Add: availability SLO, recovery time objective |
| Security | [Authentication mentioned but no authorization] | Add: role-based access control requirements |

### Missing Constraint Documentation

| Constraint Type | Status |
|---|---|
| Technical constraints | [PRESENT / MISSING] |
| Regulatory constraints | [PRESENT / MISSING — specify which regulations apply] |
| Resource constraints | [PRESENT / MISSING] |
| Integration constraints | [PRESENT / MISSING] |

---

## Consistency Issues

| Conflict | Requirement A | Requirement B | Nature of conflict | Resolution |
|---|---|---|---|---|
| C-001 | FR-007 | FR-019 | [Data field X required in FR-007, optional in FR-019] | [Resolve by making X always required, update FR-019] |

---

## Ambiguity Catalog

| Requirement | Ambiguous Term | Interpretations | Clarification Needed |
|---|---|---|---|
| [FR-012] | "user-friendly" | [Interpretation A / Interpretation B] | Measurable usability criterion |
| [FR-045] | "fast" | [< 100ms / < 1s / < 5s?] | Specific response time threshold |
| [FR-067] | "secure" | [Encrypted? Auth required? Both?] | Explicit security controls list |

---

## Traceability Assessment

### Forward Traceability (stakeholder → requirement)

| Stakeholder | Goal | Covered by Requirements | Status |
|---|---|---|---|
| [Customer] | [Complete order in < 3 minutes] | [FR-001, FR-002, FR-003] | COVERED |
| [Admin] | [View all orders] | [None found] | MISSING |

### Backward Traceability (requirement → verification)

| Requirement | Verification Method | Status |
|---|---|---|
| FR-001 | Automated acceptance test | DEFINED |
| FR-045 | Performance load test | DEFINED |
| FR-067 | Security penetration test | MISSING — no verification method defined |

**Traceability completeness**: [N]% of requirements have defined verification methods

---

## Requirements Statistics

| Metric | Value |
|---|---|
| Total requirements | [N] |
| Functional requirements | [N] |
| Non-functional / quality requirements | [N] |
| Constraints | [N] |
| EARS-compliant | [N] ([%]) |
| Requirements with unique IDs | [N] ([%]) |
| Requirements with priority (MoSCoW) | [N] ([%]) |
| Requirements with verification method | [N] ([%]) |

---

## Recommendations (Ordered by Priority)

1. **[CRITICAL]** Resolve consistency conflict C-001 between FR-007 and FR-019 — architect cannot proceed until this is resolved.
2. **[HIGH]** Add measurable performance requirements — current "fast" and "quickly" terms make testing impossible.
3. **[HIGH]** Add requirements for error handling in [missing areas] — undefined behavior creates implementation risk.
4. **[MEDIUM]** Convert all requirements to EARS format — improves testability and removes ambiguity.
5. **[LOW]** Add MoSCoW priority to all requirements — enables better scope decisions during implementation.

---

## Approval Gate

**For architecture to begin, the following must be true:**

- [ ] All CRITICAL findings resolved (RF-001, RF-002, RF-003)
- [ ] All consistency conflicts resolved (C-001)
- [ ] Missing functional areas have requirements OR are explicitly out-of-scope
- [ ] All MUST-level requirements are testable
- [ ] Stakeholder sign-off obtained for CRITICAL finding resolutions

**Gate decision**: [APPROVED / BLOCKED — list what blocks] by [human name / date]
