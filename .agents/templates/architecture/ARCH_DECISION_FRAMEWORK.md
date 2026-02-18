# Architecture Decision Framework

**Decision Title**: [e.g., Monolith vs Microservices for Order Service]
**Date**: [YYYY-MM-DD]
**Status**: [Proposed / Accepted / Rejected]

## 1. Context & Problem Statement
[What are we trying to solve? e.g., "The Order service needs independent scaling for Black Friday."]

## 2. Options Considered

| Option | Description | Pros | Cons |
|---|---|---|---|
| **Option A** | [e.g., Modular Monolith] | - Simple deployment<br>- Zero network latency | - Harder to scale writes independently |
| **Option B** | [e.g., Microservices] | - Independent scaling<br>- Tech stack freedom | - High operational complexity<br>- Network latency |
| **Option C** | [e.g., Serverless] | - Pay-per-use<br>- Infinite scaling | - Cold starts<br>- Vendor lock-in |

## 3. Decision Drivers (NFRs)
- **Scalability**: [High/Med/Low importance]
- **Cost**: [Budget constraints]
- **Time to Market**: [Urgency]
- **Maintainability**: [Team skill level]

## 4. Final Recommendation
**Selected Option**: [Option B]

**Justification**:
[Why this option won. e.g., "Scalability is the #1 driver. We accept the operational complexity cost."]

## 5. Consequences
- **Positive**: [e.g., Can scale to 10k TPS]
- **Negative**: [e.g., Need to implement distributed tracing]
