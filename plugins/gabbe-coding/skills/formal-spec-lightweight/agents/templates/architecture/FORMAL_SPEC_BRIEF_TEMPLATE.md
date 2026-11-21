# Formal Spec Brief: [Component or Protocol]

**Date:** [YYYY-MM-DD]
**Author:** [name]
**Tool:** [Quint | TLA+ (TLC) | Alloy 6 | P] version [x.y.z]

<!-- Filled at S02/S03 by formal-spec-lightweight.skill (assurance level 2). The human reviews this brief,
     especially section 3. A pass means: no violation within the bounds in section 4. -->

## 1. What is modelled

[Actors, state, and the actions that change it. One short paragraph.]

## 2. What is not modelled

[Everything left out and why: persistence, network details, performance, UI.]

## 3. Invariants in plain words

| # | Invariant (one sentence a non-author can check) | Source requirement |
|---|---|---|
| 1 | [e.g. "no balance is ever negative"] | [REQ-id] |

Human approval of section 3: [name, date, AUDIT_LOG row]

## 4. Checker and bounds

- File: [path to model]
- Command: [exact command]
- Bounds: [e.g. 2 clients, 3 nodes, 12 steps]
- Result: [pass | counterexample] on [date]
- What this does not cover: [larger sizes, longer runs]

## 5. Vacuity check

[The deliberate change that made the checker fail, and its output. Required.]

## 6. Counterexamples and derived tests

| Counterexample or invariant | Design change (ADR) | Test in the code base |
|---|---|---|
| [trace] | [ADR-n or none] | [test path] |
