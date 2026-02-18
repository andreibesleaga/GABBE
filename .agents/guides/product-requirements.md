# Guide: Product Requirements Engineering
<!-- Standards, methods, and quality criteria for writing verifiable requirements -->
<!-- Standards: IEEE 29148:2018, ISO/IEC 25010, IREB, BABOK, EARS -->
<!-- Technology-agnostic — applies to any product, system, or feature -->

---

## What Good Requirements Look Like

Bad requirements cause more project failures than bad code. The goal is requirements that are:

```
CORRECT:     States a real stakeholder need (not an assumed solution)
COMPLETE:    No gaps — all behaviors, errors, and edge cases specified
CONSISTENT:  No contradictions between requirements
UNAMBIGUOUS: One interpretation only — no wiggle room
TESTABLE:    An independent tester can write a pass/fail test
FEASIBLE:    Achievable within known constraints
NECESSARY:   Actually needed — not gold-plating
TRACEABLE:   Links to a stakeholder goal or use case
```

---

## Requirement Types

```
Functional Requirements (FR):
  What the system DOES — behaviors, operations, responses
  "WHEN [trigger], the system SHALL [action]"
  Verified by: test execution

Quality Requirements (QR / NFR):
  How well the system performs — quality attributes
  "The system SHALL [behavior] achieving [measurable standard]"
  Verified by: measurement, benchmark, audit

Constraints (CON):
  Non-negotiable restrictions on solution space
  "The system SHALL [comply with / use / not exceed] [constraint]"
  Verified by: inspection, compliance review

Interface Requirements (IR):
  How the system interacts with external actors and systems
  "The system SHALL communicate with [external] using [protocol/format]"
  Verified by: integration test, protocol validation
```

---

## EARS Syntax (Easy Approach to Requirements Syntax)

EARS provides five templates that cover all requirement types. Use these templates
for every formal requirement statement.

### Pattern 1 — Ubiquitous (Always True)
```
Template: "The [system name] shall [capability or constraint]."
Use for:  Business rules always in effect; security invariants; data invariants

Example:
  "The system shall store all user passwords using a one-way cryptographic hash
   with a minimum work factor of 12."

Anti-pattern: "The system should use strong passwords."
  → No trigger, vague ("strong"), uses "should" not "shall"
```

### Pattern 2 — Event-Driven (When Trigger Fires)
```
Template: "WHEN [trigger event] the [system name] shall [response]."
Use for:  User actions; external events; time-based triggers; system events

Examples:
  "WHEN an unauthenticated user submits valid credentials,
   the system shall issue a session token with a 15-minute expiry."

  "WHEN a payment authorization fails after 3 retry attempts,
   the system shall notify the customer and release the reserved inventory."

  "WHEN a background job has not completed within 30 minutes,
   the system shall mark it as failed and alert the operations team."
```

### Pattern 3 — State-Driven (While in a State)
```
Template: "WHILE [system or user is in state] the [system name] shall [behavior]."
Use for:  Operating modes; session states; system health states; time windows

Examples:
  "WHILE a user session is active, the system shall refresh the session token
   automatically every 14 minutes without requiring user interaction."

  "WHILE the system is in maintenance mode, the system shall return a
   503 Service Unavailable response to all API requests."
```

### Pattern 4 — Optional Feature (Configuration-Dependent)
```
Template: "WHERE [feature or configuration is enabled] the [system name] shall [behavior]."
Use for:  Optional features; licensed capabilities; tenant-level configuration

Examples:
  "WHERE multi-factor authentication is enabled for a tenant,
   the system shall require a TOTP code after successful password verification."

  "WHERE the system is deployed in the EU region, the system shall store all
   personal data exclusively on servers located within the European Economic Area."
```

### Pattern 5 — Unwanted Behavior (Defensive)
```
Template: "IF [unwanted condition] THEN the [system name] shall [protective response]."
Use for:  Error handling; security violations; resource limits; abuse prevention

Examples:
  "IF a login attempt fails 5 consecutive times within 15 minutes,
   THEN the system shall lock the account and send a notification to the
   registered email address with an unlock link."

  "IF the database connection pool is exhausted,
   THEN the system shall return a 503 response with a Retry-After header
   set to 30 seconds."
```

### Compound EARS (combining patterns)
```
Templates may be combined for complex requirements:
  "WHERE [feature enabled] WHEN [trigger] the system shall [response]."
  "WHILE [state] IF [condition] THEN the system shall [response]."

Example:
  "WHERE audit logging is enabled WHEN an administrator modifies user permissions,
   the system shall record the change with the administrator's identity, timestamp,
   previous value, and new value in the immutable audit log."
```

---

## Requirements Quality Checklist (per requirement)

```
The "shall" test:
  □ Contains exactly one "shall"
  □ Subject is "the system" (not a person)

Atomicity:
  □ States ONE behavior (no "and" connecting two behaviors)
  □ If "and" appears — split into two requirements

Measurability:
  □ Quality terms are quantified:
    "fast" → "within [N]ms"
    "many" → "[N] or more"
    "high availability" → "[N]% monthly uptime"
    "large" → "[N] MB / GB / TB"

Implementation-agnostic:
  □ No technology named (no "using React", "via REST API", "with PostgreSQL")
  □ States WHAT the system does, not HOW

Positive statement:
  □ States what SHALL happen, not what should be avoided
  □ Exception: Pattern 5 (unwanted behavior) intentionally defensive
```

---

## Requirement Levels and Hierarchy

```
Business Requirement:
  "Increase customer retention by reducing support ticket volume by 30%"
  Level: Strategic goal — NOT a system requirement

User Requirement:
  "As a customer, I want to track my order in real-time so I don't need to
   contact support for status updates."
  Level: User story — derived from business requirement

System Requirement:
  "WHEN an order status changes, the system shall update the customer-facing
   status page within 30 seconds of the change occurring."
  Level: EARS requirement — testable system behavior derived from user requirement

Design Constraint (if applicable):
  "The system shall expose order status via a WebSocket connection to minimize
   polling overhead."
  Level: Architecture constraint — acceptable only if mandated, not invented
```

---

## User Stories (Agile Format)

When using user stories alongside EARS:

```
User Story template:
  As a [specific actor role],
  I want to [action or goal],
  So that [business benefit or outcome].

Acceptance Criteria (GIVEN/WHEN/THEN — BDD format):
  GIVEN [precondition — system state or actor state]
  WHEN [action the actor takes]
  THEN [expected outcome]
  AND [additional assertions]

Example:
  As an authenticated customer,
  I want to view a list of my past orders,
  So that I can track the status of recent purchases and reorder items.

  Acceptance Criteria:
    GIVEN I am authenticated as a customer with at least one order
    WHEN I navigate to my Order History page
    THEN I see a list of all my orders, newest first
    AND each order shows: order number, date, status, and total amount
    AND if I have no orders, I see an empty state with a link to browse products

    GIVEN I have more than 20 orders
    WHEN I scroll to the bottom of the list
    THEN the next 20 orders load automatically (infinite scroll)

    GIVEN the service is unavailable
    WHEN I navigate to my Order History page
    THEN I see an error message explaining the issue and a retry option
```

---

## Use Cases (Detailed Process Documentation)

Use cases complement EARS by showing full interaction flows:

```
Use Case Template:

Name:          [Verb + Noun — e.g., "Place Order"]
ID:            UC-NNN
Actor(s):      [Primary actor: e.g., Authenticated Customer]
               [Secondary actors: e.g., Payment Gateway]
Goal:          [What the primary actor wants to achieve]
Preconditions: [What must be true before this use case can start]
Trigger:       [What starts this use case]

Main Flow:
  1. [Actor] [initiates action]
  2. [System] [validates or processes]
  3. [Actor] [provides additional input]
  4. [System] [responds with result]
  5. [Use case ends with: success state]

Extensions (Alternative and Exception Flows):
  2a. Validation fails:
    2a.1. [System] displays error message with field-level details
    2a.2. [Actor] corrects input
    2a.3. Return to step 2

  4a. External service unavailable:
    4a.1. [System] queues action for retry
    4a.2. [System] informs actor of delay
    4a.3. Use case ends with: pending state

Postconditions (Success):
  - [System state after successful completion]
  - [What the actor has now]
  - [Any events emitted]

Postconditions (Failure):
  - [System state if use case fails]
  - [No partial state changes committed]
```

---

## Non-Functional Requirements Framework (ISO 25010)

```
Write at least one QAS for each applicable quality attribute:

Performance Efficiency:
  Time behavior:       Response time, throughput
  Resource utilization: CPU, memory, bandwidth at stated load
  Capacity:            Maximum scale (users, data volume, transactions)

Reliability:
  Availability:        Percentage uptime over time period
  Fault tolerance:     Behavior under component failure
  Recoverability:      Recovery time and data loss on failure (RTO, RPO)

Usability:
  Appropriateness:     Task completion rate
  Learnability:        Time to proficiency for new user
  Accessibility:       WCAG 2.2 compliance level (A / AA / AAA)
  Error prevention:    Number of unrecoverable errors per N sessions

Security:
  Confidentiality:     Data accessible only to authorized parties
  Integrity:           Data not modified without authorization
  Non-repudiation:     Actions can be attributed to actor
  Authenticity:        Actor identity verifiable

Maintainability:
  Modularity:          Change confined to N modules for typical feature
  Testability:         Coverage achievable within N hours
  Modifiability:       New feature implementable in N days

Portability:
  Adaptability:        Works in [specified environments]
  Installability:      Deployment procedure completable in N minutes

Compatibility:
  Interoperability:    Exchange data with [specified systems] correctly
  Coexistence:         Operates alongside [specified systems] without interference
```

---

## Traceability Matrix

Maintain bidirectional traceability:

```
Stakeholder → Business Goal → User Story / Use Case → EARS Requirement → Test

Template:
| Business Goal | Use Case | FR-NNN (EARS) | Test ID | Verified |
|---|---|---|---|---|
| Reduce support tickets | UC-007 Place Order | FR-024 | T-089 | [YES/NO] |

Forward trace: "Which requirements implement this goal?"
Backward trace: "Why does this requirement exist? Which goal does it serve?"

Orphan requirements (no business goal trace) → probably gold-plating → remove or justify
```

---

## Priority Classification (MoSCoW)

```
MUST:   System cannot launch without this. Failure = launch blocked.
        Represents minimum viable product. All MUST requirements MUST be met.

SHOULD: Expected by stakeholders but not blocking launch.
        High value, do next after MUST.

COULD:  Desirable if time/budget allows. "Nice to have."
        Include if effort is low and value is clear.

WON'T:  Explicitly out of scope for this version.
        Agreed not to do now (may revisit later).
        Documenting WON'T prevents scope creep.

Rule: MUST requirements should represent ≤ 60% of total effort.
If MUST > 60%: scope is too large — something must move to SHOULD.
```

---

## Requirements Review Gates

```
Before architecture design begins:
  □ All stakeholders identified
  □ All MUST requirements present and EARS-compliant
  □ No ambiguous terms in any MUST requirement
  □ No consistency conflicts between requirements
  □ All MUST requirements are testable
  □ Traceability from every FR to a use case
  □ Quality requirements exist for top 3 quality attributes
  □ Constraints documented
  □ Out-of-scope defined explicitly
  □ Human (product owner) has approved requirements
```

---

## Common Requirements Anti-Patterns

```
"The system shall be fast."
→ Fix: "WHEN [actor] performs [action], the system SHALL respond within [N]ms
         under [load condition]."

"The system shall handle errors gracefully."
→ Fix: Write one Pattern 5 (unwanted behavior) requirement per significant error condition.

"The system shall be secure."
→ Fix: Write specific security requirements covering authentication, authorization,
        encryption, and input validation separately.

"The user shall be able to..."
→ Fix: "the system" is always the subject of a requirement, not "the user."
        User goals belong in use cases; system requirements describe system behavior.

"The system shall provide a REST API."
→ Fix: This is an architecture/interface requirement, not a functional requirement.
        The underlying need is: "The system shall expose [capability] to [actor]
        via a machine-readable interface." REST is a design choice.

"The system shall allow admins to manage users."
→ Fix: Too vague. Decompose: what does "manage" mean?
        Create, Read, Update, Deactivate, Delete, Unlock — each is a separate FR.
```
