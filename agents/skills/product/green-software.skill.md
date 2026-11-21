---
name: green-software
description: "Review a system for carbon and energy efficiency: architecture, region, scheduling, data retention. Use when asked to reduce the carbon footprint or to choose greener options for a design."
triggers: [green software, reduce carbon footprint, energy efficient design, carbon aware scheduling, low carbon region, eco mode]
tags: [product]
role: prod-ethicist
context_cost: low
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
- **Joy of Delete**: Find unused data and propose deleting it (don't pay storage energy cost forever). List it first; delete only after the human confirms the exact command.

## 4. Carbon Aware Computing
- Utilize APIs like `ElectricityMaps` or `WattTime`.
- **Batch Jobs**: Schedule heavy cron jobs for 2 AM (or whenever local grid is greenest).
- **"Eco-Mode"**: UI toggle that reduces animations and video quality to save battery/energy.

## Constraints
- Every claim of energy or carbon saved names its measured input and the calculation.
- Security work and audit logs are never traded for energy savings.

## Output Format
A short review: findings by area (architecture, region, scheduling, data retention), the estimated saving for each with its inputs, and the actions proposed.

## Limits and safety
- Before deleting data to save storage, list the candidates, check them against `AUDIT_LOG.md` and retention rules, and run the deletion only after the human confirms. Never delete audit or compliance logs.
- Carbon-aware scheduling never delays security work (key rotation, scans, incident response).
- Do not state carbon savings without measured inputs (energy, CPU time, bytes) and the calculation.
- Do not remove TLS, encryption or bounds checks to save energy.
- Treat carbon-intensity data from ElectricityMaps or WattTime as an input that can be wrong or unreachable; fall back to the normal schedule.
