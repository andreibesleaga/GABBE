# Incident Postmortem: [Incident Title]

**Date**: [YYYY-MM-DD]
**Authors**: [Names]
**Status**: [Draft / Review / Completed]
**Severity**: [SEV1 / SEV2 / SEV3]

## Executive Summary
*Briefly describe what happened, the impact (users affected), and the root cause.*

## Impact
-   **Downtime Duration**: [HH:MM]
-   **User Impact**: [X% of users experienced errors]
-   **Data Impact**: [Data loss / Corruption / Latency]

## Timeline
| Time (UTC) | Description |
|---|---|
| 10:00 | Alert fired: High Error Rate > 5% |
| 10:05 | On-call Engineer acknowledged |
| 10:15 | Rollback initiated |
| 10:20 | Service recovered |

## Root Cause Analysis (5 Whys)
1.  **Why did the system fail?** (e.g., DB CPU spiked to 100%)
2.  **Why did the DB CPU spike?** (e.g., New deployment added a query)
3.  **Why was the query slow?** (e.g., Missing index on `user_id`)
4.  **Why was the index missing?** (e.g., Migration script failed but didn't error out)
5.  **Why did the deployment proceed?** (e.g., Pipeline ignores migration warnings)

## Lessons Learned
-   **What went well?** (e.g., Alerting was fast)
-   **What went wrong?** (e.g., Rollback took too long)
-   **Where did we get lucky?**

## Action Items
-   [ ] [Fix] Add missing index to DB.
-   [ ] [Prevent] Fail pipeline on migration warnings.
-   [ ] [Detect] Add alert for high DB CPU.
