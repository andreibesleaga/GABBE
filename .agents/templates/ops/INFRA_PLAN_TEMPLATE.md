# Infrastructure Plan: [System Name]

**Status**: [Draft/Review/Approved]
**Cost Estimate**: [$X/month]
**Cloud Provider**: [AWS/GCP/Azure]

## 1. High-Level Architecture
[Insert Diagram Link]

## 2. Compute Strategy
-   **Workload Type**: [Stateless Web / Batch / Stateful DB]
-   **Service**: [EKS / Lambda / EC2 / CloudRun]
-   **Scaling**: [HPA settings / Auto-scaling Group rules]

## 3. Data Storage
-   **Relational**: [RDS Postgres / Cloud SQL]
-   **NoSQL**: [DynamoDB / Firestore]
-   **Object Storage**: [S3 / GCS]
-   **Backup Policy**: [PITR retention period, Snapshot frequency]

## 4. Networking & Security
-   **VPC**: [CIDR blocks, Subnet layout]
-   **Exposure**: [Public ALB / Private Link]
-   **WAF**: [Rulesets enabled]
-   **IAM**: [Key roles and policies]

## 5. Observability
-   **Logs**: [CloudWatch / Datadog]
-   **Metrics**: [Prometheus / CloudWatch]
-   **Tracing**: [OpenTelemetry / X-Ray]

## 6. Cost Analysis
| Resource | Count | Type | Est. Cost |
|---|---|---|---|
| EC2 | 2 | t3.medium | $30 |
| RDS | 1 | db.t3.medium | $60 |
| **Total** | | | **$90** |
