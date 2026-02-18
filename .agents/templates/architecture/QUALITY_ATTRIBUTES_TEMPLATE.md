# Quality Attributes — [System Name]
<!-- Quality Attribute Scenarios (QAS) using SEI/Carnegie Mellon format -->
<!-- Created by: arch-design.skill, req-elicitation.skill -->
<!-- Referenced by: ARCHITECTURE_VIEWS_TEMPLATE.md, ARCHITECTURE_REVIEW_TEMPLATE.md -->
<!-- Standard: ISO/IEC 25010 (SQuaRE) quality model -->

---

## Meta

| Field | Value |
|---|---|
| **System** | [system name] |
| **Version** | [1.0] |
| **Date** | [YYYY-MM-DD] |
| **Status** | DRAFT / APPROVED |

---

## Quality Attribute Priority

Rank the top quality attributes for this system (drives architecture decisions):

| Priority | Quality Attribute | Business Justification |
|---|---|---|
| 1 | [e.g., Reliability] | [e.g., Downtime directly causes revenue loss] |
| 2 | [e.g., Security] | [e.g., Handles financial data; breach is existential risk] |
| 3 | [e.g., Performance] | [e.g., Users abandon if response > 3s] |
| 4 | [e.g., Maintainability] | [e.g., Small team, frequent feature additions] |
| 5 | [e.g., Usability] | [e.g., Non-technical end users] |

---

## Quality Attribute Scenarios (QAS)

Each QAS has 6 components:
- **Source**: Who or what generates the stimulus
- **Stimulus**: The event or condition
- **Environment**: Operating conditions when stimulus occurs
- **Artifact**: What part of the system is stimulated
- **Response**: System's reaction
- **Measure**: How we know the response is acceptable (quantified)

---

### Performance Scenarios

#### QAS-P01: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | [e.g., 1,000 concurrent authenticated users] |
| **Stimulus** | [e.g., Each submits a search query simultaneously] |
| **Environment** | [e.g., Normal operating conditions, peak load period] |
| **Artifact** | [e.g., Search component and database] |
| **Response** | [e.g., System processes all queries and returns results] |
| **Measure** | [e.g., p99 response time < 2 seconds; no queries dropped] |

**Priority**: MUST / SHOULD / COULD
**Architectural implication**: [What design decisions does this drive?]

---

#### QAS-P02: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | |
| **Stimulus** | |
| **Environment** | |
| **Artifact** | |
| **Response** | |
| **Measure** | |

**Priority**:
**Architectural implication**:

---

### Reliability Scenarios

#### QAS-R01: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | [e.g., Primary database server] |
| **Stimulus** | [e.g., Hardware failure — server becomes unresponsive] |
| **Environment** | [e.g., Normal operation, no planned maintenance] |
| **Artifact** | [e.g., Data persistence layer] |
| **Response** | [e.g., System fails over to replica; in-flight transactions recovered] |
| **Measure** | [e.g., Recovery time < 30 seconds; zero data loss for committed transactions] |

**Priority**: MUST / SHOULD / COULD
**Architectural implication**: [Requires active-passive replica, automatic failover]

---

#### QAS-R02: Availability Target

| Component | Value |
|---|---|
| **Source** | [Monitoring system] |
| **Stimulus** | [Measuring system uptime over a calendar month] |
| **Environment** | [Normal operation including deployments] |
| **Artifact** | [Entire system] |
| **Response** | [System is available and responding correctly] |
| **Measure** | [99.9% availability = max 43.8 min downtime/month] |

**Priority**:
**Architectural implication**:

---

### Security Scenarios

#### QAS-S01: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | [e.g., External attacker] |
| **Stimulus** | [e.g., Attempts SQL injection via search form input] |
| **Environment** | [e.g., Normal operation, public-facing endpoint] |
| **Artifact** | [e.g., Input validation layer, database query layer] |
| **Response** | [e.g., Input rejected; malicious query never reaches database; attack logged] |
| **Measure** | [e.g., Zero successful SQL injections; attack attempt logged with source IP within 1s] |

**Priority**:
**Architectural implication**:

---

### Usability Scenarios

#### QAS-U01: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | [e.g., First-time user with no training] |
| **Stimulus** | [e.g., Attempts to complete [core task] for the first time] |
| **Environment** | [e.g., Production system, no assistance available] |
| **Artifact** | [e.g., User interface] |
| **Response** | [e.g., User successfully completes task] |
| **Measure** | [e.g., Task completed correctly in < 5 minutes by 96% of test users] |

**Priority**:
**Architectural implication**:

---

### Maintainability Scenarios

#### QAS-M01: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | [e.g., Developer] |
| **Stimulus** | [e.g., Needs to add a new payment method to the system] |
| **Environment** | [e.g., Development environment, existing codebase] |
| **Artifact** | [e.g., Payment module] |
| **Response** | [e.g., Developer adds new payment method by implementing one interface] |
| **Measure** | [e.g., Change confined to ≤ 3 files; no existing tests break; feature complete in < 1 day] |

**Priority**:
**Architectural implication**:

---

### Additional Quality Attributes

Add more QAS for: Portability, Compatibility, Interoperability, Scalability (as needed)

#### QAS-NNN: [Scenario Name]

| Component | Value |
|---|---|
| **Source** | |
| **Stimulus** | |
| **Environment** | |
| **Artifact** | |
| **Response** | |
| **Measure** | |

**Priority**:
**Architectural implication**:

---

## QAS Summary (for Architecture Validation)

| ID | Quality Attribute | Priority | Measure | Satisfied by Architecture? |
|---|---|---|---|---|
| QAS-P01 | Performance | MUST | p99 < 2s under 1k users | [YES/AT RISK/NO — after arch review] |
| QAS-R01 | Reliability | MUST | Recovery < 30s, zero data loss | |
| QAS-R02 | Availability | MUST | 99.9% monthly | |
| QAS-S01 | Security | MUST | Zero SQL injections | |
| QAS-U01 | Usability | SHOULD | Task in < 5min | |
| QAS-M01 | Maintainability | SHOULD | New payment type in 1 day | |

---

## Fitness Functions

For each MUST QAS, define how it will be continuously measured:

| QAS | Fitness Function | Measurement Tool | Frequency |
|---|---|---|---|
| QAS-P01 | Load test response time | k6 or Gatling | Every release |
| QAS-R01 | Chaos test — kill DB | Chaos Monkey / manual | Quarterly |
| QAS-R02 | Uptime monitoring | Grafana + alerting | Continuous |
| QAS-S01 | OWASP ZAP scan | CI pipeline | Every PR |
