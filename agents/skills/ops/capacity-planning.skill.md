---
name: capacity-planning
description: Estimate how many instances, how much memory, IO and connections a service needs, from a baseline, a growth factor, a load test and headroom. Use when you plan for a traffic increase, size a cluster or set autoscaling limits.
triggers: [capacity planning, how many replicas, size the cluster, forecast traffic, autoscaling limits, load test plan]
tags: [ops]
role: ops-sre
context_cost: low
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

## Constraints
- Every estimate states its inputs (target RPS, latency, headroom) so another person can redo it.
- Autoscaling rules always have a maximum.

## Output Format
`project/CAPACITY_PLAN.md` from `templates/ops/CAPACITY_PLAN_TEMPLATE.md`: baseline, growth factor, headroom, first limit reached, scaling rules, load-test results.

## Limits and safety
- Every autoscaling rule you propose has a maximum replica count and a cost ceiling the human has seen.
- Run load and stress tests against production only when the human names the window in that request; otherwise use staging.
- Load-test data is synthetic; do not copy real user data into a test environment.
- Generate load scripts only for systems the project owns; ask the human to confirm the target before the first run.
