---
name: enterprise-integration
description: Design integrations with ERP/CRM systems and modernize legacy applications.
triggers: [integration, erp, crm, sap, salesforce, legacy, middleware, esb, kafka, message bus, event bus]
tags: [ops]
context_cost: medium
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
4.  **Buffer**: Use queues to handle burst loads without crashing legacy systems.

## Deliverables
-   Integration Architecture Diagrams (Mermaid).
-   Adapter/ACL code.
-   OpenAPI specs for facade APIs.

## Security & Guardrails

### 1. Skill Security (Enterprise Integration)
- **Payload Sanitization (ACL)**: The Anti-Corruption Layer must not just translate data schemas; it must aggressively sanitize and strip dangerous execution payloads (e.g., XML External Entity injection (XXE), SQLi) originating from opaque legacy systems.
- **Integration Configuration Protection**: Connection strings, API keys, and certificate paths for enterprise systems (SAP, Salesforce) must be injected via secure Vaults at runtime, never hardcoded in the adapter logic or the workflow repository.

### 2. System Integration Security
- **Mutual Authentication (mTLS)**: All cross-system Enterprise Service Bus (ESB) or Message Broker communication must be secured with mTLS to prevent Man-in-the-Middle (MitM) attacks and ensure strict identity attestation between integration points.
- **Data Governance Boundaries**: Event payloads pushed to shared messaging queues (e.g., Kafka) must scrub regulated PII (GDPR/HIPAA) or employ field-level encryption to prevent unauthorized downstream consumers from reading sensitive enterprise data by default.

### 3. LLM & Agent Guardrails
- **Legacy Credential Harvesting Defense**: Agents interacting with legacy SOAP/REST APIs must never cache basic authentication headers or legacy token strings in episodic memory or audit logs where they might be inadvertently exposed.
- **Facade Over-Privilege Warning**: If asked to design a REST API facade over a legacy system, the agent must explicitly advocate for narrow, least-privilege endpoints. It must refuse instructions to create a direct SQL-pass-through endpoint that exposes the entire legacy database to the web.
