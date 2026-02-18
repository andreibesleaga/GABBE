---
name: enterprise-integration
description: Design integrations with ERP/CRM systems and modernize legacy applications.
context_cost: medium
---
# Enterprise Integration Skill

## Triggers
- integration
- erp
- crm
- sap
- salesforce
- legacy
- middleware
- esb
- kafka
- message bus
- event bus

## Purpose
To solve complex integration challenges between modern apps and enterprise systems of record.

## Capabilities

### 1. Integration Patterns (EIP)
-   **Messaging**: Publish-Subscribe, Point-to-Point, Dead Letter Channel.
-   **Transformation**: Content Enricher, Message Translator (XML <-> JSON).
-   **Resilience**: Circuit Breaker, Retry with Exponential Backoff.

### 2. Legacy Modernization
-   **Strangler Fig**: incrementally replacing legacy functionality.
-   **Anti-Corruption Layer (ACL)**: preventing legacy model bleed.
-   **Change Data Capture (CDC)**: streaming DB changes (Debezium).

### 3. ERP/CRM Connectivity
-   **Salesforce**: REST/SOAP API, Bulk API, Platform Events.
-   **SAP**: OData services, IDoc, BAPI.
-   **Workday/NetSuite**: SOAP/REST integrations.

## Instructions
1.  **Decouple**: Use async messaging (Kafka/RabbitMQ) where possible.
2.  **Protect**: Always use an Anti-Corruption Layer when talking to legacy.
3.  **Trace**: Ensure correlation IDs are passed across all systems.
4.  **Buffer**: Use queues to handle burst loads without crashing legacy systems.

## Deliverables
-   Integration Architecture Diagrams (Mermaid).
-   Adapter/ACL code.
-   OpenAPI specs for facade APIs.
