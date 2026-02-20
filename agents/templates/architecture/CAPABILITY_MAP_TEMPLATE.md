# Business Capability Map — [Organization / System Name]
<!-- Business capability model: what the business/system CAN DO, independent of how -->
<!-- Technology-agnostic. No implementation, no process, no org structure. -->
<!-- Created by: req-elicitation.skill or arch-design.skill -->
<!-- Use to: identify system scope, find bounded contexts, prioritize investment -->

---

## Meta

| Field | Value |
|---|---|
| **Organization / System** | [name] |
| **Scope** | [full org / product line / specific system] |
| **Version** | [1.0] |
| **Date** | [YYYY-MM-DD] |
| **Status** | DRAFT / APPROVED |

---

## What is a Business Capability?

```
A business capability defines WHAT a business does — not HOW it does it.
It is stable: capabilities don't change when technology changes or org restructures.

Good capability: "Order Management" (stable — always needed)
Bad example:     "SAP Order Processing" (implementation — changes with tools)
Bad example:     "Order Processing Team" (org structure — changes with reorgs)

Capabilities are hierarchical:
  Level 1: Major capability areas (coarsest granularity — 5-15 total)
  Level 2: Sub-capabilities within each L1 (15-50 total)
  Level 3: Specific capabilities within each L2 (50-200 total — as needed)
```

---

## Capability Map

```
Color coding for investment priority:
  ⬛ RED:    Pain area — immediate investment needed
  🟨 YELLOW: Adequate — maintain, no major investment
  🟩 GREEN:  Differentiating — competitive advantage, invest further
  ⬜ WHITE:  Not assessed
```

### Level 1 — Major Capability Areas

```
[System/Org Name] Business Capabilities

┌─────────────────────────────────────────────────────────────────────────┐
│  1. CUSTOMER MANAGEMENT    │  2. PRODUCT & CATALOG    │  3. ORDER MGMT  │
├─────────────────────────────────────────────────────────────────────────┤
│  4. FULFILLMENT            │  5. PAYMENT & FINANCE    │  6. ANALYTICS   │
├─────────────────────────────────────────────────────────────────────────┤
│  7. [CAPABILITY AREA]      │  8. [CAPABILITY AREA]    │  9. ...         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Capability Hierarchy (Detailed)

### 1. [Capability Area Name — e.g., Customer Management]

**Purpose**: [What business outcome this capability area enables]

| L2 Capability | L3 Capabilities | Priority | Investment Status | Bounded Context |
|---|---|---|---|---|
| 1.1 [Customer Acquisition] | 1.1.1 Registration, 1.1.2 Onboarding, 1.1.3 Identity Verification | HIGH | 🟨 Adequate | [Identity Context] |
| 1.2 [Customer Retention] | 1.2.1 Loyalty Programs, 1.2.2 Communication Preferences | MEDIUM | ⬛ Pain area | [CRM Context] |
| 1.3 [Customer Data Management] | 1.3.1 Profile Mgmt, 1.3.2 Consent Management, 1.3.3 Data Portability | HIGH | 🟨 Adequate | [Identity Context] |

---

### 2. [Capability Area Name — e.g., Order Management]

**Purpose**: [What business outcome this capability area enables]

| L2 Capability | L3 Capabilities | Priority | Investment Status | Bounded Context |
|---|---|---|---|---|
| 2.1 [Order Capture] | 2.1.1 Cart Management, 2.1.2 Order Placement, 2.1.3 Order Validation | HIGH | 🟩 Differentiating | [Order Context] |
| 2.2 [Order Processing] | 2.2.1 Fulfilment Routing, 2.2.2 Status Tracking, 2.2.3 Exception Handling | HIGH | ⬛ Pain area | [Order Context] |
| 2.3 [Order Modification] | 2.3.1 Cancellation, 2.3.2 Returns, 2.3.3 Exchanges | MEDIUM | 🟨 Adequate | [Order Context] |

---

### 3. [Capability Area Name]

| L2 Capability | L3 Capabilities | Priority | Investment Status | Bounded Context |
|---|---|---|---|---|
| | | | | |

---

<!-- Add one section per L1 capability area -->

---

## Capability Assessment

### Pain Areas (Immediate Investment Needed)

| Capability | Current Problem | Business Impact | Recommended Action |
|---|---|---|---|
| [1.2 Customer Retention] | [No loyalty program infrastructure] | [HIGH — customer churn 30% above industry] | [Build v1 loyalty capability in Q2] |
| [2.2 Order Processing] | [Manual exception handling] | [MEDIUM — 15% of orders need manual intervention] | [Automate exception routing] |

### Differentiating Capabilities (Competitive Advantage — Invest)

| Capability | Why Differentiating | Investment Recommendation |
|---|---|---|
| [2.1 Order Capture] | [Unique UX reduces cart abandonment by 40%] | [Continue R&D investment; protect IP] |

### Generic Capabilities (Buy/SaaS — Don't Build)

| Capability | Current Status | Recommendation |
|---|---|---|
| [Email Delivery] | [Built in-house] | [Replace with SaaS (e.g., transactional email service)] |
| [Payment Processing] | [Using gateway already] | [Keep on SaaS — do not internalize] |

---

## Capability-to-System Mapping

> Which systems currently serve each capability? Identifies gaps and overlaps.

| Capability | Current System(s) | Status |
|---|---|---|
| [Customer Registration] | [Current Auth System] | COVERED |
| [Customer Consent Management] | [None] | GAP — not implemented |
| [Order Placement] | [Legacy Order System + this new system] | OVERLAP — duplication |

---

## Capability Investment Roadmap

Based on pain areas and strategic priorities:

| Quarter | Capability | Investment Type | Expected Outcome |
|---|---|---|---|
| Q1 | [2.2 Order Processing] | Improve | [Reduce manual intervention from 15% to 3%] |
| Q2 | [1.2 Customer Retention] | Build | [Launch basic loyalty program] |
| Q3 | [3.x New capability] | Build | [Enable [business outcome]] |

---

## Notes

[Any additional context about the capability landscape, strategic context, or pending decisions]
