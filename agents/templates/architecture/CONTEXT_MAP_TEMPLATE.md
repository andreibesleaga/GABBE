# Context Map — [System Name]
<!-- Domain bounded contexts and their integration relationships -->
<!-- Created by: domain-model.skill -->
<!-- Standard: Domain-Driven Design (Eric Evans), Implementing DDD (Vaughn Vernon) -->
<!-- Referenced by: ARCHITECTURE_VIEWS_TEMPLATE.md, DOMAIN_MODEL_TEMPLATE.md -->

---

## Meta

| Field | Value |
|---|---|
| **System** | [system name] |
| **Version** | [1.0] |
| **Date** | [YYYY-MM-DD] |
| **Status** | DRAFT / APPROVED |

---

## Bounded Context Inventory

| Context ID | Name | Description | Team/Owner | Stability |
|---|---|---|---|---|
| BC-01 | [Context Name] | [What business capability this context encapsulates] | [Team] | [STABLE/EVOLVING/LEGACY] |
| BC-02 | | | | |
| BC-03 | | | | |
| BC-04 | | | | |

---

## Context Map Diagram

```mermaid
graph TB
    subgraph "BC-01: [Context Name] [U]"
        BC01[[BC-01\n[Context Name]]]
    end
    subgraph "BC-02: [Context Name] [U]"
        BC02[[BC-02\n[Context Name]]]
    end
    subgraph "BC-03: [Context Name] [D]"
        BC03[[BC-03\n[Context Name]]]
    end
    subgraph "BC-04: [Context Name] [D]"
        BC04[[BC-04\n[Context Name]]]
    end

    BC01 -->|"OHS/PL\n[API name]"| BC03
    BC02 -->|"Customer/Supplier\n[data shared]"| BC03
    BC01 -->|"Partnership\n[shared model]"| BC02
    BC01 -->|"Published Language\n[event name]"| BC04

    style BC01 fill:#d5e8d4,stroke:#82b366
    style BC02 fill:#dae8fc,stroke:#6c8ebf
    style BC03 fill:#fff2cc,stroke:#d6b656
    style BC04 fill:#fff2cc,stroke:#d6b656
```

**Legend:**
- [U] = Upstream (provides the interface)
- [D] = Downstream (consumes the interface)
- Green = Core domain (highest business value)
- Blue = Supporting domain
- Yellow = Generic / downstream

---

## Integration Relationship Details

### Relationship 1: BC-01 → BC-03

| Field | Value |
|---|---|
| **Pattern** | [OHS/PL / Customer-Supplier / Conformist / ACL / Partnership / Shared Kernel / Separate Ways] |
| **Direction** | BC-01 (Upstream) → BC-03 (Downstream) |
| **What is shared** | [specific data structures, events, or APIs] |
| **Integration mechanism** | [REST API / Event Bus / Shared Schema / Shared Library] |
| **Contract** | [link to API spec or event schema] |
| **Change impact** | [what happens if BC-01 changes its interface] |

**Pattern explanation:**
```
OHS (Open Host Service): BC-01 provides a well-documented, stable API
PL (Published Language): The API uses a formally defined schema
ACL needed at BC-03: [YES/NO — does BC-03 need to translate BC-01's model?]
```

---

### Relationship 2: BC-02 → BC-03

| Field | Value |
|---|---|
| **Pattern** | [pattern name] |
| **Direction** | |
| **What is shared** | |
| **Integration mechanism** | |
| **Contract** | |
| **Change impact** | |

---

<!-- Add one section per integration relationship -->

---

## Integration Pattern Reference

```
Partnership:
  Both teams plan and develop together — changes coordinated.
  Use when: high interdependence, teams can communicate frequently.
  Risk: both teams must move together.

Shared Kernel:
  A small piece of the domain model is shared between contexts.
  Use when: sharing is genuinely valuable and teams coordinate well.
  Risk: tight coupling — changes require coordination.

Customer/Supplier (Upstream/Downstream):
  Upstream provides an API; downstream consumes it.
  Upstream is not influenced by downstream needs.
  Use when: one context clearly serves another.
  Risk: downstream is at the mercy of upstream priorities.

Conformist:
  Downstream conforms completely to upstream's model.
  Use when: upstream cannot be influenced; not worth translating.
  Risk: downstream model polluted by upstream concerns.

Anti-Corruption Layer (ACL):
  Downstream translates upstream's model into its own language.
  Use when: upstream model is messy or conflicts with your domain.
  Cost: translation code to maintain.

Open Host Service (OHS):
  Context provides a well-defined, stable protocol for any consumer.
  Use when: many contexts depend on this one.
  Combined with Published Language for formal schema definition.

Published Language (PL):
  Formal, shared language (JSON Schema, Protobuf, OpenAPI) for communication.
  Often combined with OHS.
  Benefit: decoupled from implementation language.

Separate Ways:
  No integration — contexts solve the problem independently.
  Use when: cost of integration > cost of duplication.
  Risk: data duplication; no single source of truth.
```

---

## Ubiquitous Language Conflicts

Document where the same term means different things across contexts:

| Term | In BC-XX | Means | In BC-YY | Means | Resolution |
|---|---|---|---|---|---|
| "Order" | BC-01 | A confirmed purchase | BC-05 | A production work order | Use "PurchaseOrder" in BC-01, "WorkOrder" in BC-05 |
| "User" | BC-02 | Authenticated account holder | BC-03 | Any person interacting | Define "Account" (BC-02) vs "Visitor" (BC-03) |

---

## Context Integration Events

Events that cross context boundaries:

| Event Name | Emitted by | Consumed by | Payload Summary | Pattern |
|---|---|---|---|---|
| [OrderPlaced] | BC-01 | BC-04 | {orderId, customerId, total} | OHS/PL |
| [PaymentConfirmed] | BC-02 | BC-01, BC-04 | {paymentId, orderId, amount} | OHS/PL |

---

## Migration Notes

[If this context map replaces an older implicit architecture, document what changed and why]
