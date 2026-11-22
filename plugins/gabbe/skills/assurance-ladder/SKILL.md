---
name: assurance-ladder
description: "Choose how strongly a component must be verified, from plain tests (level 0) to a machine-checked proof of a small core (level 3), record the choice in an ASSURANCE_PLAN, and know which evidence each level leaves. Use at S01/S02 when planning verification, when a requirement mentions concurrency, money, authorisation or safety, or when asked how sure we are that code is correct. Use when: assurance level, how strongly to verify, formal verification, choose verification level, assurance plan, prove correctness, model checking, high-risk component."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/assurance-ladder.skill.md"
  tags: "coding, testing, formal-methods, verification, risk"
  core: "true"
  context_cost: "medium"
---
# Assurance Ladder

## Goal
Pick, per component, the cheapest verification level that matches its risk, get the human's approval for anything above level 1, and leave evidence a reviewer can re-run. The ladder adds evidence to the quality gates G1-G9; it never replaces one. Guide: `agents/guides/principles/assurance-ladder.md`.

## The four levels
| Level | What it adds | Technique skill |
|---|---|---|
| 0, always | types, lint, test-first, EARS requirements traced to tests | `tdd-cycle.skill.md`, `traceability-audit.skill.md` |
| 1, default for new code with logic | property tests, contracts at boundaries, fuzzing of parsers, mutation-score floor on changed code, tests the implementer may not edit | `pbt-strategy.skill.md`, `design-by-contract.skill.md`, `fuzz-differential-testing.skill.md`, `mutation-testing.skill.md`, `verification-anti-cheating.skill.md` |
| 2, risk trigger below | a design-level model (TLA+, Quint, Alloy or P) and tests derived from it | `formal-spec-lightweight.skill.md` |
| 3, human decision, small core only | machine-checked proof (Dafny, Verus, Kani, Lean) plus the leak checklist | `proof-core-verification.skill.md` |

## Steps
1. List the components from the requirements (S01) and the architecture (S02). Done when every component has a name and a one-line purpose.
2. For each component, answer the decision table. The level is the highest row that matches.

| Trigger found in the requirements or code | Minimum level |
|---|---|
| Pure logic, parsing, data transformation | 1 |
| Parser or decoder of untrusted input | 1 with fuzzing |
| Concurrency, distributed protocol, retries, queues, locks | 2 |
| State machine with more than about 5 states or irreversible transitions | 2 |
| Money, balances, quotas, billing | 2 |
| Authorisation or access-control decisions | 2 |
| Safety or security critical small core (under roughly 500 lines, few dependencies, stable interface) | 3 proposed to the human |
| Glue, configuration, UI layout, throwaway scripts | 0 |

3. Write `project/ASSURANCE_PLAN.md` from `agents/templates/core/ASSURANCE_PLAN_TEMPLATE.md`: level, trigger, reason, evidence location per component. Done when no component lacks a level.
4. Ask the human to approve every component above level 1 (levels 2 and 3 cost time and need tools installed in the project). Record one `AUDIT_LOG.md` row `HUMAN_APPROVED` with the phase, date and the human's words. Without it, stay at level 1 and say so in the plan. The human may raise or lower any level; the agent never raises a level on its own.
5. Run the techniques at the right phase:
   - S01: write the properties in plain words next to each EARS requirement (what must always hold).
   - S02/S03: level 2 models and the design-level invariants (`formal-spec-lightweight`); level 3 scope and specification (`proof-core-verification`).
   - S05: level 1 contracts, property tests, fuzz targets; level 3 proof work.
   - S06: mutation floor, fuzz run, model checker re-run, proof re-check; tests the implementer may not edit are frozen first (`verification-anti-cheating`).
   - S07: the leak checklist and the trusted-base list go to the security reviewer.
6. Collect evidence at the locations named in the plan: test and fuzz output, `MUTATION_REPORT`, model checker log and spec, `PROOF_OBLIGATION`. Done when each component row points to files that exist and a command that reproduces them.
7. Report per component: level planned, level reached, and any claim narrowed. A level not reached is stated, not rounded up.

## Constraints
- The ladder adds evidence to the quality gates G1-G9; it never replaces one.
- Levels above 1 need the human's approval (step 4); the agent never raises a level on its own.

## Output Format
`project/ASSURANCE_PLAN.md`, evidence files at the listed paths, and the per-component report of step 7.

## Limits and safety
- Agents are weak at writing both the specification and the proof; a reported success proves only what the specification says. The human reviews the specification, not the proof.
- A level-3 result covers the small core under its stated assumptions, not the product.
- Never lower a level or weaken a property to make a check pass; narrow the claim in the plan and ask the human.
- Install tools in the user's project only after step 4 approval; never add them to the kit.
- If a tool named here is not installed and cannot be installed, mark the component "level not reached" with the reason.
