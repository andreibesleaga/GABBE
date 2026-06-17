# Architecture Fitness Functions: [System / Service Name]

**Date:** [YYYY-MM-DD]
**Owner:** [name or role]
**Status:** Draft | Active | Deprecated

---

## 1. Purpose

<!-- A fitness function is an OBJECTIVE, executable test that some architectural
     characteristic stays within bounds as the system evolves. If it can't be
     measured, it isn't a fitness function — it's a wish. -->

This document defines the automated guardrails that protect the architectural
characteristics ("-ilities") of [System Name]. Each one is a test that fails
loudly when an architectural quality regresses.

---

## 2. Fitness Function Register

Type key: **atomic** = tests one characteristic in isolation; **holistic** = tests several interacting; **triggered** = runs on demand/PR; **continuous** = runs always (e.g. in prod monitoring).

| # | Architectural characteristic | Fitness function (objective test) | Type (atomic/holistic, triggered/continuous) | Threshold | CI wiring | Owner |
|---|---|---|---|---|---|---|
| 1 | [e.g. Modularity] | [Objective, runnable check] | [atomic, triggered] | [Pass/fail bound] | [Where it runs] | [Who] |
| 2 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |
| 3 | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 3. Worked Examples

### Example A — Layering rule (atomic, triggered)
- **Characteristic:** Maintainability / enforced layering.
- **Test:** "The `web` package must not import from the `persistence` package directly." Enforced with a dependency-rule tool (e.g. ArchUnit, import-linter, dependency-cruiser).
- **Threshold:** Zero violations.
- **CI wiring:** Runs on every pull request; build fails on any violation.

### Example B — Cyclomatic complexity limit (atomic, triggered)
- **Characteristic:** Readability / testability.
- **Test:** Static analysis reports cyclomatic complexity per function.
- **Threshold:** No function may exceed a complexity of [N]; offenders block merge.
- **CI wiring:** Linter step in the PR pipeline.

### Example C — Latency budget (holistic, continuous)
- **Characteristic:** Performance.
- **Test:** p99 latency of the `[endpoint]` measured against synthetic load.
- **Threshold:** p99 < [X] ms at [Y] RPS.
- **CI wiring:** Nightly load test + continuous production SLO monitor that pages on breach.

---

## 4. Governance

**Review cadence:** [How often the register is revisited, e.g. quarterly.]
**On failure:** [Block merge / page on-call / open ticket — define per severity.]
**Adding a new function:** [Who approves, where it lives, how it's wired.]
