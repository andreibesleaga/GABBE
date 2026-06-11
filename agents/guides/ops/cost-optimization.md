# Cost Optimization & FinOps Guide

## Overview
Financial Operations (FinOps) is the operating model for the cloud, bringing financial accountability to the variable spend model of cloud computing. This guide provides the philosophical and technical strategies to maximize business value from your architecture.

## Principles of FinOps
1. **Teams need to collaborate**: Finance, engineering, and product teams must work together in near-real time.
2. **Decisions are driven by business value**: Unit economics (e.g., cost per transaction, cost per user) drive decisions, not just aggregate spend.
3. **Everyone takes ownership**: Engineers are responsible for the costs their architectures generate.
4. **Data must be accessible and timely**: Feedback loops on cost must be immediate to allow for quick corrections.

## Architectural Strategies for Cost Optimization

| Strategy | Description | Implementation Examples |
|---|---|---|
| **Right-Sizing** | Continuously matching instance types and sizes to workload performance and capacity requirements. | Use predictive scaling; downsize underutilized EC2/RDS instances; utilize ARM-based instances (like Graviton). |
| **Commitment Discounts** | Utilizing financial instruments for baseline loads. | Reserved Instances (RIs), Savings Plans, committed use discounts. |
| **Auto-Scaling & Elasticity** | Matching provisioned resources dynamically to actual demand. | Kubernetes HPA (Horizontal Pod Autoscaler), scaling down non-prod environments off-hours. |
| **Serverless Architectures** | Paying strictly for execution time rather than idle capacity. | Adopting AWS Lambda, Azure Functions, Cloud Run, DynamoDB (On-Demand). |
| **Storage Tiering** | Moving data to cheaper storage classes based on access frequency. | S3 Lifecycle policies (Standard -> Infrequent Access -> Glacier). |
| **Spot Instances** | Using surplus compute capacity at steep discounts for fault-tolerant workloads. | Running stateless background workers, CI/CD pipelines, or big-data processing on Spot. |

## The FinOps Lifecycle
1. **Inform**: Visibility and allocation. Implement strict resource tagging schemas. Showback/chargeback to specific business units.
2. **Optimize**: Identify specific optimizations (rightsizing, spot usage, terminating zombies).
3. **Operate**: Automate the FinOps practices. Build continuous checks into the CI/CD pipeline.

## LLM & Agentic Cost Control (the agent's own spend)

The largest variable cost of an agentic system is LLM tokens. GABBE controls this with four levers, all enforceable through the platform-control layer (`gabbe budget` / `route` / `forecast`).

### 1. Prompt caching — the highest-leverage lever
Reusing a stable prompt prefix avoids re-billing it on every call. Sources verified 2026-06-10.

- **OpenAI-compatible endpoints (GABBE default):** caching is **automatic** for prefixes ≥ **1,024 tokens** — no code change. Cached input is discounted **~50%** (more on some newer models). Cache hits appear in `usage.prompt_tokens_details.cached_tokens`. Caches expire after ~5–10 min idle (≤1h). (openai.com/index/api-prompt-caching; developers.openai.com/api/docs/guides/prompt-caching)
- **Anthropic endpoints:** opt in with `cache_control: {"type": "ephemeral"}` (5-min TTL) or `{"ttl": "1h"}`. Cache **write** costs 1.25× (5m)/2× (1h) base input; cache **read** ~**0.1×**. ≤4 breakpoints; verify via `usage.cache_read_input_tokens`. (platform.claude.com/docs/en/build-with-claude/prompt-caching)
- **Make caching work:** keep the stable content (system prompt, tool list, frozen context) FIRST and byte-identical; put volatile content (timestamps, IDs, the user's question) LAST. Silent cache-busters: `datetime.now()`/UUIDs in the system prompt, unsorted `json.dumps`, per-user IDs in the prefix, changing the tool set mid-session.
- GABBE accounts for cache hits in `gabbe/budget.py` (cached tokens billed at the cache-read rate), so `gabbe forecast` reflects the real discounted cost.

### 2. Context-window budgeting via `context_cost`
Every skill declares `context_cost: low | medium | high` (low <2k tokens, medium 2–8k, high >8k). Load the **minimum** skills/guides needed; prefer `low`-cost skills; only pull `high`-cost context when the task demands it. This caps the input tokens an agent pays for per step.

### 3. Model tiering (route cheap → escalate)
Match model power to task difficulty. `gabbe route` decides LOCAL (free/cheap local model) vs REMOTE (SOTA) by complexity + PII. Reserve the most expensive model for genuinely hard, correctness-critical work; default to the cheapest reliable tier (per the AGENTS.md *Default Cost & Budget Optimization* mandate and CONSTITUTION cost article).

### 4. Batching & off-peak
For non-latency-sensitive bulk work, async batch APIs run at **−50%** (e.g. Anthropic Message Batches). Schedule large non-interactive runs (audits, migrations, regen) as batches.

### Hard guardrails (never disabled)
`GABBE_MAX_COST_USD`, token/iteration/wall-time budgets, and hard stops bound a runaway loop regardless of the optimizations above — cost control must never weaken the quality gates, the 10-phase SDLC, or human-in-the-loop escalation.

## Automation & Agentic Checks
Use the `cost-optimization.skill.md` to autonomously:
- Generate `COST_OPTIMIZATION_REPORT_TEMPLATE.md`.
- Analyze IaC (Terraform/CloudFormation) for untagged resources or over-provisioned defaults.
- Recommend architectural shifts (e.g., "This cron job runs 24/7 on EC2; moving to Serverless framework will save 80%").
- Audit AI/LLM costs using the [Performant AI Skill](../../skills/coding/performant-ai.skill.md), applying the four LLM levers above.
