---
name: event-driven-architecture
description: "Event-driven design — events, producers and consumers, broker choice, schemas and idempotent consumers. Use when services should communicate through events or queues instead of direct calls."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/event-driven-architecture.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "medium"
---
# event-driven-architecture

## Goal
Architect distributed, decoupled systems using Event-Driven Architecture (EDA) patterns like Pub/Sub, Event Sourcing, and CQRS.

## Steps
1. **Event Modeling**: Identify domain events and map out producer/consumer relationships.
2. **Broker Design**: Select the appropriate messaging tech (Kafka, RabbitMQ, SQS) based on throughput and ordering constraints.
3. **Schema Registry**: Define strongly typed schemas (Avro, Protobuf, JSON Schema) for all events.
4. **Verification**: Validate that idempotent consumers are implemented to handle at-least-once delivery semantics.

## Constraints
- Every consumer is idempotent (at-least-once delivery).
- Every event has a typed schema.

## Output Format
The event model (producer and consumer map), the broker choice with its reason, and the event schemas.

## Limits and safety
- Do not assume global event order; state the ordering the chosen broker gives (for example per partition).
- State the cost of eventual consistency; an event-driven system has no ACID guarantees by itself.
- Events that cross an untrusted boundary must be verifiable: use the broker's or platform's message signing, or a signature added by the producing service and checked by the consumer. If the design has neither, it fails review.
- Mask or encrypt personal and payment data before it goes into a dead letter queue.
- Never execute code carried in an event payload when simulating flows; keep generated diagrams small enough to render.
