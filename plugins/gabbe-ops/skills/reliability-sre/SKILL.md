---
name: reliability-sre
description: "Apply SRE practice - SLIs and SLOs, error budgets and freeze policy, golden signals, symptom alerts, blameless post-mortems and chaos tests. Use when you set reliability targets, an error budget runs out, or on-call needs a recovery guide."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/reliability-sre.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "medium"
---
# Reliability & SRE Skill

## Goal
To treat operations as a software problem and balance improved reliability with feature velocity.

## Capabilities

### 1. Service Level Objectives (SLO)
-   **SLI**: What you measure (e.g., Latency < 100ms).
-   **SLO**: The target (e.g., 99.9% of requests meet SLI).
-   **Structure**: 28-day rolling window. 99.9% allows about 40 minutes of downtime in 28 days.

### 2. Error Budgets
-   **Definition**: `1 - SLO`. The allowed unreliability.
-   **Policy**: If budget is exhausted -> Freeze feature launches -> Focus on stability.

### 3. Incident Management
-   **Postmortems**: Blameless analysis of *process* failure, not *human* error.
-   **Severity Levels**: SEV1 (Critical/Down) to SEV4 (Minor bug).
-   **MTTR**: Mean Time To Recovery (Focus on fixing fast, not just preventing failure).

## Steps
1.  **Define Golden Signals**: Latency, Traffic, Errors, Saturation.
2.  **Chaos Engineering**: Test failure modes *before* they happen in production.
3.  **Alerting**: Alert on *symptoms* (User Pain), not *causes* (CPU High). Each alert gets a runbook: see `runbook-authoring.skill`. For capacity and scaling limits see `capacity-planning.skill`.

## Deliverables
-   `slo-definition.md`: Document metrics and targets.
-   `runbook.md`: Step-by-step recovery guide for on-call.
-   `postmortem.md`: Incident analysis.

## Constraints
- Every SLO names its SLI, target and window.
- A post-mortem describes process and system causes, not one person's fault.

## Output Format
The files named under Deliverables: `slo-definition.md`, `runbook.md`, `postmortem.md`.

## Limits and safety
- Run chaos experiments only in a window the human has approved, with a stop command that is tested first; never against production on your own.
- Give runbook scripts only the permissions their action needs; a restart script must not be able to change IAM roles or drop tables.
- Keep SLO and alert definitions in version control; if your platform provides branch protection, use it so thresholds cannot be quietly relaxed.
- If your platform can enforce the error-budget freeze (protected branches, deploy checks), use it; otherwise report the freeze to the human.
- Write post-mortems without blame; do not lower alert severity to meet an SLO.
