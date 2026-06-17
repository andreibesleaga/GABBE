# Eval Plan: [System]

**System**: [System / Skill under evaluation]
**Version**: [x.y.z]
**Date**: [YYYY-MM-DD]
**Owner**: [Name — typically the eng-qa persona]

## 1. Scope & Eval Goals

**What we are scoring**: [Which quality dimensions matter for this system? e.g., "Correctness, Completeness, Safety, and Clarity of the generated answer".]

**Quality dimensions**:
| Dimension | Why it matters here | How scored (tier) |
|---|---|---|
| Correctness | [e.g., factual answer must match source] | Tier 1 / Tier 3 |
| Completeness | [e.g., covers all required fields] | Tier 2 |
| Safety | [e.g., no PII leakage, no unsafe instructions] | Tier 1 / Tier 3 |
| Clarity | [e.g., readable, well-structured] | Tier 3 |

**In scope**: [e.g., "The summarization skill's output quality on support tickets".]
**Out of scope**: [e.g., "Latency / cost benchmarking", "Upstream retrieval quality".]

## 2. Golden Dataset

**Size**: [N cases — start small (20–50) and grow with each discovered failure.]
**Source**: [Where the inputs come from — production logs, hand-authored, synthetic.]
**Curation**: [Who labels the expected output and how disagreement is resolved.]
**Versioning**: [Where it lives + how it is versioned — e.g., `agents/evals/<system>/golden.yaml`, committed and tagged; every regression adds a row.]

| Case ID | Input | Expected | Edge-case type |
|---|---|---|---|
| C-001 | [Typical input] | [Expected output / key facts] | happy-path |
| C-002 | [Empty / minimal input] | [Expected graceful handling] | boundary |
| C-003 | [Malformed input] | [Expected refusal / error] | adversarial |
| C-004 | [Input that previously failed] | [Corrected expected] | regression |

## 3. Assertion Tiers

Score from cheapest/most-deterministic to most-expensive/most-subjective. Prefer the
lowest tier that can express the check.

| Tier | Method | Examples | Determinism |
|---|---|---|---|
| Tier 1 | Deterministic | exact match, regex, JSON-schema / `is-json` validation, set membership | Fully deterministic — same input → same verdict |
| Tier 2 | Semantic similarity | embedding cosine similarity vs reference, `similar` with threshold | Mostly deterministic — depends on embedding model version |
| Tier 3 | LLM-as-judge | rubric scoring, pairwise preference, `llm-rubric` | Non-deterministic — judge varies; run N times and calibrate |

## 4. Nondeterminism Handling

- **Runs per case (N)**: [e.g., N=5 — the same case is run multiple times because model output varies.]
- **Aggregation**:
  - **pass@k**: case passes if it succeeds in **at least one** of k runs. Use for "can it do it at all" capability checks.
  - **pass^k**: case passes only if it succeeds in **all** k runs. Use for reliability / CI gating where consistency matters.
- **Reported threshold**: [e.g., "pass^5 >= 0.90 on the regression slice".]
- **Seed / temperature**: [Record judge temperature=0 and any sampling settings so runs are reproducible.]

## 5. CI Gating

- **Baseline scorecard location**: [e.g., `agents/evals/<system>/baseline.json` — the last known-good scores.]
- **Threshold-drop that fails the build**: [e.g., "Build fails if any dimension drops > 3 points below baseline, or overall pass^k < 0.85".]
- **Lane**:
  - **Non-blocking (nightly)**: full eval suite runs nightly; regressions reported but do not block merges. Start here.
  - **Blocking (PR gate)**: only the stable, deterministic Tier-1/Tier-2 slice gates PRs, once scores have proven stable.
- **Promotion rule**: [When does a check graduate from non-blocking to blocking? e.g., "After 2 weeks of < 1pt variance".]

## 6. Reporting

**Scorecard format**: [e.g., a JSON + markdown table emitted per run.]

| Dimension | Score (0–5) | pass^N | Δ vs baseline | Status |
|---|---|---|---|---|
| Correctness | [4.6] | [0.92] | [+0.1] | pass |
| Completeness | [4.1] | [0.88] | [-0.2] | warn |
| Safety | [5.0] | [1.00] | [0.0] | pass |
| Clarity | [4.3] | [0.90] | [+0.0] | pass |

- **Artifacts**: [Where per-case transcripts and judge rationales are stored for audit.]
- **Trend**: [Link/location of historical scores so drift is visible over time.]

---

**Honesty note**: Evals **sample** the input space and **raise confidence** — they do not
prove correctness. A green scorecard means "no regression detected on the cases we
checked", not "the system is correct on all inputs". Grow the golden dataset whenever a
new failure mode is found in production.
