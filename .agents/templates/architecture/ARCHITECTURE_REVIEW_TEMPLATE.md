# Architecture Review Report — [System Name]
<!-- Created by: arch-review.skill -->
<!-- Methodology: ATAM-lite (Architecture Tradeoff Analysis Method, adapted for single-agent use) -->
<!-- Standard: ISO/IEC/IEEE 42010, SEI ATAM -->

---

## Meta

| Field | Value |
|---|---|
| **System** | [system name] |
| **Architecture version / commit** | [reference] |
| **Review date** | [YYYY-MM-DD] |
| **Reviewer** | [agent / human] |
| **Artifacts reviewed** | [list: architecture doc, codebase, ADRs, diagrams] |
| **Requirements reference** | [PRD.md, SPEC.md] |

---

## Executive Summary

**Architecture Fitness**: SOUND / AT RISK / INADEQUATE

[3-5 sentences: overall assessment, most important finding, immediate recommendation]

**Most critical issues**:
1. [Critical issue 1]
2. [Critical issue 2]

---

## Architecture as Found

> Reconstructed or verified architecture description — this is the ACTUAL architecture,
> not the intended one. Code is the source of truth if documentation conflicts.

### System Context (reconstructed if needed)

```mermaid
C4Context
    [Reconstruct or verify from actual system]
```

### Container View (major components / services)

```mermaid
C4Container
    [Actual containers/components as they exist]
```

### Primary Architecture Style

**Identified style**: [Layered / Event-Driven / Service-Based / Monolith / etc.]
**As intended vs as found**: [Does the actual structure match stated intent?]
**Style consistency**: [Is the style applied consistently, or are there mixed patterns?]

---

## Quality Attribute Scenario Analysis

For each QAS, assess whether the architecture satisfies it:

| QAS ID | Quality Attr | Stimulus | Measure | Verdict | Evidence |
|---|---|---|---|---|---|
| QAS-P01 | Performance | 1k concurrent users | p99 < 2s | AT RISK | [Synchronous DB calls with no caching] |
| QAS-R01 | Reliability | DB server failure | Recovery < 30s | VIOLATED | [Single DB instance, no replica] |
| QAS-S01 | Security | SQL injection attempt | Zero success rate | SATISFIED | [Parameterized queries verified] |

**Verdict values**:
- `SATISFIED`: Architecture demonstrably meets this QAS
- `AT RISK`: May not meet under stress, failure, or scale
- `VIOLATED`: Architecturally cannot meet this QAS
- `UNKNOWN`: Insufficient evidence to assess

---

## QAS Details

### QAS-P01: Performance — [VERDICT]

**Finding**: [What specific architectural element causes concern or provides assurance]

**Evidence**:
- [Specific code location, design element, or measurement]
- [Load profile or usage data if available]

**Risk**: [What happens if this QAS is violated]

**Recommendation**: [Specific architectural change to improve this]
**Effort**: [hours / days / weeks]

---

### QAS-R01: Reliability — [VERDICT]

**Finding**:
**Evidence**:
**Risk**:
**Recommendation**:
**Effort**:

---

<!-- Add one section per QAS -->

---

## Architecture Smells Catalog

### Structural Smells

| Smell | Severity | Location | Evidence | Recommendation |
|---|---|---|---|---|
| God Component | HIGH | [ComponentX — 45% of all logic] | [import graph shows 23 dependents] | Split by [responsibility boundary] |
| Cyclic Dependency | HIGH | [Module A → B → C → A] | [madge output] | Extract shared abstraction |
| Layer Inversion | MEDIUM | [Domain imports Infrastructure] | [file:line] | Invert dependency via interface |
| Bottleneck | MEDIUM | [SharedUtils — 89% of modules depend on it] | [dependency graph] | Split into specific utilities |

### Communication Smells

| Smell | Severity | Location | Evidence | Recommendation |
|---|---|---|---|---|
| Missing Circuit Breaker | HIGH | [External payment API call] | [No timeout, no fallback in code] | Add circuit breaker pattern |
| Synchronous Overuse | MEDIUM | [Email sending in request path] | [POST /orders calls email inline] | Move to async worker |
| Implicit Contract | MEDIUM | [Service A calls Service B's internal URL] | [Hardcoded internal endpoint in code] | Define explicit client interface |

### Data Smells

| Smell | Severity | Description | Recommendation |
|---|---|---|---|
| Shared Mutable State | HIGH | [Global config object mutated across threads] | Immutable config or thread-local |
| Cross-Module DB Access | HIGH | [Module B queries Module A's tables directly] | Route through Module A's API |

---

## Sensitivity Points

> Design decisions that, if changed, would significantly affect one or more quality attributes.

| Sensitivity Point | Current Decision | Quality Attributes Affected | Change Impact |
|---|---|---|---|
| [Database access pattern] | [Synchronous ORM queries] | Performance, Scalability | HIGH — all latency-sensitive operations affected |
| [Authentication placement] | [Per-endpoint auth checks] | Security, Performance | MEDIUM — missing one check = security hole |
| [Message queue reliability] | [Fire-and-forget events] | Reliability, Data Consistency | HIGH — lost events = data inconsistency |

---

## Tradeoff Points

> Design decisions where improving one quality attribute degrades another.

| Tradeoff Point | Decision | Improves | Degrades | Assessment |
|---|---|---|---|---|
| [Encryption at rest] | [All data encrypted] | Security | Performance (5-10% overhead) | ACCEPTABLE — security requirement dominates |
| [Synchronous auth check] | [Check on every request] | Security | Latency (+10ms) | ACCEPTABLE — latency impact minimal |
| [Eventual consistency] | [Async event updates] | Performance, Scalability | Data Consistency | AT RISK — may violate QAS-R01 |

---

## Risks

| Risk ID | Description | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| RISK-001 | Single DB instance — no failover | H | H | Add read replica + automatic failover |
| RISK-002 | No circuit breaker on payment API | M | H | Implement circuit breaker with fallback |
| RISK-003 | God component coupling blocks team velocity | H | M | Planned decomposition per ADR-007 |

---

## Non-Risks (Sound Decisions)

> Well-reasoned decisions that may look risky but are actually sound.

| Decision | Why it's a non-risk |
|---|---|
| [Synchronous auth on all requests] | [Adds < 10ms; eliminates async session complexity; security cannot be eventually consistent] |
| [Single-process architecture] | [Load profile shows < 500 concurrent users; single process is sufficient and simpler] |

---

## Fitness Functions

> Checks that should be continuously measured to verify the architecture is healthy.

| Fitness Function | Status | Measurement | Frequency |
|---|---|---|---|
| No cyclic dependencies | EXISTING | `madge --circular src/` | Each PR |
| Test coverage ≥ 96% | EXISTING | CI coverage report | Each commit |
| No cross-layer imports | MISSING | dependency-cruiser | Should be: each PR |
| p99 latency < 500ms | MISSING | Load test in CI | Should be: each release |
| No CRITICAL CVEs | EXISTING | `npm audit` | Each PR |

**Recommended additions**: [list fitness functions to add based on risks found]

---

## Recommendations (Prioritized)

| Priority | Risk/Smell | Recommendation | Effort | ADR Needed |
|---|---|---|---|---|
| CRITICAL | RISK-001 — No DB failover | Add read replica and automatic failover | 2-3 days | YES — ADR-NNN |
| CRITICAL | RISK-002 — No circuit breaker | Implement circuit breaker for external calls | 1 day | NO |
| HIGH | God Component [X] | Decompose into [A] and [B] by [boundary] | 1 sprint | YES — ADR-NNN |
| HIGH | Cyclic dependency A→B→C→A | Extract shared abstraction [D] | 3 days | NO |
| MEDIUM | Missing fitness functions | Add dependency-cruiser + load test to CI | 2 days | NO |

---

## Architecture Evolution Recommendations

For significant improvements that require phased implementation:

### Phase 1 (Immediate — before next release)
[Critical risk mitigations]

### Phase 2 (Next sprint — maintainability)
[Architecture smell remediation]

### Phase 3 (Next quarter — strategic improvement)
[Structural changes that improve long-term health]

---

## Review Sign-off

**Gate decision**: APPROVED / APPROVED WITH CONDITIONS / BLOCKED

**Conditions for BLOCKED or APPROVED WITH CONDITIONS**:
- [ ] [Specific condition that must be met]

**Sign-off**: [human name / date]
**Next review trigger**: [When should this architecture be reviewed again? Major feature / N months / scale milestone]
