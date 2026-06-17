# Estimation Worksheet: [Project / Feature Name]

**Date:** [YYYY-MM-DD]
**Estimator(s):** [names or roles]
**Status:** Draft | Reviewed | Final

---

## 1. Scope

**In scope:** [What work is being estimated? e.g., "Backend API + DB migration for the new billing module".]
**Out of scope:** [What is explicitly NOT included? e.g., "Frontend UI, third-party tax integration".]
**Assumptions baked into this estimate:** [List the load-bearing assumptions; if one breaks, the estimate breaks.]

---

## 2. Method

Pick one (or combine) and justify:

| Method | When to use | Selected? |
|---|---|---|
| Reference-class forecasting | Similar past projects exist to anchor against | [Yes/No] |
| Story points (relative) | Team has a stable velocity baseline | [Yes/No] |
| T-shirt sizing (XS–XL) | Early/coarse; no detailed breakdown yet | [Yes/No] |

**Justification:** [Why this method fits the current uncertainty and available data.]

---

## 3. Per-Item Estimates

P50 = "as likely to finish before as after." P90 = "90% chance we finish by this." The P90/P50 gap is the risk premium.

| Item | Size | P50 | P90 | Confidence | Assumptions |
|---|---|---|---|---|---|
| [Task / story] | [XS–XL or pts] | [e.g. 2d] | [e.g. 5d] | [Low/Med/High] | [Key assumption] |
| [Task / story] | [ ] | [ ] | [ ] | [ ] | [ ] |
| [Task / story] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 4. Cone of Uncertainty

<!-- Early estimates can be off by 4x in either direction; the range narrows only as work is done.
     Record WHERE on the cone this estimate sits so readers calibrate trust. -->

**Phase:** [Concept / Requirements-set / Design-complete / In-progress]
**Expected error band at this phase:** [e.g. "0.5x to 2x" early; "0.8x to 1.25x" mid-flight]
**What would tighten the cone:** [Spikes, prototypes, or decisions that would reduce uncertainty.]

---

## 5. Total Range

| Roll-up | Optimistic (sum P50) | Realistic (P90-weighted) | Pessimistic (sum P90) |
|---|---|---|---|
| Effort | [ ] | [ ] | [ ] |
| Calendar (with WIP/parallelism) | [ ] | [ ] | [ ] |

**Stated range:** [e.g. "3–6 weeks, most likely 4."]

---

## 6. Honesty Note

> An estimate is a probability range, not a commitment or a deadline.
> Reporting a single number hides the risk. Always present the range and the
> confidence behind it. If a date is needed, derive it from the P90 plus an
> explicit buffer — and say so out loud.
