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

## Security & Guardrails

### 1. Skill Security
- **Data Privacy**: The sustainability audit must not leak or transmit PII when analyzing database payloads or workload sizes.

### 2. System Integration Security
- **Safe Profiling**: When measuring CPU cycles to determine energy use, the agent must use non-invasive profiling in production to prevent degrading the user experience.

### 3. LLM & Agent Guardrails
- **Measurable Advice**: The LLM must not output vague "be more green" advice. It must calculate tangible metrics (e.g., "compressing this payload by 20% saves 50GB of transfer per month, equal to X kg of CO2").
