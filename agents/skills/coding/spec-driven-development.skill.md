---
name: spec-driven-development
description: Spec-first workflow where an executable, testable specification is written before code and becomes the single source of truth that tests verify against, flowing spec → acceptance criteria → tasks → implementation.
triggers: [write the spec before the code, run a spec-first workflow, derive acceptance criteria from a spec, decompose a spec into tasks, make the spec the source of truth, spec kit style development]
tags: [coding, process, spec-driven, sdlc, requirements]
core: false
context_cost: medium
---
# Spec-Driven Development

## Goal
Invert the usual order: write the specification *first*, make it concrete and testable, and
treat it as the single source of truth that the implementation must satisfy and the tests must
verify against. In a spec-driven (Spec Kit-style) workflow the spec is not prose that rots in a
wiki — it is an executable contract. Work flows spec → acceptance criteria → tasks →
implementation, mapping onto the project phases S01 (Requirements) → S02 (Design) → S03
(Specification) → S04 (Tasks) before S05 (Implementation). The deliverable is a **spec-driven
workflow plan**: the spec, the acceptance criteria derived from it, the task decomposition, and
the verification linkage that keeps code, tests, and spec in agreement.

## Steps
1. **Capture requirements as the spec's intent (S01).** Before writing the spec, pin down *what*
   and *why* — the user need, scope, and non-goals — separate from *how*. This anchors the spec
   so it specifies behavior, not a premature implementation. Record explicit out-of-scope items
   so the spec can't quietly expand.
2. **Resolve design constraints (S02).** Settle the architectural decisions and constraints the
   spec must respect (interfaces, quality attributes, tech constraints) via `arch-design.skill`,
   so the specification is grounded in a feasible design rather than wishful behavior.
3. **Write the executable/testable specification (S03).** Make the spec *verifiable*: every
   requirement stated so a test can pass or fail against it. Prefer concrete, observable behavior
   (inputs, outputs, error cases, edge cases, invariants) over adjectives. Where possible express
   it in an executable form — given/when/then scenarios, contract/schema definitions, or runnable
   examples — so the spec itself can be checked, not just read. This spec is now the single source
   of truth.
4. **Derive acceptance criteria from the spec.** Turn each spec requirement into explicit,
   binary acceptance criteria ("given X, when Y, the system returns Z"; "rejects W with error E").
   Acceptance criteria are the bridge between the spec and the tests — each criterion becomes one
   or more verifications. No criterion may introduce behavior absent from the spec; if it must,
   the spec is amended first.
5. **Decompose into tasks (S04).** Break the spec + acceptance criteria into atomic, independently
   verifiable tasks (small units, each traceable to specific criteria). Every task carries a link
   back to the spec section and acceptance criteria it fulfills, so the traceability is explicit
   and gaps are visible.
6. **Implement against the spec (S05).** Write code and tests to satisfy the acceptance criteria.
   Tests verify *against the spec* — they assert the specified behavior, so a passing suite means
   "matches the spec," and a spec change forces a test change. Pair with `tdd-cycle.skill` to write
   the criterion's test before its code.
7. **Keep the spec authoritative.** When reality diverges (a missed case, a changed requirement,
   an impossible criterion), update the *spec first*, then propagate to acceptance criteria,
   tasks, tests, and code. Code that drifts from the spec is a defect in one of the two — never
   let undocumented behavior accumulate. Maintain the spec→criteria→task→test traceability as the
   record that the system does what it claims.

## Constraints
- The spec is the **single source of truth**. When code and spec disagree, one of them is wrong;
  resolve by amending the spec deliberately, never by silently letting code define behavior.
- A spec is only useful if it is **testable**. Requirements that cannot be turned into a
  pass/fail criterion are aspirations, not spec — rewrite them as observable behavior or remove
  them.
- Tests verify *against the spec*, so a green suite means "conforms to the current spec," **not**
  "is correct" — the spec itself can be wrong or incomplete. State this honestly; spec-driven
  development moves correctness questions up to spec review, it does not eliminate them.
- Every acceptance criterion and task MUST trace to a spec section; untraced work is either
  gold-plating or a spec gap. Surface both rather than absorbing them.
- Changes flow spec → criteria → tasks → tests → code, never the reverse. A code change that
  alters behavior without a spec update is an undocumented divergence to flag.

## Output Format
Produce a **spec-driven workflow plan** containing:
- The specification: requirements and non-goals (S01), respected design constraints (S02), and
  the executable/testable behavior statements (S03) — inputs, outputs, error and edge cases,
  invariants.
- The acceptance criteria derived from each spec requirement, each binary and observable.
- The task decomposition (S04), each task linked to its spec section and acceptance criteria.
- The verification linkage: which test verifies which criterion, and the spec→criteria→task→test
  traceability map.
- An honesty note: tests confirm conformance to the spec, not absolute correctness; the spec must
  be reviewed on its own merits. Cross-reference `tdd-cycle.skill` for the test-first inner loop
  and `arch-design.skill` for the design phase.

## Security & Guardrails

### 1. Skill Security
- **Risk**: "Tests pass" is reported as "the system is correct," when it only means the code
  conforms to a spec that may itself be wrong or incomplete. Mitigation: every report MUST scope
  the claim to spec-conformance and require the spec to be reviewed independently; the agent MUST
  NOT present spec conformance as proof of correctness.
- **Risk**: The spec is silently weakened to make a failing test pass. Mitigation: spec changes
  MUST be explicit, reviewed, and version-controlled like code; the agent MUST refuse to edit the
  spec merely to accommodate broken code without surfacing the change for human approval.

### 2. System Integration Security
- **Risk**: Security and compliance requirements live only in the implementation and never enter
  the spec, so they are untested and can be dropped in a refactor. Mitigation: require security,
  authz, data-handling, and compliance requirements to be first-class, testable spec items with
  their own acceptance criteria and traceable tests.
- **Risk**: Implementation adds undocumented behavior (a hidden endpoint, an extra side effect)
  not in the spec, expanding attack surface invisibly. Mitigation: treat any behavior absent from
  the spec as a divergence to flag; the traceability map MUST expose code paths that map to no
  spec section.

### 3. LLM & Agent Guardrails
- **Risk**: The agent invents acceptance criteria or tasks describing behavior the spec never
  stated, then builds and tests to its own fiction. Mitigation: every criterion and task MUST
  trace to a spec section; the agent MUST amend the spec first (with human review) before adding
  derived behavior, and MUST mark agent-proposed requirements as unconfirmed.
- **Risk**: The agent writes tests that assert the implementation it just wrote rather than the
  spec, making them tautological and unable to catch spec violations. Mitigation: tests MUST be
  derived from acceptance criteria/spec, not reverse-engineered from the code; the agent MUST
  verify each test would fail if the specified behavior were violated.
