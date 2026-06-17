# Evaluation Strategy Guide (for agentic / LLM systems)

When the system under construction is — or relies on — an LLM, "does it pass?" is the
wrong question. Output is probabilistic, so the right question is "how good is it, on
average, on the inputs we care about, and is it getting worse?". This guide covers how
GABBE evaluates probabilistic systems alongside its normal deterministic testing.

## 1. Tests vs Evals — two different jobs

These are complementary, not competing. You need both.

- **Tests** verify **determinism**. The same input must always produce the same output.
  The verdict is binary pass/fail, it is cheap, and it runs on every commit/PR in CI. This
  is everything in `testing-strategy.md` — static analysis, unit, integration, contract,
  E2E.
- **Evals** score **probabilistic quality**. The same input may produce different output
  each run. The verdict is **graded** (a score, not a boolean), it **samples** the input
  space rather than covering it exhaustively, and it tolerates variance by running many
  times.

Rule of thumb: if you can write a deterministic assertion, write a **test**. Reach for an
**eval** only for the part that is genuinely probabilistic (the model's judgment, phrasing,
or reasoning).

## 2. The Eval Pyramid

Like the testing pyramid, push work down to the cheapest, most-deterministic layer that
can express the check. Climb only when you must.

1. **Deterministic assertions (base)** — exact match, regex, JSON-schema validation, set
   membership. Cheap, instant, 100% reproducible. Most "quality" checks are secretly
   deterministic — catch them here.
2. **Semantic similarity** — embedding cosine similarity against a reference answer, with
   a threshold. Tolerates wording differences while still being mostly reproducible.
3. **LLM-as-judge** — a model scores the output against a rubric. Expensive, subjective,
   non-deterministic; use for quality dimensions no formula captures (clarity, helpfulness).
4. **Human review (tip)** — the gold standard and the calibration anchor for everything
   below it. Slowest and most expensive; reserve for high-stakes output and for keeping the
   judges honest.

Each layer up costs more and is less reproducible. A good eval suite is fat at the base.

## 3. Eval-first, alongside test-first

Test-first says: write the failing test before the code. Eval-first extends this to
probabilistic work: **define the golden dataset and the rubric before building the
system**. The golden dataset is the executable form of the spec — it states, in concrete
input/expected pairs, what "good" means. Writing it first forces you to define success
before you can fool yourself into thinking you have it. See `eval-driven-development.skill`
for the full workflow (start small, grow the dataset from every real failure).

## 4. Where evals plug into GABBE's SDLC

- **S05 / S06 (implementation / testing)** — eval **checkpoints**, owned by the **eng-qa**
  persona. As the skill/system is built, it is scored against the golden dataset and rubric
  defined earlier. A failing eval checkpoint blocks the same way a failing test does, once
  the scores are stable enough to gate on (see section 6).
- **S12 (Day-2 / evolve)** — **continuous eval**. The system runs against the eval suite on
  a schedule so quality drift (model updates, prompt edits, data shift) is caught after
  release, not by users. New production failures become new golden-dataset rows here.

The relevant skills slot in by layer: `llm-as-judge.skill` for the Tier-3 judging layer,
`rag-evaluation.skill` when the system retrieves context (score retrieval and generation
separately), and `agent-trajectory-eval.skill` when you must grade the *path* an agent took
(tool calls, intermediate steps), not just its final answer.

## 5. Nondeterminism — why we run N times and report pass^k

A single run is a single sample from a distribution. Published agent-quality estimates
vary by roughly **2–6 points** between runs of the *same* system on the *same* tasks, so a
one-shot number is noise as often as signal. To get a stable read:

- Run each case **N times** (e.g., N=5).
- Report **pass^k** (passes in *all* k runs) for reliability/CI gating — it measures
  consistency, which is what production needs. Report **pass@k** (passes in *at least one*
  of k runs) when you only want to know whether the capability exists at all.
- Record temperature and seeds so a run can be reproduced.

A system that scores 0.95 on pass@5 but 0.55 on pass^5 is not reliable — it can do the task
but won't do it dependably.

## 6. Eval-driven CI — earn the right to block

Eval scores are noisy at first, and a flaky gate that fails good PRs trains everyone to
ignore it. So introduce evals into CI in two stages:

1. **Non-blocking nightly first** — run the full suite on a schedule, publish the
   scorecard, watch the variance. Regressions are reported, not enforced.
2. **Blocking gates only once scores are stable** — promote a check to a PR-blocking gate
   only after it has shown low run-to-run variance. Gate on the deterministic Tier-1/Tier-2
   slice first; keep noisy LLM-judge checks advisory until they calibrate.

This mirrors how E2E tests earn their place in CI: prove they are not flaky before you let
them block the build.

---

**Honesty note**: Evals **raise confidence**; they do not **prove** correctness. A green
scorecard means "no regression detected on the sampled cases", never "correct on all
inputs" — so keep growing the golden dataset from real failures. And the LLM judge is
**biased-but-useful**: a fast, scalable proxy that is never ground truth and must be
**calibrated against human labels**. When you stop calibrating, you stop knowing what your
scores mean.
