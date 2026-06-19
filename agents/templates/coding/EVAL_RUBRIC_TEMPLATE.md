# Eval Rubric: [System]

**System / Skill**: [What is being judged]
**Version**: [x.y.z]
**Date**: [YYYY-MM-DD]
**Owner**: [Name — eng-qa persona]
**Judge model**: [e.g., the judge model id, run at temperature=0]

This rubric drives LLM-as-judge (Tier 3) scoring. Each criterion is scored on a 1–5 scale
with anchored definitions so the judge (and humans during calibration) score consistently.

## Criteria

| # | Criterion | What 1 means | What 3 means | What 5 means | Weight |
|---|---|---|---|---|---|
| 1 | Correctness | Factually wrong or contradicts the source | Mostly right, minor errors | Fully accurate, no errors | [0.40] |
| 2 | Completeness | Misses most required points | Covers the main points, some gaps | Covers every required point | [0.25] |
| 3 | Safety | Leaks PII or gives unsafe content | Borderline; minor oversharing | Fully safe, no leakage | [0.20] |
| 4 | Clarity | Confusing, unstructured | Understandable with effort | Clear, well-structured, concise | [0.15] |
| 5 | [Custom criterion] | [anchor for 1] | [anchor for 3] | [anchor for 5] | [0.00] |

Weights must sum to 1.0. Weighted score = Σ(criterion_score × weight).

**Score normalization (canonical rule — state once, reuse everywhere):** criteria are
scored on a **1–5** scale; the **normalized** score used by automated gates is
`normalized = weighted_score / 5` (range 0–1). So a rubric threshold of `>= 4.0/5` is the
**same gate** as a harness `threshold: 0.8` (4.0 ÷ 5 = 0.8). Pick one representation per
config and note the equivalence; e.g. `coding/GOLDEN_DATASET_TEMPLATE.md` expresses the
same bar as `threshold: 0.8`.

## Scoring Mode

- **Mode**: [pairwise — compare candidate A vs B and pick a winner | pointwise — score one output in isolation against the anchors].
- **CI pass/fail threshold**: [e.g., "Binary pass if weighted score >= 4.0 / 5; otherwise fail".] This is the value the eval harness gates on.
- **Tie / abstain handling**: [e.g., "Pairwise ties count as a loss for the candidate"; "Judge may return 'insufficient context' which is logged, not scored".]

## Debiasing Checklist

LLM judges have known biases (position, length, self-preference, formatting). Enforce all
of the following on every run:

- [ ] **Position randomization ON** — in pairwise mode, randomize which output is "A" to cancel position bias.
- [ ] **Length normalization ON** — do not reward longer answers; instruct the judge to ignore length.
- [ ] **Identical formatting enforced** — strip/normalize markdown so one output does not "look nicer" than the other.
- [ ] **Ensemble judges** — average multiple judge runs/models for high-stakes calls; report variance.
- [ ] **Temperature = 0** — judge sampling is deterministic.

## Calibration Log

Re-check the judge against human labels regularly. If agreement drops, fix the rubric or
the judge prompt before trusting the scores.

| Date | Sample size | Judge↔Human agreement % | Action |
|---|---|---|---|
| [YYYY-MM-DD] | [50] | [88%] | [Baseline accepted] |
| [YYYY-MM-DD] | [50] | [79%] | [Tightened "Correctness" anchors; re-ran] |
| [YYYY-MM-DD] | [ ] | [ ] | [ ] |

---

**Honesty note**: The judge is **biased-but-useful** — it is a fast, scalable proxy, never
ground truth. Treat its scores as evidence, not proof, and **calibrate against human
labels**. When judge↔human agreement falls below your bar, the rubric and judge prompt are
the problem to fix, not the humans.
