---
name: green-software
description: Carbon efficiency, sustainable architecture choices, and GreenTech goals.
triggers: [green software]
tags: [product]
role: prod-ethicist
---
# green-software Skill

## Goal
This skill guides the reduction of the system's environmental impact.

## Steps
## 1. Principles (Green Software Foundation)
1.  **Carbon Efficiency**: Emit the least amount of carbon per unit of work.
2.  **Energy Efficiency**: Consume the least amount of electricity.
3.  **Carbon Awareness**: Do more work when the electricity is clean (low carbon intensity) and less when it's dirty.

## 2. Architectural Choices
- **Serverless vs Always-On**: Serverless scales to zero (0 energy) when idle.
- **Compiled vs Interpreted**: Rust/Go consume ~50% less energy than Python/Node for compute-heavy tasks.
- **Data Minimization**: Sending less data = less network energy.

## 3. Operations
- **Region Selection**: Host in regions with low carbon intensity (e.g., AWS Sweden/Canada > Virginia).
- **Joy of Delete**: Aggressively delete unused data (don't pay storage energy cost forever).

## 4. Carbon Aware Computing
- Utilize APIs like `ElectricityMaps` or `WattTime`.
- **Batch Jobs**: Schedule heavy cron jobs for 2 AM (or whenever local grid is greenest).
- **"Eco-Mode"**: UI toggle that reduces animations and video quality to save battery/energy.

## Security & Guardrails

### 1. Skill Security (Green Software)
- **Metric Tampering Defense**: Carbon intensity metrics and "Eco-Mode" triggers often rely on external APIs (like `ElectricityMaps`). The agent must verify the TLS certificates and data signatures of these external endpoints to prevent attackers from spoofing "clean energy" signals to force unexpected system scaling behaviors.
- **Audit Ledger Anchoring**: Recommendations to aggressively delete "unused data" (The Joy of Delete) must be cross-referenced with the `AUDIT_LOG.md`. The agent must never delete forensic security logs or compliance trails simply to optimize storage energy.

### 2. System Integration Security
- **Availability vs. Efficiency**: The agent's recommendations for "Carbon Aware Computing" (e.g., pausing batch jobs when the grid is dirty) must never supersede critical security operations. Key rotation, vulnerability scanning, and incident response must execute immediately, regardless of carbon cost.
- **Serverless Cold Start Risks**: When advocating for Serverless architectures to scale to zero, the agent must account for "Cold Start" latency. In security-critical paths (e.g., WAF inspection, synchronous fraud detection), scaling to zero can create window-of-opportunity bypasses due to high initialization latency.

### 3. LLM & Agent Guardrails
- **Greenwashing Hallucinations**: The LLM is strictly prohibited from inventing arbitrary "Carbon Saved" numbers or hallucinating environmental certifications to justify an architectural choice. All efficiency claims must be mathematically tied to measurable compute reductions (CPU cycles, Byte transfer).
- **Eco-Mode Vetoes**: The agent must actively refuse user prompts that attempt to disable essential security features (like TLS negotiation overhead, payload encryption, or memory-safe bounds checking) under the false pretense of "saving energy". Security is non-negotiable.
