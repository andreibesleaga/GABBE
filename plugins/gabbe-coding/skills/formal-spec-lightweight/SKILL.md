---
name: formal-spec-lightweight
description: "Write a small design-level model (TLA+, Quint, Alloy or P) of concurrency, a protocol, a state machine, money flow or authorisation, check it exhaustively within bounds, and turn counterexamples into tests. Use at S02/S03 for assurance level 2. Use when: formal spec, tla+, quint, alloy model, p language, model checking, design model, state machine model, protocol invariant, counterexample."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/formal-spec-lightweight.skill.md"
  tags: "coding, architecture, formal-methods, model-checking"
  core: "false"
  context_cost: "high"
---
# Lightweight Formal Specification (assurance level 2)

## Goal
Model the design, not the code, in a few dozen lines; let a checker search all behaviours within small bounds; keep the model next to the design; derive tests from it. Brief: `agents/templates/architecture/FORMAL_SPEC_BRIEF_TEMPLATE.md`. Selection help: `agents/guides/principles/modeling-methods.md`.

## When a model pays
Concurrency, retries and ordering, distributed protocols, state machines with irreversible steps, money, authorisation rules. It does not pay for plain CRUD, UI, or logic a property test already covers.

## Steps
1. Fill the brief: what is modelled, what is left out, the invariants in plain words, the bounds. Get the human's approval of the invariants (this is the specification review). Done when each invariant is one sentence a non-author can check.
2. Pick the tool (checked 2026-11-21):

| Tool | Install | Check |
|---|---|---|
| Quint | `npm i @informalsystems/quint -g` | `quint typecheck m.qnt`; `quint run m.qnt --invariant=inv` (random simulation); `quint verify m.qnt --invariant=inv` (Apalache, bounded) |
| TLA+ (TLC) | download `tla2tools.jar` from github.com/tlaplus/tlaplus/releases (Java 11+) | `java -jar tla2tools.jar -help` lists options; `-dumpTrace json out.json` writes an error trace |
| Alloy 6 | `org.alloytools.alloy.dist.jar` from alloytools.org | open it in the Analyzer, then run `check` commands with a stated scope |
| P | `p` from p-org.github.io/P (see its install page) | `p compile`, then `p check -tc <testcase> -s 100` explores 100 schedules; a bug writes a `.schedule` file |

3. Model the state, then the actions (each action is a guarded step), then the invariants. Start with the smallest model that has the risky interaction (two clients, two nodes, three states).
4. Run the checker. A pass says: no violation within these bounds. Write the bounds down.
5. Check the model is not vacuous: break an invariant on purpose, or remove an action's guard, and see that the checker finds a counterexample. Done when it does.
6. For every counterexample: decide whether the design or the model is wrong. If the design, change the design and record it in an ADR. Keep the counterexample as a test scenario.
7. Derive tests: turn each interesting trace (and each invariant) into an integration or property test against the real code; for a state machine use a stateful test (`pbt-strategy.skill.md`, `RuleBasedStateMachine`). Done when each invariant has a code-level test or a written reason why not.
8. Store the model beside the design (`docs/` or `project/models/`) with the exact check command in a comment. Re-run it whenever the design changes.

## Constraints
- Model the design, not the code, with the smallest model that contains the risky interaction.
- Write the bounds down with every result.

## Output Format
The model file beside the design with its check command, the filled brief, each counterexample kept as a test scenario, and the derived tests.

## Limits and safety
- The model is not the code. Passing the model says nothing about the implementation until the derived tests pass.
- A bounded check misses bugs that need more nodes, steps or values than the bounds; say so in the brief.
- Do not widen the model's assumptions or shrink the bounds to make a violation disappear; show the human.
- Agents often write models that are too weak. The step 5 check and the human's review of invariants are required.
