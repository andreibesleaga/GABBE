---
name: event-driven-architecture
description: Design and implement Event-Driven and Async Architectures
triggers: [design event-driven system, implement eda, setup message broker topology]
tags: [architecture]
context_cost: medium
---
# event-driven-architecture

## Goal
Architect distributed, decoupled systems using Event-Driven Architecture (EDA) patterns like Pub/Sub, Event Sourcing, and CQRS.


## Steps
1. **Event Modeling**: Identify domain events and map out producer/consumer relationships.
2. **Broker Design**: Select the appropriate messaging tech (Kafka, RabbitMQ, SQS) based on throughput and ordering constraints.
3. **Schema Registry**: Define strongly typed schemas (Avro, Protobuf, JSON Schema) for all events.
4. **Verification**: Validate that idempotent consumers are implemented to handle at-least-once delivery semantics.

## Security & Guardrails

### 1. Skill Security
- **Schema Poisoning**: Prevent the skill from executing dynamic code attached to event payloads when simulating event flows.
- **Topology Overload**: Limit the visual diagram generation (e.g., Mermaid) to prevent generating massively complex graphs that crash the markdown renderer.

### 2. System Integration Security
- **Event Tampering**: All events traversing untrusted boundaries must be digitally signed to guarantee origin and integrity.
- **Dead Letter Security**: Ensure sensitive data (PII/PCI) in failed events is masked or encrypted before being dumped into a Dead Letter Queue (DLQ).

### 3. LLM & Agent Guardrails
- **Ordering Hallucination**: The LLM must not assume guaranteed global ordering of events unless explicitly supported by the selected broker (e.g., Kafka partitions).
- **Consistency Fallacies**: Explicitly warn the user about eventual consistency side-effects; do not falsely claim that distributed EDA systems provide ACID guarantees out-of-the-box.
