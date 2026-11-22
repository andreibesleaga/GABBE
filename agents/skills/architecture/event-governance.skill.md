---
name: event-governance
description: Rules for events as data contracts — CloudEvents envelope, schema registry checks, compatibility rules and AsyncAPI documentation. Use when event schemas change or several teams consume the same topics.
triggers: [event governance, schema registry, cloudevents, asyncapi, avro schema evolution]
tags: [architecture]
role: prod-architect, eng-data
context_cost: low
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
  "time": "2020-01-01T12:00:00Z",
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

## Constraints
- Payloads are validated against the registry before publishing.
- A breaking change needs a new topic version.

## Output Format
The CloudEvents envelope definition, the registry schemas and an AsyncAPI document of the topics.

## Limits and safety
- Publishing a schema version goes through review. If your platform provides CI approval or registry access control, use it so nobody changes a schema silently.
- Never make fields needed for authorization (tenant id, role) or compliance (consent timestamps) optional, and never drop them through schema evolution.
- Dead letter queues have the same access and retention rules as the main topic.
- Every AsyncAPI document has `securitySchemes`; check with grep.
- Events that cross a boundary use authenticated transport, and sensitive fields are encrypted.
