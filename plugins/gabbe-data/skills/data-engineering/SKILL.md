---
name: data-engineering
description: "Pipeline and warehouse design — ELT, orchestration, dbt models, idempotent loads, data quality checks and PII handling. Use when data must be moved or transformed for analytics, or when a pipeline is unreliable."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/data/data-engineering.skill.md"
  tags: "data"
  core: "false"
  context_cost: "medium"
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

## Output Format
-   `dags/` for Airflow.
-   `models/` for dbt.
-   `spark_jobs/` for PySpark.

## Constraints
- Every pipeline is idempotent: a re-run does not duplicate data.
- Every pipeline has validation steps (Great Expectations or dbt tests).

## Limits and safety
- Credentials come from a secret manager, never from DAGs or dbt models; grep for them before handing over.
- Mask or hash personal data at ingestion, before it lands in the warehouse.
- Test with read-only roles; writes go only to named staging or target schemas.
- Run generated SQL, DAGs and Spark jobs first on a copy or sample, never on production tables.
- Data moves over encrypted transport, and pipeline runs and schema changes are logged.
