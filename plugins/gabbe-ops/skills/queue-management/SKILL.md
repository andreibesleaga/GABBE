---
name: queue-management
description: "Set rules for message queues - dead-letter queues, idempotent consumers, retries, at-least-once delivery, ordering and poison pills. Use when you add a consumer, messages are lost or processed twice, or a DLQ fills up."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/queue-management.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "low"
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

For integration with ERP, CRM or legacy systems through queues see `enterprise-integration.skill`.

## Constraints
- Every consumer has a DLQ and an idempotency check.
- No consumer relies on global message order.

## Output Format
The consumer code and configuration, the DLQ and replay procedure in the runbook, and a test with a duplicate message and a poison message.

## Limits and safety
- Replaying or purging a DLQ or production queue is proposed with the exact command and queue name and run only after the human confirms.
- Do not run parsers or tools on quarantined poison messages; inspect them as plain text.
- Put a unique constraint on the message id in the processed-messages table; test two simultaneous deliveries.
- Redact personal data, tokens and financial values from DLQ payloads before quoting or logging them.
- If your broker supports message authentication, use it where untrusted producers can write to the queue.
