---
name: sustainability-checks
description: Evaluate software architecture for ESG and sustainability impact
triggers: [run sustainability check, audit esg, is this green, sustainability review, science-based targets, carbon footprint]
tags: [product, sustainability, green-software, esg]
context_cost: medium
---
# sustainability-checks

## Goal
To enforce broad sustainability and Environmental, Social, and Governance (ESG) checks across the project, evaluating carbon footprint, energy efficiency of algorithms, hardware utilization, and socioeconomic impacts of the software.

## Steps
1. **Analyze Compute Intensity**: Identify the most computationally expensive algorithms, database queries, and ML model training loops.
2. **Review Data Lifecycles**: Audit caching strategies, data transfer volumes, and inactive data storage (which consume baseline energy).
3. **Hardware Lifecycle Assessment**: Review infrastructure choices. Propose shifting workloads to regions running on renewable energy or utilizing spot instances to maximize existing server uptime.
4. **Social & Governance Check**: Verify that the system does not promote systemic bias (social) and handles data transparently (governance).
5. **Reporting**: Generate a `GREEN_SOFTWARE_REPORT_TEMPLATE.md` with the Software Carbon Intensity (SCI) score estimates and actionable reduction strategies.

## Constraints
- Advice is measurable: a quantity, its unit and the calculation behind it.
- Estimates carry their inputs and a range.

## Output Format
`GREEN_SOFTWARE_REPORT_TEMPLATE.md`, filled: findings by step, SCI estimate with inputs, and ranked reduction actions.

## Limits and safety
- Do not read or copy personal data from database payloads; use counts and sizes.
- Profile production only with low-overhead sampling and the human's yes; otherwise measure in staging.
- Every advice item has a number and its calculation (for example bytes saved per month and the conversion factor with its source); no "be more green".
- SCI scores are estimates; state the inputs.
