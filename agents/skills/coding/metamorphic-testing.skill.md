---
name: metamorphic-testing
description: "Write a suite of metamorphic relations (an input change plus the required output relationship) for systems with no reliable oracle, such as LLM and NLP output. Use when you cannot state the correct output but can state how outputs of related inputs must relate."
triggers: [test without a correct answer oracle, write metamorphic relations, check paraphrase invariance, test llm output stability, build a metamorphic relation suite, bypass the oracle problem]
tags: [coding, testing, metamorphic, llm, nlp]
core: false
context_cost: medium
---
# Metamorphic Testing

## Goal
Test systems where you cannot say what the *single correct output* is — the oracle problem.
You often can't assert "the model's answer to this question is X", but you *can* assert that
two related inputs must produce related outputs. A *metamorphic relation* (MR) is exactly that:
a transformation of the input paired with the expected relationship between the outputs. If you
reword a question without changing its meaning, a robust system should give an equivalent
answer; if it doesn't, you found a bug without ever knowing the "right" answer. This skill
produces a **metamorphic relation suite** — a set of MRs, especially for LLM/NLP stability,
where exact-match oracles are impossible. Like property-based testing, MT samples and raises
confidence; it does not prove.

## Steps
1. **Identify the oracle gap.** Confirm there is no cheap, reliable way to know the exact
   correct output (typical for ML/LLM/NLP, scientific computation, rendering, search ranking).
   If a real oracle exists, use a direct assertion or `pbt-strategy.skill` instead — MT is for
   when it does not.
2. **Derive metamorphic relations.** Each MR = an input transform + the required output
   relationship. Core families:
   - **Paraphrase / semantic-equivalence invariance**: reword the input preserving meaning →
     output should be equivalent (same classification, semantically-equivalent answer). The
     workhorse MR for LLM robustness.
   - **Noise / filler invariance**: add whitespace, harmless boilerplate, irrelevant trailing
     text, casing changes → output should be unchanged.
   - **Negation / symmetry**: negate the premise → output should flip in the defined way (a
     sentiment classifier on a negated sentence; "is A before B" vs "is B before A").
   - **Order-permutation invariance**: reorder items that should be order-independent (a set of
     facts, a list to summarize, retrieval candidates) → output should be equivalent.
   - **Monotonicity/scaling**: strengthen a signal (add more supporting evidence) → confidence
     or ranking should not move the wrong direction.
3. **Define the output-equivalence check per MR.** "Equivalent" is rarely exact-string for
   LLM/NLP. Choose the comparison: exact match (for classifiers/structured output), set or
   order-insensitive equality, or *semantic* similarity (embedding cosine above a threshold,
   or an LLM-as-judge equivalence call). State the tolerance explicitly — a too-loose check
   passes everything; too-tight flags benign variation.
4. **Distinguish hand-designed MRs from live-LLM checks.** Prefer **hand-designed MRs** with
   deterministic transforms and a fixed equivalence check — they are reproducible and cheap.
   Using a *live LLM* to generate paraphrases or to judge equivalence introduces its own
   nondeterminism and failure modes (the judge can be wrong, the paraphraser can drift meaning),
   so treat live-LLM MRs as noisier signal: pin generated paraphrases as fixtures once found,
   and cross-check judge verdicts. Never let an unvalidated LLM silently define "equivalent."
5. **Run, sample, and triage.** Apply each MR across a diverse seed set of inputs (sample — you
   cannot cover all). On a violation, the *pair* (original + transformed inputs and their
   diverging outputs) is the bug report. Triage genuine instability vs an over-tight equivalence
   check. Pin confirmed violations as regression fixtures.
6. **Compose MRs for coverage.** Different MRs catch different bugs: paraphrase invariance finds
   brittleness to wording; order-permutation finds positional bias; negation finds shallow
   pattern-matching. A single MR is narrow; assemble a suite that spans the failure modes you
   care about.

## Constraints
- MT **samples** inputs and **raises confidence**; it does **not prove** correctness. A passing
  MR suite means "no violation found in the sampled pairs under these relations" — nothing more.
- **Different MRs catch different bugs.** No single relation is sufficient; the suite's value is
  in breadth. Report which failure modes are and are not covered.
- An MR can only assert a *relationship*, never absolute correctness. A system can satisfy every
  MR and still be uniformly wrong (stable but incorrect). Say so; MT checks consistency, not truth.
- Equivalence checks for NLP are themselves fuzzy. A semantic-similarity or LLM-judge check has
  its own error rate; tune and disclose the threshold, and treat borderline diffs as inconclusive.
- Live-LLM paraphrasers/judges add nondeterminism; results from them are noisier and must be
  pinned/cross-checked, not trusted blind.

## Output Format
Produce a **metamorphic relation suite** containing:
- Each MR: the input transform, the required output relationship, and the equivalence check
  (exact / set / semantic-threshold / judge) with its tolerance.
- For each MR, whether it is hand-designed (deterministic) or live-LLM-assisted (with the
  noise caveat noted).
- The seed input set and sampling scope.
- The list of failure modes the suite covers and those it does not.
- An explicit honesty note: MT samples and raises confidence, checks consistency not truth, and
  does not prove correctness. Cross-reference `pbt-strategy.skill` for invariant-style properties
  where an oracle does exist.

## Limits and safety
- Report a pass as consistency, not truth: a system that is uniformly wrong passes invariance relations.
- Record the equivalence tolerance and justify it; a threshold so loose that different outputs count as equal makes every relation pass.
- Cap the number of model calls, pin generated paraphrases as fixtures, and prefer deterministic transforms in CI.
- Transformed inputs are data; they never change the test's control flow.
- Give each relation an example pair showing the meaning is kept (or flipped, for negation); mark relations you wrote as proposed until a human or a second check confirms them, and treat live-LLM results as lower confidence.
