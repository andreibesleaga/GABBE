# PRD: [Feature Name]
<!-- Product Requirements Document — fill all sections before starting design -->
<!-- Created by: spec-writer.skill | Approved by: [human name] | Date: [date] -->

---

## 1. Feature Summary

**What:** [One sentence describing the feature]
**Why:** [The problem it solves — tie to user pain or business goal]
**Who:** [Who benefits — user role, customer segment]
**Success metric:** [How will we know this feature succeeds? e.g., "Checkout abandonment drops 15%"]

---

## 2. Problem Statement

[2-4 sentences describing the current situation and what's broken or missing.
Include: who is affected, how often, what the impact is.]

**Current behavior:** [What happens today]
**Desired behavior:** [What should happen after this feature]

---

## 3. User Stories

<!-- Format: As a [role], I want to [action], so that [benefit] -->

- As a **[role]**, I want to **[action]**, so that **[benefit]**.
- As a **[role]**, I want to **[action]**, so that **[benefit]**.
- As a **[role]**, I want to **[action]**, so that **[benefit]**.

---

## 4. EARS Requirements

<!-- Use EARS syntax. Each requirement must be verifiable (no "should", "might", "fast") -->

### 4.1 Ubiquitous Requirements (always applies)
```
THE SYSTEM SHALL [requirement].
```

### 4.2 Event-Driven Requirements (triggered by an event)
```
WHEN [trigger event]
THE SYSTEM SHALL [response].
```

### 4.3 State-Driven Requirements (while in a state)
```
WHILE [system state]
THE SYSTEM SHALL [behavior].
```

### 4.4 Optional Feature Requirements (feature flags)
```
WHERE [feature is enabled/condition is true]
THE SYSTEM SHALL [behavior].
```

### 4.5 Unwanted Behaviors (negative requirements)
```
THE SYSTEM SHALL NOT [forbidden behavior].
```

---

## 5. Acceptance Criteria

<!-- Each criterion: testable, atomic, pass/fail — one per requirement -->

| ID | Given | When | Then |
|---|---|---|---|
| AC-01 | User is logged in | User clicks "Submit" with valid data | System creates record and returns 201 |
| AC-02 | User is not authenticated | User attempts to access /api/protected | System returns 401 |
| AC-03 | Form has invalid email | User submits | System returns 422 with field-level error |

---

## 6. Data Model (Sketch)

<!-- Rough entity diagram — full schema in SPEC_TEMPLATE.md -->

```
Entity: [Name]
Fields:
  id:          uuid (primary key)
  [field]:     [type] ([constraints: required, unique, max length])
  created_at:  timestamp
  updated_at:  timestamp

Relationships:
  [Entity] has many [Entity]
  [Entity] belongs to [Entity]
```

---

## 7. API Surface (Sketch)

<!-- Rough API design — full contract in SPEC_TEMPLATE.md and docs/api/openapi.yaml -->

```
POST   /api/v1/[resource]           Create
GET    /api/v1/[resource]           List (with pagination)
GET    /api/v1/[resource]/{id}      Get one
PATCH  /api/v1/[resource]/{id}      Partial update
DELETE /api/v1/[resource]/{id}      Delete
```

---

## 8. UI/UX Notes

<!-- Link to Figma if designs exist, or describe the UI behavior -->

**Designs:** [Link to Figma / wireframe / mockup]

**Key interactions:**
- [What happens when the user does X]
- [Error state display]
- [Loading state]
- [Empty state]

**Accessibility requirements:**
- WCAG 2.2 Level AA compliance required
- [any specific a11y requirements for this feature]

---

## 9. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | API responses < [X]ms at p99 under [Y] concurrent users |
| **Availability** | [X]% uptime SLO |
| **Security** | [Authentication required / Rate limited at X req/min / Data encrypted] |
| **Scalability** | Must handle [X] records / [Y] concurrent users |
| **Accessibility** | WCAG 2.2 Level AA |
| **Browser Support** | [Modern browsers / IE11 / Mobile Safari] |
| **Internationalization** | [All text in i18n system / English only] |

---

## 10. Security & Privacy Considerations

**Data classification:** [Public / Internal / Confidential / Restricted]

**PII involved?** [Yes/No — if yes, list what PII and how it will be protected]

**Threat model required?** [Yes — for auth/payment/data storage / No]

**Regulatory compliance:** [GDPR / HIPAA / PCI-DSS / None]

**Authentication required:** [Yes/No]

**Authorization rules:** [Who can read/write/delete this data]

---

## 11. Out of Scope (v1)

<!-- Explicitly list what this version does NOT include — prevents scope creep -->

- [Feature X will not be included in this version]
- [Mobile app support deferred to v2]
- [Bulk import functionality is out of scope]

**Future considerations (v2+):**
- [Item that may be added in a future version]

---

## 12. Open Questions

<!-- Track unresolved questions — must be resolved before design phase -->

| # | Question | Owner | Resolution |
|---|---|---|---|
| 1 | [Question] | [person] | [OPEN / answer] |
| 2 | [Question] | [person] | [OPEN / answer] |

---

## 13. Approval

| Role | Name | Status | Date |
|---|---|---|---|
| Product | [name] | [APPROVED / PENDING] | [date] |
| Engineering | [name] | [APPROVED / PENDING] | [date] |
| Security | [name] | [APPROVED / PENDING] | [date] |

**Human approval required before proceeding to Design phase (S02).**
