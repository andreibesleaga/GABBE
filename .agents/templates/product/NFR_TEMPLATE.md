# Non-Functional Requirements (NFRs) Definition

**System**: [System Name]
**Date**: [YYYY-MM-DD]

## 1. Reliability & Availability
-   **Availability Target**: [99.9% / 99.99%]
-   **Max Downtime**: [43 min/month / 4 min/month]
-   **RTO (Recovery Time Objective)**: [Time to restore service after disaster]
-   **RPO (Recovery Point Objective)**: [Max acceptable data loss interval]

## 2. Performance & Scalability
-   **Latency (p95)**: [< 100ms / < 500ms]
-   **Throughput (Peak)**: [Req/sec expected]
-   **Throughput (Sustained)**: [Req/sec average]
-   **Concurrent Users**: [Number of active users]

## 3. Security & Compliance
-   **Data Class**: [Public / Internal / PII / PCI]
-   **Encryption**: [At Rest / In Transit / Client-Side]
-   **Audit Logging**: [Retention period]

## 4. Compatibility & Evolution
-   **Backwards Compatibility**: [Must support Clients vX.Y]
-   **Browser Support**: [Chrome/Firefox/Safari last 2 versions]
-   **Device Support**: [iOS 16+, Android 12+]

## 5. Observability
-   **Metrics**: [Golden Signals required?]
-   **Tracing**: [Distributed tracing ID propagation?]
-   **Logs**: [Structured JSON logs required?]
