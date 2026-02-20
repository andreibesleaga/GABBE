# System Benchmark Report

**Date:** [YYYY-MM-DD]
**Environment:** [Staging / Production Clone]
**Tools Used:** [k6 / Artillery / Jmeter]
**Tester:** [Agent Name / Human]

## 1. Executive Summary
> One-line verdict: [PASS / FAIL / WARN]
> Summary of key findings...

## 2. Test Configuration
*   **Target URL/Service:** `[URL]`
*   **Duration:** `[Time]`
*   **Virtual Users (VUs):** `[Count]`
*   **Ramp-up Pattern:** `[Description]`

## 3. Results Summary

| Metric | Target (NFR) | Measured | Status |
|---|---|---|---|
| **Avg Throughput** | 1000 RPS | [Value] | ✅/❌ |
| **Peak Throughput** | 1500 RPS | [Value] | ✅/❌ |
| **Latency p95** | < 200ms | [Value] | ✅/❌ |
| **Latency p99** | < 500ms | [Value] | ✅/❌ |
| **Error Rate** | < 0.1% | [Value] | ✅/❌ |
| **CPU Usage (Peak)** | < 80% | [Value] | ✅/❌ |
| **Memory Leak?** | No | [Yes/No] | ✅/❌ |

## 4. Bottleneck Analysis
*   **Database:** [Locks, Slow Queries, Connection Pool...]
*   **Application:** [GC pauses, Event Loop lag, Thread exhaustion...]
*   **Network:** [Bandwidth, Latency, Timeout...]
*   **Dependencies:** [3rd party API limits...]

## 5. Resilience Observations
*(If Chaos testing was performed)*
*   **Scenario:** [e.g., Kill DB Master]
*   **Recovery Time (RTO):** [Seconds]
*   **Data Loss (RPO):** [Records]

## 6. Recommendations
1.  [Action Item 1]
2.  [Action Item 2]
3.  [Action Item 3]

## 7. Evidence
> [Attach Screenshots / Log Snippets / Grafana Links]
