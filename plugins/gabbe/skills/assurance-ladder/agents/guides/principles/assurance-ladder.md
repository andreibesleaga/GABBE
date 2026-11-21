# Assurance Ladder

> How strongly must this software be verified? Four levels, chosen by risk, approved by a human above level 1.
> Skill that applies it: `agents/skills/coding/assurance-ladder.skill.md`. Related: `modeling-methods.md`, `testing-strategy.md`.
> Sources were fetched on 2026-11-21; see the reference list.

## 1. The ladder on one page

| Level | Evidence it adds | Choose it when | Phase | Skills |
|---|---|---|---|---|
| 0 | Types, lint, test-first, EARS requirements traced to tests | Always | S01, S05, S06 | `tdd-cycle`, `traceability-audit` |
| 1 | Property tests, contracts at boundaries, fuzzing of parsers, mutation-score floor on changed code, tests the implementer may not edit | Default for new code with logic | S05, S06 | `pbt-strategy`, `design-by-contract`, `fuzz-differential-testing`, `mutation-testing`, `verification-anti-cheating` |
| 2 | A design-level model (TLA+, Quint, Alloy or P) checked within bounds, and tests derived from it | Concurrency, distributed protocol, state machine, money, authorisation | S02, S03 | `formal-spec-lightweight` |
| 3 | Machine-checked proof of a small core (Dafny, Verus, Kani, Lean) with a leak checklist | Safety or security critical small core, on the human's decision | S05, S07 | `proof-core-verification` |

The agent applies the risk triggers (decision table in the skill) and proposes a level per component in `project/ASSURANCE_PLAN.md`. The human approves every level above 1 at a human gate and the approval is one `HUMAN_APPROVED` row in `AUDIT_LOG.md`. The human may raise or lower any level.

## 2. Where each level acts in the lifecycle

| Phase | What happens |
|---|---|
| S01 Requirements | Each EARS requirement gets its "always true" property in plain words; the plan is drafted |
| S02 / S03 | Level 2 model, invariants reviewed by the human; level 3 scope and specification written |
| S05 Implementation | Contracts, property tests, fuzz targets; level 3 proof work; frozen tests stay untouched |
| S06 Testing & Quality | Mutation floor, fuzz budget, model re-check, proof re-check; anti-cheating checks |
| S07 Security Review | Leak checklist and trusted-base list reviewed with the security sign-off |

## 3. Relation to the quality gates G1-G9

The ladder adds evidence; every gate G1 to G9 still runs and still blocks. Mutation score is read next to G3 coverage (coverage says lines ran; mutation score says changes were noticed). Fuzz and proof evidence is read at G5 and S07 for the code they cover. A passed level never waives a gate, and a failed gate is not offset by a higher level elsewhere.

## 4. Who reviews what

The human reviews the specification: the invariants, the proof claim, the plain-words copy. The checker reviews the proof. Agents are weak at writing both the specification and the proof; the benchmark evidence is in section 6. A specification that is too weak or wrong gives a correct proof of the wrong thing, so the specification gets the human's attention and the vacuity checks (a deliberate fault must make the check fail).

## 5. Standards map

Only entries with a clause or table that was read. This is a pointer, not a compliance claim; the standard's own text governs.

| Standard | Clause or table | What it asks, in short | Ladder level that produces similar evidence |
|---|---|---|---|
| Common Criteria CC:2022 Part 5 (ISO/IEC 15408 family) | 4.4.8, "EAL7 - Formally verified design and tested" | Assurance from a formal model of select security policies and tightly focused functionality; practical use "currently limited to" such TOEs [1] | 3 (small core), with 2 for the policy model |
| RTCA DO-333 (supplement to DO-178C and DO-278A) | Table FM.A-3, objective FM.A-3.10 "Requirements formalization is correct" | Formalised requirements are reviewed for correctness; the tool and method must be defined and justified (FM.A-3.11) [2] | 2 and 3: the human reviews the specification |
| RTCA DO-333 | Tables FM.A-4 to FM.A-7 | Formal analysis can meet verification objectives and, in some cases, replace coverage testing; the cited case study does not address FM.A-6 and FM.A-7 [2] | 3 |

Other standards (for example IEC 61508, ISO 26262, NIST SSDF) were not read for this guide and are left out on purpose. Add a row only after reading its clause.

## 6. Honest limits, with dated sources

- Benchmarks of language models on verified-code tasks: a September 2025 benchmark of 12,504 specifications reports off-the-shelf model success of 82% on Dafny, 44% on Verus and 27% on Lean [3]. A June 2024 benchmark of over 750 Dafny programs reports a best result of 68% [4]. A Lean benchmark of 161 problems where the model must write specification and implementation reports that all tested methods "struggle to achieve full verification" [5]. These results come from different tasks and model versions and age quickly; they are not predictions for a given project.
- Proof leaks are real. Lean says `sorryAx` in `#print axioms` means an incomplete proof, and a green `lean` run is not enough [6]. Dafny's `dafny audit` exists to list assumptions such as `assume` statements, bodyless methods with postconditions and disabled verification [7]. Kani documents that a result can hold vacuously when the harness is over-constrained [8].
- Tools differ in strength. Kani checks within an unwinding bound [8]. A model checker run says "no violation within these bounds". A fuzzer or property test samples inputs and proves nothing.
- The kit has not measured whether this ladder improves agent results. Treat the levels as a method with stated evidence, not as a measured gain.

## 7. Tools by level (commands were checked on each tool's own site; see the skills)

| Purpose | Tools named in the skills |
|---|---|
| Property tests | Hypothesis, fast-check, jqwik, proptest, rapid, FsCheck |
| Contracts | icontract, deal, JML with OpenJML |
| Fuzzing | Go native fuzzing, cargo-fuzz, Atheris, Jazzer, Jazzer.js, AFL++ |
| Mutation | mutmut, StrykerJS, PIT, Stryker.NET, cargo-mutants |
| Models | Quint, TLA+ with TLC, Alloy 6, P |
| Proofs | Dafny, Verus, Kani, Lean 4 |

The kit stays plain Markdown and depends on none of them. A level installs its tools in the user's project, after the human approved the level.

## References

Fetched 2026-11-21.

1. Common Criteria for Information Technology Security Evaluation, Part 5: Pre-defined packages of security requirements, November 2022, section 4.4.8. https://www.commoncriteriaportal.org/files/ccfiles/CC2022PART5R1.pdf
2. D. Cofer and S. P. Miller, Formal Methods Case Studies for DO-333, NASA/CR-2014-218244, April 2014 (Tables FM.A-3 to FM.A-7). https://shemesh.larc.nasa.gov/fm/papers/NASA-CR-2014-218244.pdf
3. S. Bursuc et al., A benchmark for vericoding: formally verified program synthesis, arXiv:2509.22908, 26 September 2025. https://arxiv.org/abs/2509.22908
4. DafnyBench: A Benchmark for Formal Software Verification, arXiv:2406.08467, 12 June 2024. https://arxiv.org/abs/2406.08467
5. CLEVER: A Curated Benchmark for Formally Verified Code Generation, arXiv:2505.13938, v4 23 October 2025. https://arxiv.org/abs/2505.13938
6. Lean reference manual, Validating Proofs. https://lean-lang.org/doc/reference/latest/ValidatingProofs/
7. Dafny 4 release notes, 3 March 2023 (`dafny audit`). https://dafny.org/blog/2023/03/03/dafny-4-released/
8. The Kani Rust Verifier, usage and verification results. https://model-checking.github.io/kani/usage.html and https://model-checking.github.io/kani/verification-results.html
