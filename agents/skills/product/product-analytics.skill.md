---
name: product-analytics
description: Design event taxonomy, funnels and retention, rigorous A/B experiments, plus DORA and SPACE delivery metrics.
triggers: [design event taxonomy, build funnel analysis, measure retention cohorts, design ab experiment, calculate minimum detectable effect, track dora four keys, space developer productivity metrics]
tags: [product, analytics, experimentation]
core: false
context_cost: medium
---
# Product Analytics

## Goal
Build a measurement system that tells the team whether the product is working and whether the delivery
engine behind it is healthy. It spans two layers: **product analytics** (a clean event taxonomy, funnels,
retention, and statistically sound A/B experiments) and **delivery metrics** (the DORA Four Keys and the
SPACE framework). The output is an analytics-and-delivery-metrics plan. The discipline throughout is rigor:
a metric you cannot trust is worse than no metric, because it produces confident wrong decisions.

## Steps
1. **Design the event taxonomy first.**
   - Define a consistent naming convention (object-action, e.g. `checkout_completed`) and a documented set
     of events and properties *before* instrumenting. A taxonomy bolted on after the fact produces
     un-joinable, untrustworthy data.
   - Capture only what answers a defined question; over-instrumentation creates noise and privacy exposure.
2. **Build funnels and retention.**
   - **Funnels**: define ordered steps toward a goal and measure conversion and drop-off at each step to
     locate where users are lost.
   - **Retention**: use cohort analysis (e.g. weekly cohorts, N-day or unbounded retention) to see whether
     value is durable — acquisition without retention is a leaking bucket.
3. **Design A/B experiments rigorously.**
   - State a falsifiable **hypothesis** and one primary metric before launch.
   - Compute the **Minimum Detectable Effect (MDE)** and required sample size from baseline rate, desired
     **power** (typically 80%), and significance level — so you know the experiment can actually detect the
     effect before you run it.
   - Define **guardrail metrics** (latency, error rate, revenue, unsubscribe) that must not regress even if
     the primary metric improves.
   - Fix the duration and decision rule in advance; do not peek and stop early on a favorable swing.
4. **Track delivery health — DORA Four Keys.**
   - **Deployment frequency**, **lead time for changes**, **change failure rate**, and **time to restore
     (MTTR)** — the four together balance throughput against stability so the team can't game one by
     sacrificing another.
5. **Measure developer experience — SPACE.**
   - Complement DORA with **SPACE** dimensions: Satisfaction, Performance, Activity, Communication, and
     Efficiency. Use multiple dimensions because any single productivity metric (e.g. raw Activity like
     commit count) is gameable and misleading alone.
6. **Assemble the plan.**
   - Combine taxonomy, product metrics, experiment design, and delivery metrics into one plan with owners
     and review cadence.

## Constraints
- Define the event taxonomy and the experiment hypothesis/primary metric *before* collecting data; the
  agent MUST NOT rationalize a metric after seeing results (HARKing) or pick a winning slice post-hoc.
- An A/B result is invalid without pre-computed power/MDE and a fixed stopping rule; the agent MUST NOT
  endorse stopping early on a favorable peek or declaring significance from an under-powered test.
- DORA and SPACE are read as balanced sets, never single numbers; the agent MUST NOT optimize one key in
  isolation (e.g. deploy frequency) at the expense of stability or developer well-being.
- Statistical results carry uncertainty; report confidence intervals, not just point lifts, and never imply
  certainty a test cannot support.

## Output Format
Produce an analytics + delivery-metrics plan containing:
- The event taxonomy: naming convention plus a table of core events and their properties.
- Funnel definitions (ordered steps) and the retention model (cohort basis, retention window).
- Per planned experiment: hypothesis, primary metric, MDE, required sample size and power, guardrail
  metrics, duration, and the pre-committed decision rule.
- The DORA Four Keys with current/target values, and the SPACE dimensions with how each is measured.
- Owners, instrumentation sources, and review cadence.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Result-shopping — the agent surfaces a favorable post-hoc segment or stops a test on a lucky
  peek; mitigation: the agent enforces the pre-registered hypothesis, primary metric, and stopping rule and
  reports any deviation as exploratory-only, not confirmatory.
- **Risk**: Metric gaming — a single DORA or SPACE figure (deploy count, commits) is optimized in isolation;
  mitigation: the agent MUST present the balanced metric set and flag movements that improve one key while
  degrading a counterbalancing one.

### 2. System Integration Security
- **Risk**: PII and over-collection in events — the taxonomy captures raw emails, precise location, or other
  sensitive fields by default; mitigation: the agent instruments only question-driven events, excludes or
  hashes sensitive properties, and notes the lawful basis and retention for each.
- **Risk**: Experiment exposure of vulnerable users — an A/B test routes harmful or untested experiences to
  real users without guardrails; mitigation: the agent requires guardrail metrics and a kill-switch before
  ramp and excludes experiments that could materially harm a user segment.

### 3. LLM & Agent Guardrails
- **Risk**: Correlation-as-causation — the model reads an observational funnel change as proof a feature
  caused it; mitigation: the agent distinguishes correlational from controlled-experiment evidence and
  attaches confidence intervals rather than asserting a causal point lift.
- **Risk**: Surveillance creep — instrumentation drifts toward tracking individuals across unrelated contexts
  to "improve analytics"; mitigation: the agent refuses event designs whose value depends on covert
  cross-context tracking and keeps collection scoped to the stated product question.
