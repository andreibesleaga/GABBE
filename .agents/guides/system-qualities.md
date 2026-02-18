# System Qualities: The "Ilities" Guide

Building software is easy. Building software that *lasts*, *scales*, and *adapts* is hard.

## 1. Reliability & SRE
*Reliability is the most important feature. If it's down, it doesn't matter how fast it is.*

-   **SLOs (Service Level Objectives)**: Set a target (e.g., 99.9%). Don't aim for 100%.
-   **Error Budgets**: Use the remaining 0.1% to take risks. If you burn the budget, stop shipping features.
-   **Chaos Engineering**: Break things on purpose. If you don't test failover, it won't work when you need it.

## 2. Scalability & Performance
*Performance is not about being "fast". It's about being "consistent" under load.*

-   **Caching**: The fastest query is the one you don't make. Use **Cache-Aside** for most cases.
-   **Async Processing**: Don't make the user wait for email sending. Use a Queue (RabbitMQ / SQS).
-   **Database First**: Optimize your SQL queries and Indices before rewriting the app in Rust.

## 3. Compatibility & Evolution
*Change is constant. Breaking things is optional.*

-   **Expand & Contract**: The Golden Rule of Zero Downtime Migrations.
    1.  **Add** the new thing.
    2.  **Support** both old and new.
    3.  **Delete** the old thing.
-   **Tolerant Readers**: Follow Postel's Law. Be strict in what you send, but liberal in what you accept.
-   **Forward Compatibility**: Design today's system to ignore tomorrow's unknown fields.

## 4. Observability
*You can't fix what you can't see.*

-   **Logs**: "What happened?" (Events)
-   **Metrics**: "Is it healthy?" (Aggregates)
-   **Traces**: "Where did it happen?" (Context)
