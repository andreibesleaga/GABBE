# Cost Optimization Report
**Date:** [YYYY-MM-DD]
**Scope:** [AWS/GCP/Azure/All]
**Reviewer:** [Agent Name]

## Executive Summary
| Total Spend/Month | Estimated Waste | Potential Savings | ROI |
|---|---|---|---|
| $X,XXX | $XXX | $XXX | X% |

## 1. Idle Resources (Immediate Action)
These resources are running but unused (CPU < 5% for 7 days).

| Resource ID | Service | Cost/Month | Recommendation | Savings |
|---|---|---|---|---|
| `i-0123456789` | EC2 | $45.00 | Terminate | $45.00 |
| `vol-0987654` | EBS | $12.00 | Snapshot & Delete | $11.50 |

## 2. Over-Provisioned Resources
These resources are used, but larger than necessary.

| Resource ID | Service | Current Size | utilization | Recommended Size | Savings |
|---|---|---|---|---|---|
| `db-prod-01` | RDS | db.r5.2xlarge | 12% Max CPU | db.r5.large | $350.00 |

## 3. Storage Optimization
Data that can be moved to colder storage.

| Bucket Name | Total Size | Current Class | Recommendation | Est. Savings |
|---|---|---|---|---|
| `logs-2023` | 5 TB | Standard | Glacier Deep Archive | $110.00 |

## 4. Architecture Modernization (Long Term)
- Switch [Service A] to Lambda/Serverless?
- Use Spot Instances for [Workload B]?

## Action Plan
1. [ ] Terminate idle resources (Risk: Low)
2. [ ] Resize RDS instance (Risk: Medium - requires maintenance window)
3. [ ] Apply Lifecycle Policy to S3 buckets (Risk: Low)
