---
name: data-engineering
description: Design and implement data pipelines (ETL/ELT), warehousing, and analytics engineering.
triggers: [data pipeline, etl, elt, spark, airflow, dbt, warehouse, big data, sql optimization, kafka]
tags: [data]
context_cost: medium
---
# Data Engineering Skill

## Goal
To assist with moving, transforming, and storing data at scale for analytics and AI.

## Capabilities

### 1. Data Pipelines (ETL/ELT)
-   **Orchestration**: Airflow DAGs, Prefect flows, Dagster.
-   **Processing**: Spark (PySpark) jobs, Python scripts (Polars/Pandas).
-   **Ingestion**: Kafka consumers, Kinesis, File watchers.

### 2. Analytics Engineering (dbt)
-   **Modeling**: Staging -> Intermediate -> Marts (Star Schema).
-   **Testing**: `unique`, `not_null`, custom dbt tests.
-   **Documentation**: `schema.yml` descriptions.

### 3. Warehousing (Snowflake / BigQuery / Redshift)
-   **Schema Design**: OBT (One Big Table) vs Star Schema.
-   **Optimization**: Partitioning, Clustering, Materialized Views.
-   **Cost Control**: Slot management, auto-suspend.

## Steps
1.  **Pattern Selection**: Prefer ELT (Load -> Transform in Warehouse) for modern stacks.
2.  **Idempotency**: All pipelines must be re-runnable without duplicating data.
3.  **Data Quality**: Always include data validation steps (Great Expectations / dbt tests).
4.  **Privacy**: Identify and hash PII (GDPR/CCPA compliance).

## Deliverables
-   `dags/` for Airflow.
-   `models/` for dbt.
-   `spark_jobs/` for PySpark.

## Security & Guardrails

### 1. Skill Security (Data Engineering)
- **Credential Protection**: Never hardcode database or warehouse credentials in DAGs or dbt models. Use Secret Managers (e.g., AWS Secrets Manager, HashiCorp Vault).
- **Least Privilege Access**: ETL/ELT service accounts should only have read access to source systems and write access to specific staging/target schemas.
- **Data Masking**: Implement dynamic data masking or hashing for PII during the ingestion phase before it lands in the warehouse.

### 2. System Integration Security
- **Secure Transport**: Ensure all data movement between source systems, message brokers (Kafka), and the warehouse is encrypted in transit (TLS 1.2+).
- **Network Isolation**: Run processing nodes (Spark clusters, Airflow workers) in private subnets with no direct internet access.
- **Audit Logging**: Log all pipeline executions, data volume changes, and schema modifications for compliance tracking.

### 3. LLM & Agent Guardrails
- **Prompt Injection Defense**: If using LLMs to generate SQL or dbt models from natural language, sanitize inputs to prevent injection of malicious commands (e.g., `DROP TABLE`).
- **Read-Only Agent Access**: Agents generating or testing pipelines must operate with read-only database roles unless executing explicitly approved migrations.
- **Output Validation**: LLM-generated code (Airflow DAGs, PySpark scripts) must be statically analyzed for security flaws and executed in a sandboxed environment before deployment.
