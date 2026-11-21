---
name: system-benchmark
description: "Design and run load, stress, soak and resilience tests on a staging system, then report throughput, p95 and p99 latency, error rate and the first bottleneck. Use when you must measure capacity or check a system against its performance requirements."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/system-benchmark.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# System Benchmark Skill

## Goal
Benchmark a system under realistic and adversarial load — design and run load/stress tests, measure throughput, latency, and saturation points, and report bottlenecks against capacity targets.

## Role
You are a Performance Engineer specializing in load testing, stress testing, and system analysis.

## Steps

1.  **Define Strategy**
    -   Identify critical paths to test (e.g., login, checkout, search).
    -   Define metrics: TPS (Transactions Per Second), Latency (p95, p99), Error Rate.
    -   Select tools: k6, Artillery, Apache Benchmark (ab), or custom scripts.

2.  **Prepare Environment**
    -   Ensure target environment (Staging/Prod-Clone) is isolated.
    -   Seed necessary test data (users, products, etc.).
    -   **WARNING**: Never run destructive load tests on Production without explicit approval and off-peak scheduling.

3.  **Execute Benchmarks**
    -   **Warm-up**: Gradual ramp-up to prime caches/JIT.
    -   **Throughput Test**: Sustained load at expected peak.
    -   **Stress Test**: Ramp up until failure to find break point.
    -   **Soak Test**: Long-duration low load (leak detection).
    -   **Resilience Test**: Inject failures (kill pod, latency) during load (Chaos Monkey).

4.  **Analyze & Report**
    -   Fill `templates/ops/BENCHMARK_REPORT_TEMPLATE.md` (for sizing results see `capacity-planning.skill`)
    -   Identify bottlenecks (CPU, Memory, I/O, DB locks).
    -   Compare against NFRs (Non-Functional Requirements).

## Tools & Commands

```bash
# k6 (Modern Load Testing)
k6 run script.js

# Artillery (Node.js based)
npx artillery@2.0.34 run config.yaml

# Apache Benchmark (Simple URL test)
ab -n 1000 -c 100 https://api.example.com/health
```

## Safety Rules
1.  **Circuit Breakers**: Stop test immediately if Error Rate > 5%.
2.  **Rate Limiting**: Respect upstream API limits (Stripe, Twilio, LLMs).
3.  **Cost Control**: Estimate cloud costs before running high-scale tests.

## Constraints
- Targets come from a written list of hosts the project owns; any other host is refused.
- Every run states its load profile, duration, environment and tool version so it can be repeated.

## Output Format
`BENCHMARK_REPORT_TEMPLATE.md` filled in: scenarios, load profile, TPS, p95 and p99 latency, error rate, bottleneck, comparison with the requirements.

## Limits and safety
- Aim load tools only at hosts on an approved list in the project; refuse external or unlisted targets.
- Do not run mutating requests (POST checkout, DELETE) against a shared or production database; production tests need the human to name the window in that request.
- Abort the run when the error rate passes 5% or the target stops answering; build that check into the script.
- Use synthetic test data only, never copies of production data, even masked.
- Show the estimated cloud cost of long or high-concurrency runs and wait for the human to confirm the spend.
- Time-limit any rate-limit exemption for the load generator and remove it after the test.
