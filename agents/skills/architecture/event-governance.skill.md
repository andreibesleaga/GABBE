---
name: event-governance
description: Schema Registry enforcement (Avro/JSON), CloudEvents standard, and Event Evolution rules.
triggers: [event governance]
tags: [architecture]
role: prod-architect, eng-data
---
# event-governance Skill

## Goal
Events are Data Contracts. They must be governed as strictly as APIs.

## Steps
## 1. CloudEvents Standard
Use the standard envelope structure:
```json
{
  "specversion": "1.0",
  "type": "com.example.order.created",
  "source": "/service/order",
  "id": "A234-1234-1234",
  "time": "20.2.01-01T12:00:00Z",
  "datacontenttype": "application/json",
  "data": { ... }
}
```

## 2. Schema Registry
- **Rule**: All event payloads must be validated against a Schema Registry (e.g., Confluent, Glue) *before* publishing.
- **Formats**: Avro (preferred for compact/evolution), Protobuf, or JSON Schema.

## 3. Schema Evolution (Compatibility)
- **Backward Compatibility**: New consumer can read old data. (Add optional fields).
- **Forward Compatibility**: Old consumer can read new data. (Ignore unknown fields).
- **Full Compatibility**: Both.
- **Breaking Changes**: renaming fields, changing types. **Forbidden** without a new topic version (`orders.v2`).

## 4. Documentation
- Use **AsyncAPI** to document event topography.
- Treat Events as Public APIs.

## Security & Guardrails

### 1. Skill Security (Event Governance)
- **Schema Poisoning Prevention**: The Schema Registry itself is a critical security dependency. The agent must enforce that CI/CD pipelines require cryptographic signatures or strict RBAC approval before a new Schema Version (e.g., Avro `.avsc`) can be published. If an attacker can silently alter the schema to make a high-security field optional, downstream validation might fail open.
- **Dead-Letter Queue (DLQ) Containment**: The agent must stipulate that DLQs, which catch malformed or failing events, are subject to the same strict data residency and access controls as the primary topic. DLQs often accumulate edge-case data that might contain unexpected PII or raw secrets that crashed the parser.

### 2. System Integration Security
- **PII Field Pinning**: When defining backward/forward compatibility rules (Step 3), the agent must explicitly forbid the "silent deprecation" of fields tagged for security or compliance (e.g., `consent_withdrawn_timestamp`). Dropping these fields via schema evolution can cause downstream systems to violate GDPR/CCPA.
- **Event Forwarding Trust Boundaries**: If CloudEvents are forwarded across bounded contexts or network boundaries, the agent must mandate `mTLS` at the transport layer and strongly recommend payload-level encryption (e.g., AES-GCM) for sensitive fields, preventing cross-tenant data leakage in shared event brokers like Kafka.

### 3. LLM & Agent Guardrails
- **Compatibility-Over-Security Bias**: The LLM might suggest making all schema fields optional to maximize Forward/Backward compatibility. The agent must veto this for security-critical fields (e.g., `tenantId`, `authorizationRole`). Fields required for downstream authorization MUST remain strictly enforced and non-nullable.
- **Hallucinated AsyncAPI Authorization**: The LLM might generate an AsyncAPI specification that perfectly describes the message structure but entirely omits the security scheme (e.g., SASL/SCRAM or mutual TLS requirements). The agent must mathematically ensure that every produced AsyncAPI document contains an explicit `securitySchemes` definition.
