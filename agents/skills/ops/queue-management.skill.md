---
name: queue-management
description: Standards for DLQs (Dead Letter Queues), Idempotency, and Retry policies.
triggers: [queue management]
tags: [ops]
role: eng-backend, ops-sre
---
# queue-management Skill

## Goal
Async messaging is powerful but dangerous. Messages must never be lost.

## Steps
## 1. Dead Letter Queues (DLQ)
- **Rule**: Every consumer MUST have a configured DLQ.
- **Behavior**: If a message fails processing N times (Poison Pill), move it to DLQ. Alert `ops-sre`.
- **Replay**: Must have a mechanism to replay messages from DLQ after bug fix.

## 2. Idempotency
- **Rule**: All consumers `handle(msg)` must be idempotent.
- **Pattern**:
  1. Check `processed_messages` table for `msg.id`.
  2. If found, ack and ignore.
  3. If not, process transactionally.
  4. Save `msg.id` to `processed_messages`.

## 3. At-Least-Once Delivery
- Assume you will receive duplicates. Network acks fail. Design for it.

## 4. Ordering
- **Kafka**: Ordering is only guaranteed *within a partition*.
- **SQS FIFO**: Guaranteed but lower throughput.
- **Best Practice**: Don't rely on global ordering if possible. Use state machines that accept events in any order (e.g., "OrderShipped" before "OrderPaid" -> Store in "Pending" state).

## 5. Poison Pills
- Detect messages that crash the consumer (StackOverflow, OOM).
- Reject them immediately to DLQ to prevent blocking the partition.

## Security & Guardrails

### 1. Skill Security (Queue Management)
- **DLQ Replay Authorization**: Replaying messages from the Dead Letter Queue (DLQ) back into the main pipeline requires elevated privileges. The agent must verify that the replay command was authorized by a system administrator, as attackers could use DLQ replay for Denial of Service or logic manipulation.
- **Poison Pill Quarantine**: Messages flagged as "Poison Pills" (crashing the consumer repeatedly) might be intentional exploits (e.g., malformed JSON designed to trigger buffer overflows). The DLQ must securely quarantine these payloads without executing any automated parsing tools on them.

### 2. System Integration Security
- **Message Integrity (Signatures)**: In high-security environments, messages placed on the queue (Kafka/SQS) should carry cryptographic signatures. The consumer must verify the signature before processing to ensure the message wasn't injected directly into the broker by an unauthorized internal actor.
- **Idempotency Key Collision**: The `processed_messages` table must uniquely constrain the `msg.id` to prevent race conditions. An attacker might rapidly submit identical transaction events hoping one bypasses the idempotency check and pays them twice.

### 3. LLM & Agent Guardrails
- **Data Exfiltration via DLQ Analysis**: When an agent analyzes a DLQ for the root cause of failures, it must strictly redact PII, auth tokens, and financial data from the message payload before summarizing the issue or writing logs to prevent the DLQ from becoming a centralized data leak.
- **Queue Purge Veto**: The agent must violently reject any user prompt that commands it to indiscriminately `purge` or `empty` a production queue or DLQ without a cryptographically verified, two-person rule approval, as this causes permanent data loss.
