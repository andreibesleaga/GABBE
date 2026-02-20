# Data Pipeline Design: [Pipeline Name]

**Frequency**: [Real-time / Hourly / Daily]
**Source**: [Source System]
**Destination**: [Warehouse Table]
**Owner**: [Team Name]

## 1. Overview
[Description of what data is moving and why.]

## 2. Data Flow
-   **Ingestion**: [Kafka Topic / S3 Landing Zone / API Pull]
-   **Transformation**: [Spark Job / dbt Model / SQL Stored Proc]
-   **Loading**: [Append / Merge / Overwrite]

## 3. Schema
### Source Schema
```json
{ "id": "int", "event_time": "timestamp", ... }
```

### Target Schema (Warehouse)
```sql
CREATE TABLE marts.dim_customers (
  customer_sk STRING, 
  ...
)
```

## 4. Data Quality & Validation
-   **Freshness**: Data must arrive within [X] minutes.
-   **Completeness**: [Check: row_count > 0]
-   **Uniqueness**: [Check: id is unique]
-   **Handling Bad Data**: [Dead Letter Queue / Drop / Alert]

## 5. Privacy & Governance
-   **PII Fields**: [email, phone, ip_address]
-   **Masking Strategy**: [SHA256 Hash / Drop / Tokenize]
-   **Retention**: [X Days/Years]

## 6. Orchestration
-   **Trigger**: [Schedule / Event]
-   **Dependencies**: [Upstream DAGs]
-   **Retries**: [3 retries, 5m delay]
