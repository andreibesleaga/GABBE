---
name: runbook-authoring
description: Author operational runbooks so every alert maps to a tested, copy-pasteable, idempotent recovery procedure with diagnosis, remediation, escalation, rollback, and verification.
triggers:
  - write a runbook for the high-latency alert
  - create an on-call recovery procedure
  - the disk-full alert has no runbook
  - document remediation steps for the outage
  - turn the postmortem into a runbook
  - make these recovery commands idempotent
  - add escalation and rollback steps to the runbook
tags: [ops, runbook, on-call, incident]
core: false
context_cost: medium
---
# Runbook Authoring Skill

## Goal
Produce an operational runbook that a tired on-call engineer can follow at 3am without prior context. The governing rule: **every alert maps to exactly one runbook**, and the runbook walks from symptom to verified recovery with steps that are copy-pasteable and idempotent (safe to re-run). The output ties to `RUNBOOK_TEMPLATE.md` and should be linked from the alert that triggers it.

## Steps
1. **Anchor to the alert.** Start from the firing alert and its SLI. State the exact alert name/condition so the runbook is discoverable from the alert payload. If the alert has no runbook, this is the gap being closed.
2. **Symptom.** Describe what the operator observes — the alert text, the dashboard panel, the user-visible behavior. This confirms they are in the right runbook.
3. **Impact.** State who/what is affected and how badly (user-facing? data at risk? degraded vs. down?). This sets urgency and whether to escalate immediately.
4. **Diagnosis steps.** List ordered, read-only checks to confirm the cause and rule out look-alikes. Each step is a copy-pasteable command or query plus the expected/healthy output and the branch to take on each result. Diagnosis must not mutate state.
5. **Remediation.** Give the ordered fix actions. Each command must be **idempotent** — re-running it converges to the same healthy state and does not compound damage (prefer `apply`/declarative over imperative one-shots; guard destructive actions with explicit confirmation). Note the blast radius of each action.
6. **Verification.** Define how the operator confirms recovery: the metric/SLI returning to normal, the alert clearing, and a synthetic or smoke check. The runbook is not "done" until verification passes.
7. **Rollback.** Provide the exact steps to undo the remediation if it makes things worse, including how to revert a deploy or flip the relevant kill-switch (see `feature-flag-management.skill`).
8. **Escalation.** Name the next contact/team, the trigger to escalate (e.g., not recovered in N minutes, or impact crosses a severity threshold), and the on-call channel. Reference `incident-response.skill` for severity handling.
9. **Test it.** Validate the runbook against a real or game-day scenario; commands that have never been run are not a runbook. Record the last-tested date.

## Constraints
- One runbook per alert; the alert must link to it and the runbook must name its alert.
- Diagnosis steps are read-only; only the Remediation section mutates state.
- Every command is copy-pasteable (no "adjust as needed" placeholders inside the command itself) and remediation commands are idempotent.
- Destructive or wide-blast-radius actions carry an explicit warning and a confirmation gate.
- Every runbook includes verification AND rollback; neither is optional.
- The agent authors and proposes runbook content; it does not execute remediation commands against production without human approval.

## Output Format
A runbook in Markdown following `RUNBOOK_TEMPLATE.md`:
- **Alert** — name, condition, SLI defended, severity.
- **Symptom** — what the operator sees.
- **Impact** — who/what is affected, degraded vs. down.
- **Diagnosis** — ordered read-only checks with expected output and branches.
- **Remediation** — ordered idempotent commands with blast-radius notes.
- **Verification** — recovery checks and the alert-clear condition.
- **Rollback** — exact undo steps.
- **Escalation** — contact, trigger, channel.
- **Metadata** — owner, last-tested date.

## Security & Guardrails

### 1. Skill Security
- **Risk**: A runbook command leaking or hardcoding secrets/credentials in copy-pasteable text. Mitigation: reference secrets by named env var or vault path, never inline values; review runbooks for embedded credentials before publishing.
- **Risk**: A non-idempotent remediation command compounding damage when re-run (e.g., scaling up repeatedly, double-applying a migration). Mitigation: prefer declarative/converging commands, add guards, and explicitly mark any step that is not safe to re-run.

### 2. System Integration Security
- **Risk**: Runbook automation running with excessive privilege (a "restart" script that can drop tables or edit IAM). Mitigation: scope runbook tooling to least privilege per the action it performs; destructive scopes require separate authorization.
- **Risk**: A tampered or out-of-date runbook directing an operator to a harmful action. Mitigation: store runbooks as version-controlled, reviewed artifacts linked from alerts; stale runbooks past their test date are flagged for re-validation.

### 3. LLM & Agent Guardrails
- **Risk**: The agent executing remediation autonomously during an incident. Mitigation: the agent proposes and explains steps; running destructive remediation against production requires explicit human approval and an audit-trail entry.
- **Risk**: The agent fabricating commands that look plausible but were never tested. Mitigation: mark any unverified step clearly, prefer commands grounded in the actual system's tooling, and require a game-day or real test before a runbook is considered authoritative.
