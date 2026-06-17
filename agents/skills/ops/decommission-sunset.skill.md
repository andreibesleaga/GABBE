---
name: decommission-sunset
description: Plan the safe sunset of a service or product — deprecation policy and timeline, data retention/migration/export, user comms, contract wind-down, traffic drain, teardown, and post-sunset verification.
triggers:
  - plan to decommission the legacy billing service
  - sunset and deprecate the old api
  - draft a shutdown timeline for the product
  - export and migrate data before teardown
  - drain traffic and tear down the system
  - wind down the vendor contract and licenses
  - verify nothing depends on the retired service
tags: [ops, decommission, sunset, lifecycle]
core: false
context_cost: medium
---
# Decommission & Sunset Skill

## Goal
Produce a decommission plan that retires a service, product, or system safely and reversibly-until-the-last-step — protecting users and their data, honoring contractual and legal obligations, and avoiding the two failure modes of a careless shutdown: stranding data/users, and tearing down something still in use. The output ties to `DECOMMISSION_PLAN_TEMPLATE.md`.

## Steps
1. **Confirm the decision and scope.** State what is being sunset, why, and the boundary (one endpoint, one service, a whole product). Identify all consumers — internal services, external integrators, and end users — and any contractual/SLA commitments still in force.
2. **Set the deprecation policy and timeline.** Define dated phases: announce → deprecate (no new adopters, warnings emitted) → read-only/grace → shutdown → teardown → post-verification. Honor any contractual notice periods. Each phase has a date and an exit criterion.
3. **Plan data retention, migration, and export.** For every dataset, decide: retain (and where, under what retention/legal-hold policy), migrate (to which successor system), or delete (and when). Provide an end-user **export** path so customers can retrieve their own data before shutdown. Map source→target fields for migrations and define a reconciliation check.
4. **Plan archival.** Specify what is archived for compliance/audit (configs, final data snapshots, audit logs) and the archive location, retention duration, and restore procedure.
5. **Define the user-comms cadence.** Schedule notifications at announce, at each milestone, and at final cutoff (e.g., T-90/T-30/T-7/T-1 days plus shutdown day), through the right channels (email, in-app banner, API deprecation headers, status page, docs). State who sends each and what it says.
6. **Wind down licenses and contracts.** List vendor contracts, licenses, certificates, domains, and recurring costs tied to the system; schedule cancellation/non-renewal aligned to the shutdown date so you neither pay for dead infrastructure nor cut a dependency early.
7. **Drain traffic.** Progressively reduce and redirect traffic (return deprecation responses, then 410/redirect, then hard-off) before teardown, watching telemetry to confirm consumers have actually moved. Keep a documented rollback until the point of no return (data deletion).
8. **Final teardown.** After the drain confirms zero meaningful traffic and data is migrated/exported/archived, decommission infrastructure: remove compute, revoke credentials and access, delete or quarantine data per the retention plan, and remove DNS/load-balancer entries.
9. **Post-sunset verification.** Confirm nothing still depends on the retired system: no lingering callers, no broken downstream services, no orphaned cloud resources or costs, credentials revoked, and the archive is restorable. Record completion in the audit trail.

## Constraints
- Honor all contractual notice periods and legal/data-retention obligations; the timeline bends to them, not the reverse.
- Provide a user-facing data export path before any data deletion.
- Data deletion is the point of no return — keep rollback available through every prior phase and gate deletion behind explicit human approval.
- Traffic must be drained and confirmed near-zero via telemetry before teardown; do not tear down on assumption.
- Credentials and access are revoked and orphaned resources removed as part of teardown — a half-decommission is a security and cost liability.
- This skill plans the sunset; it does not delete data or tear down infrastructure without explicit human authorization.

## Output Format
A decommission plan in Markdown following `DECOMMISSION_PLAN_TEMPLATE.md`:
- **Scope & rationale** — what is sunset, why, consumers, contractual commitments.
- **Timeline** — dated phases (announce → deprecate → grace → shutdown → teardown → verify) with exit criteria.
- **Data plan** — per-dataset retain/migrate/delete decision, user export path, migration field map, reconciliation check.
- **Archival** — what is archived, where, retention, restore procedure.
- **Comms cadence** — schedule, channels, owner, message per milestone.
- **Contract/license wind-down** — items, cancellation dates, owners.
- **Traffic drain** — drain stages, telemetry checks, rollback boundary.
- **Teardown** — infra removal, credential revocation, data disposition.
- **Post-sunset verification** — dependency checks, orphaned-resource check, audit-trail record.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Premature or unrecoverable data deletion. Mitigation: deletion is gated behind explicit human approval, occurs only after export + migration + archive are verified, and uses soft-delete/quarantine with a hold period before hard deletion where feasible.
- **Risk**: Exposing data during export/migration. Mitigation: encrypt exports in transit and at rest, scope access to the data owner, and expire export links; never export PII to an unsecured location.

### 2. System Integration Security
- **Risk**: Leaving orphaned credentials, keys, or cloud resources after teardown (security and cost exposure). Mitigation: the verification phase explicitly revokes all credentials, removes IAM grants, and reconciles the cloud account for orphaned resources and lingering spend.
- **Risk**: Tearing down a system still in active use, causing an outage. Mitigation: require telemetry-confirmed near-zero traffic and a dependency scan before teardown; keep deprecation responses live through a grace period.

### 3. LLM & Agent Guardrails
- **Risk**: The agent executing teardown or deletion autonomously. Mitigation: destructive teardown and any data deletion require explicit human authorization with an audit-trail entry; the agent only produces and sequences the plan.
- **Risk**: The agent shortcutting notice periods or comms to "finish faster." Mitigation: contractual notice periods and the full comms cadence are hard requirements the agent may not compress; skipping a notification is flagged, not silently dropped.
