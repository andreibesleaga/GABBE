---
name: design-by-contract
description: State preconditions, postconditions and invariants at module boundaries and make them runnable checks. Use at S03/S05 for level 1 code with logic, public module interfaces, or when a requirement says what must always hold.
triggers: [design by contract, preconditions, postconditions, invariants, contract at boundary, icontract, assert contracts, module boundary checks]
tags: [coding, testing, contracts, verification]
core: false
context_cost: low
---
# Design by Contract

## Goal
Every public function at a module boundary says what it requires from the caller (precondition), what it guarantees (postcondition), and what stays true for its data (invariant). The statement is code that runs in tests and, where cheap, in production, so a broken promise fails at its source.

## Steps
1. List the boundaries: public functions, API handlers, queue consumers, anything another module or team calls. Done when each has a name.
2. For each, write the three clauses in plain words, taken from the EARS requirement or the spec (S03): "requires amount > 0", "ensures balance_after = balance_before - amount", "invariant balance >= 0". A clause with no requirement behind it is marked "proposed" for the human.
3. Choose the mechanism for the language (checked 2026-11-21):

| Language | Option | Notes |
|---|---|---|
| Python | `icontract` (`pip install icontract`) | `@icontract.require(lambda x: x > 0)`, `@icontract.ensure(lambda result, x: result > x)`, `@icontract.invariant(lambda self: self.x > 0)`; a breach raises `icontract.errors.ViolationError` |
| Python | `deal` (`pip install 'deal[all]'`) | `@deal.post`, `@deal.pure`; `deal.cases(f)` makes a test from the contract; `python3 -m deal lint` and `python3 -m deal test` |
| Java | JML, checked by OpenJML | OpenJML does runtime assertion checking and static verification; take its commands from openjml.org/documentation |
| Any other | guard clause at entry, assertion at exit, invariant method called after each mutator | plain `assert` or an explicit `throw`; no library needed |

4. Write the clauses as code next to the function. Keep each clause side-effect free and cheap.
5. Write one test per clause that breaks it on purpose and expects the failure (precondition: bad argument fails; postcondition: a stub returning a wrong result is caught). Done when each clause has a test that fails when the clause is removed.
6. Decide what stays on in production: cheap preconditions at trust boundaries stay on; expensive postconditions and invariants run in tests and staging. Write the choice in the plan.
7. Feed the contracts to property tests: a precondition is the generator's domain, a postcondition is the assertion (`pbt-strategy.skill.md`).

## Constraints
- Clauses are side-effect free and cheap.
- Every clause traces to a requirement or is marked "proposed" for the human.

## Output Format
Contract code beside each boundary function, one test per clause, and a note in the plan stating which checks stay on in production.

## Limits and safety
- Contracts at a boundary check one call; they do not prove the system. They find faults only when a test drives the code.
- Do not put validation of untrusted input in a contract that production builds strip; use real input validation there.
- Never weaken a clause to make a failing test pass; a failing contract is a finding to fix or to take to the human.
- Debug-only checks (assert statements) can be disabled by the runtime; state in the plan which checks run in production.
