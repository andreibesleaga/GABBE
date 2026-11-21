---
name: fuzz-differential-testing
description: Fuzz parsers and decoders with a coverage-guided fuzzer, compare an implementation with a reference by differential testing, and triage crashes into permanent regression tests. Use at S05/S06 for any code that reads untrusted or complex input, and for rewrites that must match an old implementation.
triggers: [fuzzing, fuzz parser, coverage-guided fuzzer, differential testing, crash triage, fuzz target, reference implementation comparison]
tags: [coding, testing, fuzzing, security]
core: false
context_cost: medium
---
# Fuzzing and Differential Testing

## Goal
Find inputs that crash, hang or disagree, by generating many inputs guided by code coverage. Output: fuzz targets in the repo, a seed corpus, and a regression test for every crash found. A fuzzer samples; a clean run is not a proof.

## Steps
1. Pick the targets: functions that take bytes or text from outside (parsers, decoders, deserialisers, file readers, protocol handlers). Done when the list is written in the plan.
2. Choose the fuzzer (commands checked 2026-11-21 on each tool's site or repository):

| Ecosystem | Fuzzer | Setup and run |
|---|---|---|
| Go (1.18+) | built in | `func FuzzX(f *testing.F)` with `f.Fuzz(func(t *testing.T, b []byte){...})`; `go test -fuzz=FuzzX -fuzztime=30s`; failures land in `testdata/fuzz/FuzzX/` |
| Rust | cargo-fuzz | `rustup install nightly`, `cargo install cargo-fuzz`, `cargo fuzz init`, `cargo fuzz run <target>`; crashes in `fuzz/artifacts/<target>/` |
| Python | Atheris | `pip3 install atheris`; target takes `bytes`, calls `atheris.Setup(sys.argv, TestOneInput)` then `atheris.Fuzz()`; run the script with `python3` |
| Java/Kotlin | Jazzer | `jazzer-junit` from Maven Central; a `@FuzzTest` method; fuzz mode: `JAZZER_FUZZ=1` and run the test |
| JavaScript/TypeScript | Jazzer.js | `npm install --save-dev @jazzer.js/core`; export `fuzz(data)`; `npx jazzer FuzzTarget` |
| C/C++ | AFL++ | `afl-fuzz -i seeds -o out -- ./target @@` after compiling with `afl-cc` |

   Other languages: use property tests with generated inputs (`pbt-strategy.skill.md`) and say the fuzzer is missing.
3. Write the target so it is fast and deterministic, with no network, clock or shared files. The check is "no crash, no hang, no unhandled error"; add a round-trip check where one exists (`decode(encode(x)) == x`).
4. Seed the corpus with a few valid inputs and the known-bad inputs from past bugs. Commit the seeds.
5. Run for a fixed budget (for example 60 seconds per target in CI, longer nightly). Record the budget in the report; it is part of the claim.
6. Triage each crash: reproduce it from the saved file, minimise it (Go and cargo-fuzz do it; otherwise by hand), find the cause, fix the code, and commit the input as a regression test. Done when the corpus replays clean in the normal test run.
7. Differential testing: when a reference exists (the old implementation, a standard library, a trusted slow version), feed the same generated inputs to both and assert equal outputs, or equal error class. Disagreements are either a bug in the new code or a documented difference; write the difference down, do not hide it.

## Constraints
- A fuzz target is fast and deterministic: no network, clock or shared files.
- The run budget (time, corpus size) is part of every claim.
- Every crash becomes a committed regression input.

## Output Format
Fuzz targets in the repository, the committed seed corpus, a regression test for each crash, and a report that states the run budget.

## Limits and safety
- Run fuzzers only in a sandbox or container with no secrets and no production access; fuzz inputs can exhaust memory, disk and time. Set time and memory limits.
- Never delete a crashing input to make the run green; the file becomes the regression test.
- Never catch-all inside the target so errors disappear; only expected, documented errors may be ignored.
- Do not claim "no crashes" without the budget and the corpus size.
