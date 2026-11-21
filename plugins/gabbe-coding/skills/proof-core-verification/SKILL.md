---
name: proof-core-verification
description: "Scope a small safety- or security-critical core, have the human review its specification, prove it with Dafny, Verus, Kani or Lean, and run the leak checklist. Use only at assurance level 3, after the human has decided to pay for a proof. Use when: formal proof, machine-checked proof, dafny, verus, kani, lean proof, proof obligation, proof leak, verified core, sorry admit assume."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/proof-core-verification.skill.md"
  tags: "coding, formal-methods, proof, safety, security"
  core: "false"
  context_cost: "high"
---
# Proof of a Small Core (assurance level 3)

## Goal
Show, with a checker, that a small piece of code meets a specification written and reviewed by a human. Record the claim, assumptions and trusted base in `agents/templates/coding/PROOF_OBLIGATION_TEMPLATE.md`. Level 3 is chosen by the human in `ASSURANCE_PLAN`; the agent proposes it, never starts it alone.

## Steps
1. Scope the core: one module, a stable interface, no I/O in the part to prove (move I/O outside), and a size one person can read in an hour. If it is larger, split it or return to level 2 (`formal-spec-lightweight.skill.md`). Done when the boundary is a list of function names.
2. Write the specification (preconditions, postconditions, invariants) in the tool's language, from the requirements, with a plain-words copy beside it. The human reviews this text and the plain copy, and approves it with an `AUDIT_LOG.md` row `HUMAN_APPROVED`. The proof is not reviewed by the human; the checker does that.
3. Choose the tool (checked 2026-11-21):

| Tool | Fits | Install | Check |
|---|---|---|---|
| Dafny | new verified code, compiles to C#, Go, Python, Java, JavaScript | release binaries or VS Code extension, github.com/dafny-lang/dafny | `dafny verify f.dfy`; `dafny audit f.dfy` lists assumptions |
| Verus | Rust code | binary release, github.com/verus-lang/verus (`./verus` installs the toolchain) | `verus file.rs`, or `cargo verus verify` |
| Kani | Rust, bounded checks of panics, overflow, assertions | `cargo install --locked kani-verifier`, `cargo kani setup` | `cargo kani`, `--harness name` for one harness |
| Lean 4 | proofs about a model of the code or a Lean program | install `elan` by the steps on lean-lang.org/install (use the pinned or verified instructions there, do not pipe a downloaded script into a shell) | `lake build`, then `#print axioms thm` |

   Kani is bounded (loop unwinding), so its result is "no failure within the bound", not an unbounded proof.
4. Implement and prove. Keep the specification file read-only from now on: the proof work may change code, lemmas and hints, not the specification. A spec change goes back to the human.
5. Run the leak checklist and paste the result into the obligation file:
   - Dafny: search for `assume` and `{:axiom}`; run `dafny audit`; every item is listed with a reason or removed. Bodyless lemmas and `{:verify false}` count.
   - Verus: search for `assume(`, `admit(`, `external_body`, `external` and `assume_specification` (names from secondary sources; confirm them in the Verus guide for the installed version).
   - Kani: a SUCCESS can be vacuous (Kani's docs name unreachable checks and over-constrained harnesses); read the `UNREACHABLE` count in the summary, and delete each `kani::assume` in turn and re-run to see what it was hiding.
   - Lean: no `sorry`; `#print axioms` shows only `propext`, `Classical.choice`, `Quot.sound`; `lean4checker --fresh` after `lake build`; custom `axiom` lines listed.
   - All tools: postcondition not weaker than the plain-words copy; no stronger precondition than the requirements allow; the proved function is the one that ships.
6. Check the specification is not vacuous: mutate the code (a flipped comparison) and see the proof fail. Done when it does.
7. If the proof does not go through, in this order: (a) fix the code; (b) add a missing lemma or invariant; (c) narrow the claim openly (smaller scope, stated assumption) and ask the human; (d) return to level 2 or 1. Never weaken the postcondition, add `assume`, `sorry` or `admit`, or shrink the bounds to get a green result without the human's written approval of the narrower claim.
8. Add the proof command to CI so it re-runs on each change. Done when CI fails if the proof breaks.

## Constraints
- The specification file is read-only during proof work; a change goes back to the human.
- Report only "proved", "proved under assumptions X" or "not proved".

## Output Format
The filled `PROOF_OBLIGATION` file (claim, assumptions, trusted base, leak checklist result), the proof files, and the CI step that re-runs the proof.

## Limits and safety
- Published benchmarks show agents succeed far less when they must write the specification and the proof together; use the agent for proof search, not for deciding what is true.
- The result holds only under the listed assumptions and trusted base (compiler, solver, runtime, unverified callers); list them.
- Do not run a solver or prover on private code through an online service without the human's consent.
- Report "proved", "proved under assumptions X" or "not proved"; no other wording.
