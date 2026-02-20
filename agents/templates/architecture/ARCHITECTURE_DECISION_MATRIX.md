# Architecture Decision Matrix — [Decision Title]
<!-- Weighted multi-criteria decision matrix for comparing architecture options -->
<!-- Created by: arch-design.skill, adr-writer.skill -->
<!-- Use when: choosing between 2+ viable architectural approaches -->
<!-- One matrix per major decision. Reference from ADR. -->

---

## Meta

| Field | Value |
|---|---|
| **Decision** | [Clear decision statement: "Which architecture style to use for X"] |
| **Date** | [YYYY-MM-DD] |
| **Author** | [agent / human] |
| **Status** | DRAFT / DECIDED |
| **ADR reference** | [ADR-NNN] |

---

## Decision Context

**Problem statement**: [What specific problem are we solving with this architectural decision?]

**Constraints** (non-negotiable — options violating these are eliminated):
- [Constraint 1: e.g., Must support 10k concurrent users without vertical scaling]
- [Constraint 2: e.g., Must integrate with existing [system] via [protocol]]
- [Constraint 3: e.g., Must be operable by a team of ≤ 3 engineers]

**Assumptions** (things we're taking as true — document to revisit later):
- [Assumption 1: e.g., User growth will not exceed 100x current load in 2 years]
- [Assumption 2: e.g., Team has familiarity with event-driven patterns]

---

## Options Considered

| Option | Short Description | Eliminated? (and why) |
|---|---|---|
| Option A | [e.g., Layered monolith] | NO — viable |
| Option B | [e.g., Event-driven service-based] | NO — viable |
| Option C | [e.g., Full microservices] | YES — violates Constraint 3 (team size) |
| Option D | [e.g., Serverless] | YES — violates Constraint 2 (integration protocol) |

**Options proceeding to evaluation**: Option A, Option B

---

## Evaluation Criteria

Define criteria that matter for this specific decision.
Assign weight (1-5) based on which quality attributes are most important for this system.

| # | Criterion | Why it matters | Weight (1-5) |
|---|---|---|---|
| C1 | [Operational simplicity] | [Small team — operations complexity is a key risk] | 5 |
| C2 | [Scalability] | [System must handle 10x growth] | 4 |
| C3 | [Development velocity] | [Team needs to ship features frequently] | 4 |
| C4 | [Fault isolation] | [Failure in one area must not cascade] | 3 |
| C5 | [Data consistency] | [Financial data must be consistent] | 5 |
| C6 | [Cost to implement] | [Limited budget for initial build] | 3 |
| C7 | [Team familiarity] | [Learning curve has real cost] | 2 |

**Scoring scale**: 1 (very poor) → 5 (excellent) for each criterion.

---

## Decision Matrix

| Criterion | Weight | Option A Score | Option A Weighted | Option B Score | Option B Weighted |
|---|---|---|---|---|---|
| C1 — Operational simplicity | 5 | 5 | **25** | 3 | **15** |
| C2 — Scalability | 4 | 3 | **12** | 5 | **20** |
| C3 — Development velocity | 4 | 4 | **16** | 3 | **12** |
| C4 — Fault isolation | 3 | 2 | **6** | 4 | **12** |
| C5 — Data consistency | 5 | 5 | **25** | 3 | **15** |
| C6 — Cost to implement | 3 | 4 | **12** | 2 | **6** |
| C7 — Team familiarity | 2 | 5 | **10** | 2 | **4** |
| **TOTAL** | | | **106** | | **84** |

---

## Qualitative Analysis

### Option A: [Name]

**Pros:**
- [Strength 1]
- [Strength 2]
- [Strength 3]

**Cons:**
- [Weakness 1]
- [Weakness 2]

**Key risk**: [What is the biggest risk if we choose this option?]

**Reversibility**: HIGH / MEDIUM / LOW
[How easy is it to change this decision later if it proves wrong?]

---

### Option B: [Name]

**Pros:**
- [Strength 1]
- [Strength 2]

**Cons:**
- [Weakness 1]
- [Weakness 2]

**Key risk**: [What is the biggest risk if we choose this option?]

**Reversibility**: HIGH / MEDIUM / LOW

---

## Sensitivity Analysis

```
Which criteria, if weighted differently, would change the outcome?

If C2 (Scalability) weight = 5 instead of 4:
  Option A total: [recalculate]
  Option B total: [recalculate]
  Winner changes? YES/NO

If C1 (Operational simplicity) weight = 3 instead of 5:
  Option A total: [recalculate]
  Option B total: [recalculate]
  Winner changes? YES/NO

Conclusion:
  The decision is ROBUST — winner stays the same across weight variations.
  OR
  The decision is SENSITIVE to [C2] weighting — human must confirm priority.
```

---

## Decision

**Recommended option**: [Option A / Option B]
**Based on**: [weighted score + key qualitative factors]

**Rationale** (beyond the numbers):
[2-3 sentences explaining the decision in human-readable terms, focusing on the most important factors]

**Specific conditions on the decision**:
- [Condition 1: e.g., Re-evaluate if team grows beyond 10 engineers]
- [Condition 2: e.g., Re-evaluate if user growth exceeds 50x]

**Accepted risks**:
- [Risk 1: e.g., Scaling beyond 10x will require architectural rework — accepted for now]

---

## Decision Sign-off

| Role | Name | Date | Approved |
|---|---|---|---|
| [Architect / Tech Lead] | | [YYYY-MM-DD] | [ ] |
| [Product Owner] | | [YYYY-MM-DD] | [ ] |
| [Engineering Manager] | | [YYYY-MM-DD] | [ ] |

---

**Linked ADR**: [ADR-NNN — write full ADR using adr-writer.skill referencing this matrix]
