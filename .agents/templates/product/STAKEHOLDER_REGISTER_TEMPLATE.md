# Stakeholder Register — [System Name]
<!-- Created by: req-elicitation.skill or prod-pm persona -->
<!-- Referenced by: PRD.md, ARCHITECTURE_REVIEW_TEMPLATE.md -->
<!-- Update when: new stakeholders identified, roles change, concerns evolve -->

---

## Meta

| Field | Value |
|---|---|
| **System / Feature** | [system or feature name] |
| **Version** | [1.0] |
| **Date** | [YYYY-MM-DD] |
| **Author** | [agent/human] |

---

## Stakeholder Categories

```
Direct Users:     People who directly operate or use the system
Indirect Users:   People affected by system outputs without operating it
System Owners:    People accountable for the system's existence and funding
External Systems: Other systems (automated actors) that integrate
Regulators:       Authorities with compliance requirements over the system
```

---

## Stakeholder Register

| ID | Name / Role | Category | Goals | Concerns | Influence | Interest | Communication |
|---|---|---|---|---|---|---|---|
| SH-001 | [Role name e.g. "End Customer"] | Direct User | [What they want to achieve] | [What they fear or care about most] | H/M/L | H/M/L | [How/when to communicate with them] |
| SH-002 | [Role name e.g. "Operations Team"] | Direct User | | | | | |
| SH-003 | [Role name e.g. "Product Owner"] | System Owner | | | | | |
| SH-004 | [External system name] | External System | | | | | |
| SH-005 | [Regulatory body] | Regulator | | | | | |

**Influence**: How much can they change system direction?
**Interest**: How affected are they by system outcomes?

---

## Stakeholder Engagement Matrix

```
High Interest + High Influence → MANAGE CLOSELY (primary stakeholders)
High Interest + Low Influence  → KEEP INFORMED
Low Interest  + High Influence → KEEP SATISFIED
Low Interest  + Low Influence  → MONITOR (minimal effort)
```

| Stakeholder | Interest | Influence | Engagement Strategy |
|---|---|---|---|
| [SH-001] | H | H | MANAGE CLOSELY — weekly updates, approval gates |
| [SH-002] | H | L | KEEP INFORMED — bi-weekly reports |
| [SH-003] | L | H | KEEP SATISFIED — milestone reviews |

---

## Stakeholder Concerns Catalog

For each primary stakeholder, document their key concerns:

### SH-001: [Role Name]

**Goals:**
- [Primary objective 1]
- [Primary objective 2]

**Concerns / Fears:**
- [What they're afraid the system will do wrong]
- [What risks worry them]

**Success Criteria:**
- [How this stakeholder knows the system succeeded]
- [Measurable: "Order confirmation received within 30 seconds"]

**Required Consultations:**
- [Phase S01 requirements approval]
- [Phase S08 final review]

---

### SH-002: [Role Name]

**Goals:**
-

**Concerns / Fears:**
-

**Success Criteria:**
-

**Required Consultations:**
-

<!-- Repeat for each primary stakeholder (Influence=H or Interest=H) -->

---

## Conflicting Concerns

Document any stakeholder concerns that conflict with each other:

| Conflict | SH-A concern | SH-B concern | Resolution approach |
|---|---|---|---|
| [Conflict 1] | [SH-001 wants X] | [SH-003 wants not-X] | [How to resolve or escalate] |

---

## Stakeholder Sign-off Requirements

| Phase Gate | Required Sign-off | Stakeholder |
|---|---|---|
| S01 — Requirements | Approval of PRD.md | [SH-001, SH-003] |
| S02 — Architecture | Approval of PLAN.md | [SH-003] |
| S08 — Human Review | Final code/product review | [SH-003] |

---

## Notes

[Any additional context about stakeholders, organizational dynamics, or communication constraints]
