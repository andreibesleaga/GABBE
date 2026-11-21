# Assurance Plan: [Project Name]

**Date:** [YYYY-MM-DD]
**Author:** [name]
**Status:** Draft | Approved by human

<!-- Filled at S01/S02 by assurance-ladder.skill (agents/skills/coding/assurance-ladder.skill.md).
     Level 0 always; level 1 default for new code with logic; level 2 and 3 need the human's approval.
     The plan adds evidence to quality gates G1-G9; it never replaces a gate. -->

## 1. Level per component

| Component | Level (0-3) | Trigger (from requirement or code) | Reason | Techniques | Phase |
|---|---|---|---|---|---|
| [name] | [1] | [pure logic / concurrency / money / authorisation / safety core] | [one sentence] | [property tests, contracts, fuzz, mutation floor] | [S05, S06] |

## 2. Thresholds the human set

| Item | Value | Set by, date |
|---|---|---|
| Mutation-score floor on changed code | [percent] | [name, date] |
| Fuzz budget per target in CI | [seconds] | [name, date] |
| Model-check bounds | [e.g. 3 nodes, 10 steps] | [name, date] |

## 3. Frozen paths (the implementing agent may not edit)

- [tests/properties/**]
- [models/*.qnt or *.tla]
- [spec files for proofs]

## 4. Evidence locations

| Component | Evidence (file or log) | Command that reproduces it |
|---|---|---|
| [name] | [project/assurance/<component>/...] | [exact command] |

## 5. Human approval (required for every component above level 1)

- [ ] Levels above 1 approved. `AUDIT_LOG.md` row `HUMAN_APPROVED`: [date, phase, the human's words]
- [ ] Specifications (invariants, proof claims) reviewed by the human: [date]

## 6. Result per component

| Component | Level planned | Level reached | Claim narrowed? (what, why, who agreed) |
|---|---|---|---|
| [name] | [ ] | [ ] | [ ] |
