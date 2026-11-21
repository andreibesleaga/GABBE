---
name: empirical-methods
description: "Designs a measurement or experiment (metric, hypothesis, controls, sample size) and reports results with effect size and confidence interval. Use when comparing benchmarks, reading A/B results, choosing a metric or tracing a root cause."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/empirical-methods.skill.md"
  tags: "core, measurement, experimentation, statistics"
  core: "false"
  context_cost: "medium"
---
# Empirical Methods

## Goal
Bring empirical rigor to engineering decisions so that claims about performance, quality, or user behavior
rest on evidence rather than intuition. This skill operationalizes the empirical-methods strand of the
SWEBOK v4 "Engineering Foundations" knowledge area: measurement theory (scales, validity, reliability),
hypothesis and experiment design (design of experiments, controls, confound management), honest statistical
interpretation of benchmarks and A/B results (significance, effect size, confidence intervals), and
root-cause analysis as an engineering method. It pairs with the skills that gather the raw numbers —
`system-benchmark.skill` for performance measurement and `product-analytics.skill` for user-behavior
metrics — and ties its experiment artifact to `EXPERIMENT_PLAN_TEMPLATE.md`.

## Steps
1. **Define the measurement before measuring.**
   - State the **construct** you want to know about and the concrete metric that operationalizes it. Pick the
     right **scale** (nominal, ordinal, interval, ratio) because the scale bounds which statistics are
     legitimate (you cannot average ordinal ranks meaningfully). Check **validity** (does the metric measure
     the construct?) and **reliability** (does it give consistent results on repeat?). A precise-but-invalid
     metric is worse than an honest rough one.
2. **Frame a falsifiable hypothesis.**
   - Write a null and an alternative hypothesis in advance, plus the decision rule and the practically
     meaningful effect size *before* looking at data. Pre-registering the hypothesis and stopping rule
     prevents fishing for whatever turns out significant.
3. **Design the experiment.**
   - Apply design-of-experiments thinking: isolate the independent variable, hold others constant or
     randomize them, use a **control** group, and identify **confounds** (warm-up effects, caching, time of
     day, population skew) and how each is controlled. Decide sample size from the smallest effect worth
     detecting, not from convenience.
4. **Run and record honestly.**
   - Capture the full environment, the raw measurements (not just summaries), variance, and any anomalies or
     discarded runs with the reason. Reproducibility requires that another engineer could repeat the setup
     from the record alone.
5. **Interpret statistics with guardrails.**
   - Report **effect size** and a **confidence interval**, not just a p-value: statistical significance is
     not practical importance, and a tiny p-value on a trivial effect changes nothing. State the confidence
     level and what the interval actually means. Most importantly, **correlation is not causation** — only a
     controlled, randomized design licenses a causal claim; observational data yields association plus
     candidate confounds, no more.
6. **Run root-cause analysis when something fails.**
   - Treat a failure or surprising result as an empirical question: form hypotheses for the cause, test each
     against evidence (logs, metrics, bisection, controlled reproduction), and distinguish the confirmed root
     cause from contributing factors and from mere correlates. Stop at the cause you can demonstrate, not the
     first plausible story.

## Constraints
- The agent MUST report effect size and a confidence interval alongside any significance claim, and MUST NOT
  present a p-value alone as proof a change "works."
- Causal language is reserved for controlled, randomized designs; for observational or A/B data with
  uncontrolled confounds the agent states association only and lists the plausible confounds.
- The metric and scale are fixed before measurement; the agent does not switch metrics or stopping rules
  after seeing data, and flags any post-hoc analysis as exploratory, not confirmatory.
- Raw data and environment are recorded for reproducibility; a result that cannot be reproduced from the
  record is reported as preliminary.
- Honesty over narrative: the agent reports negative, null, and inconclusive results plainly rather than
  reframing them as wins.

## Output Format
Produce an experiment/measurement design (aligned to `EXPERIMENT_PLAN_TEMPLATE.md`) containing:
- The construct, the operational metric, its scale, and validity/reliability notes.
- The null and alternative hypotheses, the practically meaningful effect size, the sample-size rationale, and
  the pre-declared stopping rule.
- The design: independent variable, controls, randomization, and the identified confounds with their
  mitigations.
- An **interpretation guardrail block**: how results will be reported (effect size + confidence interval),
  the explicit reminder that significance is not importance and correlation is not causation, and the
  conditions under which a causal claim would be justified.
- For diagnostic use, a root-cause section separating confirmed cause from contributing factors and
  correlates.

## Limits and safety
- Fix the hypothesis, metric and stopping rule before looking at data; any later slice is labelled "exploratory".
- Report effect size, interval and variance; never a p-value alone, and no causal claim without a controlled, randomised design.
- Record data source, environment and discarded runs; a result that cannot be reproduced from the record is called preliminary.
- An experiment on production traffic needs a guardrail metric, a size limit and the human's yes first.
