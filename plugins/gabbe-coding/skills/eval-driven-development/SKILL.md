---
name: eval-driven-development
description: "Build an offline eval suite for LLM or agent output: golden dataset, tiered checks, pass@k and pass^k, and a CI gate against a baseline. Use when output quality is probabilistic and unit tests cannot score it, or after a prompt change."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/eval-driven-development.skill.md"
  tags: "coding, ai, evaluation, testing"
  core: "false"
  context_cost: "medium"
---
# Eval-Driven Development

## Goal
Build offline evaluation suites that *score* the quality of probabilistic LLM and agent
outputs, as opposed to tests that *verify* deterministic code. A unit test asserts a fixed
truth (`add(2,2) == 4`). An eval measures a distribution: "across 200 diverse inputs, how
often does the agent produce an acceptable answer, and how reliable is that across repeated
runs?" Evals raise confidence in a behavior that has no single correct output. They do not
prove correctness — be explicit about that throughout.

## Steps
1. **Define a golden dataset.**
   - Collect 100-300 input→expected cases that are *diverse* (cover edge cases, failure
     modes, and the long tail — not just the happy path) and *mutually exclusive* (no two
     cases test the same behavior, so a single regression does not silently fail ten rows).
   - Source from real production logs, known past bugs, and adversarial hand-authored cases.
   - Version-control the dataset alongside code so every change is reviewable and revertible.
   - Record, per case, the input, the expected output (or acceptance criteria), and which
     assertion tier applies.
2. **Apply the 3-tier assertion ladder.** Layer cheapest-and-strictest first.
   - **Tier 1 — Deterministic** (exact string match, regex, JSON-schema validation). Run at
     `temperature=0`. Fully reproducible, near-zero cost. Use whenever the output has a
     verifiable structure (valid JSON, contains a required field, matches a pattern).
   - **Tier 2 — Semantic similarity** (embedding cosine distance against a reference answer,
     threshold-gated). Near-deterministic. Use when wording may vary but meaning must match.
   - **Tier 3 — LLM-as-judge** (a model scores open-ended quality against a rubric). Most
     expensive and least reproducible; reserve for subjective criteria. Delegate the judge
     design to `llm-as-judge.skill` and inherit its bias controls.
3. **Handle nondeterminism with statistical gating.**
   - LLM/agent outputs vary run-to-run, so a single run is *noise*: single-run estimates of
     agent quality commonly swing 2-6 percentage points between runs. One green run proves
     nothing about reliability.
   - Run each case N times (e.g. N=5). Report **pass@k** (succeeds in at least one of k
     trials — measures capability) and **pass^k** (succeeds in *all* k trials — measures
     reliability). For production gating, pass^k matters far more than pass@k.
4. **Build eval-driven CI.**
   - Order checks by cost: run all Tier 1 deterministic checks first, then Tier 2, then run
     expensive Tier 3 judge evals only on the subset that actually needs subjective scoring.
   - Store a baseline (the accuracy of the current main branch). Gate on a *threshold drop*
     vs. that baseline — e.g. fail the build if aggregate accuracy drops more than 5% — rather
     than demanding a fixed absolute score, which would be brittle.
5. **Guard against prompt-drift regression.**
   - When you tweak a prompt to fix one failing case, re-run the *entire* golden set before
     accepting the change. Prompt edits routinely fix one row and silently break fifty others.
   - Track the per-case pass/fail diff vs. baseline so a +1/-50 trade is impossible to miss.

## Constraints
- Evals **sample** the input space; they raise confidence, they do not prove correctness.
  Never report or claim "100% correct" — at most "100% on the current golden set of N cases."
- Keep golden datasets version-controlled and reviewed like code; an unreviewed dataset edit
  can quietly redefine "passing."
- Always layer cheap deterministic checks before expensive judge calls to control token cost
  and latency.
- A single eval run is statistically meaningless for a stochastic system; always report N and
  pass^k, never a one-shot number.
- Named external tools/patterns worth knowing (not dependencies of this skill): **promptfoo**
  (declarative eval configs and CI gating) and **DeepEval** (pytest-style LLM assertions).

## Output Format
Produce an **eval report** containing:
- Per-tier pass rates (Tier 1 / Tier 2 / Tier 3) with the assertion type for each.
- pass@k and **pass^k** reliability figures with the value of N used.
- Drift-vs-baseline delta (per-case diff and aggregate accuracy change), and the CI verdict
  (pass/fail against the threshold).
- An explicit disclaimer that the suite samples the input space and does not certify
  correctness.

## Limits and safety
- Review dataset changes like code; accept no generated case without a traceable origin, and remove personal data from production logs before they become cases.
- Keep the baseline read-only during a gating run; update it only in a separate step the human reviews.
- Before a large judge run, state the number of model calls and set a cap; run cheap checks first.
- Pass the text under evaluation to the judge as quoted data, never mixed into the rubric (see `llm-as-judge.skill`).
- Hold out cases not used while tuning prompts and report them separately; say "passed N cases", never "correct".
