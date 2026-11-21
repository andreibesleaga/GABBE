# Proof Obligation: [Core Name]

**Date:** [YYYY-MM-DD]
**Author:** [name]
**Tool and version:** [Dafny | Verus | Kani | Lean] [x.y.z]

<!-- Filled at S05/S07 by proof-core-verification.skill (assurance level 3, on the human's decision).
     Report only "proved", "proved under assumptions", or "not proved". -->

## 1. Claim

- Code in scope: [function or module names, file paths]
- Specification file (read-only after approval): [path]
- Plain-words copy of the specification: [text]
- Human approval of the specification: [name, date, AUDIT_LOG row]

## 2. Assumptions

| # | Assumption | Why acceptable | Where it appears in the code |
|---|---|---|---|
| 1 | [e.g. inputs are validated by caller X] | [reason] | [file:line] |

## 3. Trusted base

[Compiler, solver, runtime, libraries, unverified callers, the tool itself.]

## 4. Command and result

- Command: [exact command]
- Result and date: [output summary]
- Runs in CI: [yes, job name | no]

## 5. Leak checklist result

| Check | Result (count, and each hit with reason) |
|---|---|
| `assume` / `admit` / `sorry` / admitted lemmas | [ ] |
| `{:axiom}`, `external_body`, custom `axiom`, `{:verify false}` | [ ] |
| Tool audit (`dafny audit`, `#print axioms`, `lean4checker --fresh`) | [ ] |
| Kani: assumptions removed one at a time, coverage | [ ] |
| Postcondition not weaker than the plain-words copy | [ ] |
| Proved code is the shipped code | [ ] |
| Vacuity check (a mutated body fails the proof) | [ ] |

## 6. Claim changes

[Any narrowing of the claim, who agreed, date. Empty if none.]
