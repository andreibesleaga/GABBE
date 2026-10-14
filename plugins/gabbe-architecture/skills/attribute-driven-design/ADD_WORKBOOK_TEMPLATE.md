# Attribute-Driven Design (ADD 3.0) Workbook: [System Name]

**Date:** [YYYY-MM-DD]
**Architect(s):** [names or roles]
**Status:** Draft | In progress | Complete

<!-- ADD 3.0 is an iterative, step-driven design method. You loop over design
     rounds; each round refines one element of the system against the most
     important drivers. Capture every round below. -->

---

## 1. Inputs (Design Drivers)

### 1.1 Functional Requirements
| ID | Requirement | Priority |
|---|---|---|
| F-1 | [What the system must do] | [H/M/L] |
| F-2 | [ ] | [ ] |

### 1.2 Quality-Attribute Scenarios
<!-- Format each scenario as: Source -> Stimulus -> Artifact -> Environment -> Response -> Response Measure. -->

| ID | Quality attribute | Scenario (stimulus → response → measure) | Priority (business × difficulty) |
|---|---|---|---|
| QA-1 | [e.g. Performance] | [e.g. "Under peak load, a request returns in < 200ms p99"] | [H/H] |
| QA-2 | [ ] | [ ] | [ ] |

### 1.3 Constraints
| ID | Constraint | Type (technical/business) |
|---|---|---|
| C-1 | [Non-negotiable, e.g. "Must run on existing K8s cluster"] | [ ] |
| C-2 | [ ] | [ ] |

---

## 2. Design Rounds

> Duplicate this block for each design round.

### Round [N]

**2.1 Design purpose:** [What this round aims to achieve — e.g. "Decompose the system into top-level modules."]

**2.2 Element(s) to refine / decompose:** [Which element from the previous round are we elaborating? For Round 1 this is usually "the system."]

**2.3 Drivers addressed this round:** [List the QA-/F-/C- IDs prioritized here and why.]

**2.4 Chosen tactics & patterns:**
| Driver addressed | Tactic / pattern selected | Alternatives rejected | Rationale |
|---|---|---|---|
| [QA-1] | [e.g. Caching, CQRS, Bulkhead] | [ ] | [ ] |

**2.5 Instantiated elements & responsibilities:**
| Element | Responsibility | Interfaces / dependencies |
|---|---|---|
| [Module/service/component] | [ ] | [ ] |

**2.6 Views sketch:** [Textual or Mermaid-style sketch of the structure produced this round — module view, C&C view, or deployment view.]

```
[ component diagram / box-and-line sketch here ]
```

**2.7 Decisions & ADR references:** [Link decisions made this round to their `ADR_TEMPLATE` records by ADR number.]

**2.8 Analysis vs drivers:**
| Driver | Satisfied? | Evidence / residual risk |
|---|---|---|
| [QA-1] | [Yes/Partial/No] | [How we know; what's left to validate] |

**2.9 Not-yet-addressed drivers (carried to next round):** [List.]

---

## 3. Exit Check

- [ ] All high-priority drivers addressed or explicitly deferred with rationale.
- [ ] Each design round records tactics, elements, a view, and an analysis.
- [ ] Key decisions captured as ADRs.
- [ ] Residual risks logged for the next iteration.
