---
name: enterprise-integration
description: "Design integrations between a modern app and ERP, CRM or legacy systems - messaging patterns, anti-corruption layer, strangler fig, CDC, facade APIs. Use when you connect to SAP, Salesforce or a legacy system, or add a message bus."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/enterprise-integration.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# Enterprise Integration Skill

## Goal
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

## Steps
1.  **Decouple**: Use async messaging (Kafka/RabbitMQ) where possible.
2.  **Protect**: Always use an Anti-Corruption Layer when talking to legacy.
3.  **Trace**: Ensure correlation IDs are passed across all systems.
4.  **Buffer**: Use queues to handle burst loads without crashing legacy systems. For queue retries and dead-letter handling see `queue-management.skill`.

## Deliverables
-   Integration Architecture Diagrams (Mermaid).
-   Adapter/ACL code.
-   OpenAPI specs for facade APIs.

## Constraints
- Every call to a legacy system goes through the anti-corruption layer; no legacy model leaks into the new code.
- Every message carries a correlation id.

## Output Format
The files named under Deliverables: a Mermaid integration diagram, adapter and anti-corruption layer code, and the OpenAPI spec of any facade API.

## Limits and safety
- Validate and sanitise data coming from legacy systems in the anti-corruption layer; turn off external entity resolution when parsing XML.
- Connection strings, keys and certificate paths come from the secret store at run time, not from adapter code or the repository.
- Mask or leave out personal data in events on shared topics, or use field-level encryption; list the consumers of each topic.
- A facade over a legacy system exposes narrow endpoints only; refuse a SQL pass-through endpoint.
- Do not store basic-auth headers or legacy tokens in memory files or audit logs.
