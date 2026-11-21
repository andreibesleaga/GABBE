---
name: system-qualities
description: Measurable quality requirements (SLIs and SLOs) mapped to architecture decisions. Use when requirements say "fast" or "reliable" without numbers, or when SLAs must be set.
triggers: [define NFRs, analyze system qualities, set SLAs]
tags: [architecture]
context_cost: low
---
# system-qualities

## Goal
Elicit, define, and enforce system Quality Attributes (NFRs) such as performance, scalability, reliability, and security metrics.

## Steps
1. **Elicitation**: Parse the `PRD_TEMPLATE.md` to map business goals to technical NFRs.
2. **Definition** (for the iterative design method that consumes these, see `attribute-driven-design.skill`): Use the `QUALITY_ATTRIBUTES_TEMPLATE.md` to specify exact Service Level Indicators (SLIs) and Service Level Objectives (SLOs).
3. **Mapping**: Map these NFRs to architectural decisions (e.g., caching for latency, redundancy for availability).
4. **Verification**: Verify that the chosen architecture patterns theoretically support the required SLOs.

## Constraints
- Every requirement is measurable (SLI, SLO, unit).
- Each requirement maps to an architecture decision.

## Output Format
`QUALITY_ATTRIBUTES_TEMPLATE.md` (`templates/architecture/`) filled in with SLIs, SLOs and the mapping.

## Limits and safety
- Do not lower an agreed SLO without the human's reason and yes.
- Security and compliance are first-tier quality requirements, with measurable logging and retention rules.
- Do not promise 100 percent availability or zero latency; every requirement has a measure and a unit, and a vague one is rejected.
