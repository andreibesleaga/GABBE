---
name: capacity-planning
description: Forecasting resource usage, load testing interpretation, and scaling limits.
triggers: [capacity planning]
tags: [ops]
role: ops-sre
---
# capacity-planning Skill

## Goal
This skill guides the estimation of infrastructure needs based on usage patterns.

## Steps
## 1. The Universal Formula
`Required Replicas = (Target RPS * Avg Request Latency) / Max Thread Utilization`

*Example*:
- Target: 1000 RPS
- Latency: 0.2s (200ms)
- 1 Core handles: 1 / 0.2 = 5 req/s (Sync) OR much higher if Async.
- **Rule of Thumb**: Run load tests to find "Breaking Point" RPS per instance.

## 2. Resource Dimensions

| Resource | Bottleneck Symptom | Mitigation |
|---|---|---|
| **CPU** | High latency, timeouts. | Horizontal Scale (add replicas). |
| **Memory** | OOM Kills, Crash loops. | Vertical Scale (larger pods), fix leaks. |
| **Disk IO** | High IOWAIT, slow DB. | Provision IOPS (GP3/IO1), cache reads. |
| **Network** | Bandwidth limits, packet loss. | Compress data, reduce payload size. |
| **DB Connect** | "Too many connections". | Connection Pooling (PgBouncer). |

## 3. Creating a Capacity Plan (Template)
Use `templates/ops/CAPACITY_PLAN_TEMPLATE.md`.

1.  **Baseline**: Current usage (Peak CPU %, Avg RAM).
2.  **Growth Factor**: "Marketing launching new campaign, expect 3x traffic".
3.  **Headroom**: Always provision +30% buffer for spikes.
4.  **Limits**: What hits the ceiling first? (Usually the DB).

## 4. Load Testing
- **Tools**: k6, Artillery, Locust.
- **Pattern**:
  1.  **Smoke**: 1 VUser (Verify logic).
  2.  **Load**: Target RPS (Verify stability).
  3.  **Stress**: Ramp until crash (Find the limit).
  4.  **Soak**: Run 99% load for 4 hours (Find memory leaks).

## 5. Auto-Scaling Rules (HPA)
- **Don't scale on CPU alone**. If app is IO bound, CPU might be low while app is dead.
- **Scale Up Fast**: Reaction time < 1 min.
- **Scale Down Slow**: Stabilization window > 5 mins (prevent flapping).

## Security & Guardrails

### 1. Skill Security (Capacity Planning)
- **Denial of Wallet (DoW) Protection**: Auto-scaling rules proposed by the capacity planner MUST include hard upper boundaries (e.g., `maxReplicas: 20`) to prevent an application layer DDoS attack from spinning up infinite instances and bankrupting the organization.
- **Forecast Formula Integrity**: The scaling multiplier algorithms used by the agent must be protected from external manipulation. An attacker should not be able to poison telemetry logs to trick the planner into prematurely scaling up or down.

### 2. System Integration Security
- **Secure Load Testing**: Load tests and stress tests must *never* be executed against Production environments without an explicit, multi-factor authorized maintenance window, preventing accidental self-inflicted Denial of Service (DoS) attacks.
- **Load Test Data Sanitization**: Virtual Users (VUsers) in test scripts must utilize securely generated synthetic data. Copying real user PII from Production to Staging for capacity planning is a critical data breach risk and is strictly forbidden.

### 3. LLM & Agent Guardrails
- **Resource Exhaustion Awareness**: The LLM must be explicitly prompted to prioritize security over absolute availability when resources run out. For example, if a DB connection pool is exhausted, it must advocate for graceful degradation (HTTP 503) rather than advising disabling connection timeouts.
- **Adversarial Input Recognition**: Provide guardrails against user prompts that request the generation of "stress testing" scripts aimed at external third-party URLs. The agent must verify ownership of the target domain before outputting load-generation code.
