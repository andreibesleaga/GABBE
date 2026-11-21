---
name: cost-optimization
description: Find cloud spend that can be cut (idle compute, unused storage, network, over-sized databases) and report each item with savings and risk. Use when the cloud bill grows, a FinOps review is due, or you look for unused resources.
triggers: [reduce aws bill, analyze cloud costs, find unused resources, optimize instance types, finops, cloud spend review]
tags: [ops, cloud, finops, cost]
context_cost: medium
---
# Cost Optimization Skill

## Goal
Find cloud spend that can be reduced and report it, with the saving and the risk of each change. The skill reports and recommends; it does not change resources.

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

## Constraints
- Use real billing exports or the provider's price data; do not estimate savings from remembered prices.
- Check that a resource is not a security or recovery component before calling it idle.
- The output is a report; changes to resources are made by the human or by a separate request.

## Limits and safety
- Run analysis with read-only credentials; a command that terminates, resizes or deletes a resource is proposed in the report, never run.
- Before marking a resource idle, check that it is not a standby database, a backup, a WAF or another security or recovery component.
- Check compliance tags before moving data to a cheaper tier; retention and location rules come before savings.
- Billing reports are business data: save them in the private project folder, not in a public repository.
