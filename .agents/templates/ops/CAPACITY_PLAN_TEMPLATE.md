# Capacity & Scaling Plan

**Service**: [Name]
**Date**: [YYYY-MM-DD]
**Author**: [Name]

## 1. Current Baseline
| Metric | Peak Value | Average | Notes |
|---|---|---|---|
| RPM | 5,000 | 1,200 | Peak at 9am EST |
| Latency p95 | 350ms | 150ms | |
| CPU Usage | 65% | 20% | |
| RAM Usage | 2GB | 1.8GB | High constant memory |
| DB Connections | 85 | 40 | Limit is 100 |

## 2. Growth Forecast
**Scenario**: [e.g., Black Friday, New Feature Launch]
**Expected Multiplier**: [e.g., 3x Traffic]

| Metric | Projected Peak | Capacity Limit | Status |
|---|---|---|---|
| RPM | 15,000 | 20,000 (Load Tested) | ✅ Safe |
| DB Connections | 255 | 100 | ❌ **CRITICAL** |

## 3. Bottleneck Analysis
- **Primary Bottleneck**: Database Connection Limit.
- **Secondary Bottleneck**: Memory (JVM Heap is tight).

## 4. Mitigation Plan
1.  **Immediate**: Implement PgBouncer/RDS Prxoy to pool connections. Target: Support 1000 client conns multiplexed to 100 DB conns.
2.  **Scale Up**: Increase App Server memory to 4GB to prevent OOM.
3.  **Scale out**: Increase Read Replicas from 1 to 2.

## 5. Cost Impact
- Previous Monthly: $500
- New Monthly: $850 (+70%)
- Justification: Loss of service during lunch would cost ~$5k/min.

## 6. Sign-off
- [ ] Engineering Lead
- [ ] SRE Lead
