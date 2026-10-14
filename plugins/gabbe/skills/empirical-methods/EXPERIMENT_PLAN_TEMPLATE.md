# A/B Experiment Plan: [Experiment Name]

**Date:** [YYYY-MM-DD]
**Owner:** [name]
**Reviewers:** [data science / PM]
**Status:** Draft | Approved | Running | Concluded

---

## 1. Hypothesis

<!-- State it as a falsifiable prediction with a direction and a mechanism. -->

> We believe that [change] will cause [primary metric] to [increase/decrease]
> by [expected effect] because [reasoning / user insight].

**Null hypothesis:** [No difference in primary metric between variants.]

---

## 2. Metrics

### Primary metric (the decision metric)
| Metric | Definition | Baseline | MDE (min. detectable effect) |
|---|---|---|---|
| [e.g. conversion rate] | [Exact computation] | [current value] | [smallest effect worth detecting, e.g. +2% rel] |

### Guardrail metrics (must not regress)
| Metric | Definition | Acceptable bound |
|---|---|---|
| [e.g. page latency] | [ ] | [no worse than +X] |
| [e.g. error rate / refunds] | [ ] | [ ] |

---

## 3. Sample Size & Power

| Parameter | Value |
|---|---|
| Significance level (α) | [e.g. 0.05] |
| Power (1−β) | [e.g. 0.80] |
| Baseline rate | [ ] |
| MDE | [ ] |
| Required sample / variant | [computed N] |
| Expected traffic / day | [ ] |
| Estimated runtime to reach N | [ ] |

---

## 4. Variants

| Variant | Description | Traffic allocation |
|---|---|---|
| Control (A) | [Current experience] | [e.g. 50%] |
| Treatment (B) | [Changed experience] | [e.g. 50%] |

**Randomization unit:** [user / session / account]
**Targeting / eligibility:** [Who is included; who is excluded.]

---

## 5. Duration

**Planned start:** [YYYY-MM-DD]
**Minimum runtime:** [≥ one full business cycle, usually ≥ 1–2 weeks to avoid day-of-week bias.]
**Stop conditions:** [Reach N AND minimum runtime; no early peeking unless using a sequential test.]

---

## 6. Decision Rule

<!-- Decide the rule BEFORE seeing data, to avoid p-hacking. -->

- **Ship B if:** primary metric improves by ≥ MDE with p < α AND no guardrail breached.
- **Keep A if:** no significant lift, or any guardrail regresses.
- **Inconclusive:** [What to do — extend, iterate, or abandon.]

---

## 7. Rollout / Rollback

**Rollout on win:** [Ramp plan, e.g. 50% → 100% over N days with monitoring.]
**Rollback trigger:** [Guardrail breach or SEV — how to kill the experiment fast.]
**Kill switch:** [Flag name / mechanism.]
