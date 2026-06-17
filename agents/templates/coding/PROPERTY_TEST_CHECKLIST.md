# Property-Based & Metamorphic Test Checklist: [Component / Module Name]

**Date:** [YYYY-MM-DD]
**Author:** [name]
**Status:** Draft | Reviewed

<!-- Property-based tests assert that invariants hold across MANY generated
     inputs. Metamorphic tests assert RELATIONS between outputs when inputs are
     transformed. Use this checklist to make sure the test is actually testing
     properties, not just one example. -->

---

## 1. Invariants Identified

| # | Invariant (always true) | Holds for which inputs |
|---|---|---|
| 1 | [e.g. "encode then decode returns the original"] | [all valid inputs] |
| 2 | [e.g. "output list is always sorted"] | [ ] |

- [ ] At least one round-trip / inverse property considered.
- [ ] At least one "never crashes / always well-formed" property considered.

---

## 2. Generators / Strategies

| Input | Generator / strategy | Edge cases forced |
|---|---|---|
| [param] | [e.g. integers, text, composite builder] | [empty, max, unicode, negative] |

- [ ] Generators cover the full valid domain (not just happy values).
- [ ] Boundary and degenerate cases are reachable.
- [ ] Invalid inputs handled by a separate negative property where relevant.

---

## 3. Stateful / Model-Based Machine (if applicable)

- [ ] Rules / commands defined for each operation.
- [ ] `@invariant`-style checks assert system consistency after every step.
- [ ] Model (oracle) compared against the real implementation.
- [ ] Preconditions guard illegal command sequences.

---

## 4. Shrinking

- [ ] Failures shrink to a minimal counterexample.
- [ ] Shrunk examples are human-readable and reproducible (seed recorded).
- [ ] No custom type defeats shrinking (custom strategies still shrink).

---

## 5. Metamorphic Relations

| # | Transformation on input | Expected relation on output |
|---|---|---|
| 1 | [e.g. "permute input order"] | [e.g. "result unchanged"] |
| 2 | [e.g. "scale all inputs by k"] | [e.g. "result scales by k"] |
| 3 | [e.g. "add an irrelevant record"] | [e.g. "decision unchanged"] |

---

## 6. Honesty Note

> Property tests SAMPLE the input space; they do not PROVE correctness.
> A green run means "no counterexample found in N cases," not "always correct."
> Record the case count and seed, and treat a pass as strong evidence, not proof.

---

## 7. CI Marker

- [ ] Test tagged with the right marker: [`slow` / `live_llm` / default].
- [ ] Long-running property runs gated out of the fast PR lane if needed.
- [ ] Seed / example database committed so failures are reproducible in CI.
