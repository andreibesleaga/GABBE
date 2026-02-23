---
name: cost-optimization
description: Cloud cost analysis and optimization (FinOps)
triggers: [Reduce AWS bill, Analyze cloud costs, Find unused resources, Optimize instance types, finops]
tags: [ops, cloud, finops, cost]
context_cost: medium
---
# Cost Optimization Skill

## Goal
## Steps

### 1. Analysis Areas
1.  **Compute**: Idle EC2s? Over-provisioned Lambda memory?
2.  **Storage**: Unused EBS volumes? Old S3 data not in Glacier?
3.  **Network**: Excessive NAT Gateway charges? Cross-AZ traffic?
4.  **Database**: Over-provisioned IOPS? Idle RDS instances?

## Output Format
Produce a **Cost Optimization Report** detailing:
- Resource ID
- Current Cost/Month
- Recommended Action (Resize/Terminate/Archive)
- Estimated Savings
- Risk Level (Low/Medium/High)

## Security & Guardrails

### 1. Skill Security (Cost Optimization)
- **Non-Destructive Scanning**: The FinOps analysis scripts execution environment must be strictly bound to **ReadOnlyAccess** IAM roles. The agent cannot have the ability to terminate instances or modify auto-scaling groups while gathering cost metrics.
- **Cost Data Privacy**: Detailed billing reports can leak business strategies, customer acquisition costs, or exact scaling metrics. The agent must ensure generated reports are saved securely and never exposed in public repositories or logs.

### 2. System Integration Security
- **Security Dependency Recognition**: Before flagging a resource as "idle" or "waste" for termination, the agent must verify it isn't a critical security appliance (e.g., a passive WAF, a cold-standby disaster recovery database, or an empty Security Hub bucket).
- **Compliance Scope Awareness**: When recommending moving old data to cheaper storage tiers (like S3 Glacier), the agent must query data compliance tags. Regulated data (HIPAA/GDPR) might have strict retention or location policies that supersede cost savings.

### 3. LLM & Agent Guardrails
- **Optimization Hallucination Avoidance**: The LLM must not guess or estimate potential savings using outdated pricing tables. It must ground its math directly on real-time API pricing queries or provided billing exports.
- **Termination Action Guardrails**: The agent must violently reject any user prompt like "Go ahead and delete all the instances you marked as high risk to save money." Output must strictly be constrained to *Reporting* and *Recommendations*.
