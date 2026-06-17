---
name: feature-flag-management
description: Manage the full feature-flag lifecycle — create, roll out, measure, and clean up — across release, ops/kill-switch, experiment, and permission flag types with progressive delivery.
triggers:
  - add a feature flag for the checkout rollout
  - plan a canary release with flags
  - set up a kill switch for the search feature
  - clean up stale feature flags
  - do a percentage rollout
  - track flag debt and ownership
  - ring deployment plan for the new feature
tags: [ops, feature-flags, progressive-delivery, release]
core: false
context_cost: medium
---
# Feature Flag Management Skill

## Goal
Produce a flag plan that takes a feature from dark-launch to full rollout and then to clean removal, choosing the right flag type, the right progressive-delivery strategy, and naming the owner and cleanup date so flags do not rot into permanent, untested branching. Every flag created is a liability with a planned end-of-life; this skill makes that lifecycle explicit.

## Steps
1. **Classify the flag type.** Pick exactly one primary purpose: **release** (temporary, gates an in-progress feature, deleted after launch); **ops/kill-switch** (operational toggle to disable a subsystem under load or incident, may be long-lived); **experiment** (A/B variant assignment, removed when the experiment concludes); **permission/entitlement** (per-user or per-tenant gating, long-lived by design). The type sets the expected lifespan and the cleanup rule.
2. **Define the flag contract.** Specify the key (namespaced, e.g. `release.checkout-v2`), default value (safe/off), the evaluation context (user, tenant, region), and the fallback behavior when the flag service is unreachable — code must fail safe to the default.
3. **Plan progressive delivery.** Choose a rollout strategy: **canary** (small fixed cohort first), **percentage rollout** (ramp 1% → 5% → 25% → 50% → 100% with hold points), or **ring deployment** (internal → beta → broad). Define the guardrail metric and the abort condition at each step (e.g., error rate or p99 latency exceeding the SLO triggers automatic hold).
4. **Wire the kill switch.** For any flag guarding risky behavior, ensure flipping it off is instant, requires no deploy, and is rehearsed. Document who can flip it and how it is verified (tie the abort path to a runbook via `runbook-authoring.skill`).
5. **Measure.** State the success criteria and the metrics that confirm the rollout is healthy before each ramp step. Connect rollout-stage and flag-key to telemetry (see `observability-stack-setup.skill`) so dashboards show behavior per flag state.
6. **Schedule cleanup.** Assign a named **cleanup owner** and a target removal date at creation time. Release and experiment flags must be deleted once fully rolled out or concluded; record the follow-up task so the flag and its dead code path are removed.
7. **Track flag debt.** Inventory existing flags, flag any that are stale (fully rolled out but not removed, or untouched past their target date), and recommend removals. Stale flags are tech debt and a correctness risk because the off-path is rarely tested.

## Constraints
- One primary purpose per flag; do not overload a single flag to gate unrelated features.
- Defaults are safe/off; code must fail to the default if the flag service is unavailable.
- Every release and experiment flag carries a cleanup owner and target removal date from creation — no orphans.
- Kill switches must work without a deploy and be rehearsed, not theoretical.
- Progressive rollout ramps have explicit hold points and automatic abort conditions tied to SLO guardrails.
- This skill plans flag lifecycle; it does not flip production flags or change live targeting without human approval.

## Output Format
A flag plan in Markdown:
- **Flag** — key, type (release/ops/experiment/permission), default, evaluation context, fail-safe behavior.
- **Rollout strategy** — canary / percentage / ring, ramp steps with hold points, guardrail metric, abort condition.
- **Kill switch** — toggle path, who can flip, verification, linked runbook.
- **Measurement** — success criteria and per-stage health metrics.
- **Lifecycle & cleanup** — cleanup owner, target removal date, follow-up task reference.
- **Flag debt** — table of existing flags with status (active / stale / remove) and recommended action.

## Security & Guardrails

### 1. Skill Security
- **Risk**: A permission/entitlement flag misconfigured to grant broader access than intended. Mitigation: permission flags default to deny, require review of the targeting rule, and are tested for the deny path before rollout.
- **Risk**: Flag evaluation context carrying PII (raw email, IDs) to a third-party flag service. Mitigation: pass hashed/opaque identifiers in evaluation context; do not send raw PII to external flag providers.

### 2. System Integration Security
- **Risk**: Unauthorized or untracked changes to flag targeting flipping a feature on for everyone. Mitigation: flag changes go through audited, access-controlled tooling with change records; production targeting changes are logged to the audit trail.
- **Risk**: Flag-service outage silently changing behavior. Mitigation: clients cache last-known values and fail to the documented safe default; alert on flag-service unavailability rather than failing open.

### 3. LLM & Agent Guardrails
- **Risk**: The agent flipping a production kill switch or ramping a rollout autonomously. Mitigation: live flag state changes require explicit human approval; the agent only proposes the plan and the ramp steps.
- **Risk**: The agent recommending deletion of an ops/kill-switch flag because it "looks unused," removing an incident control. Mitigation: ops/kill-switch flags are exempt from automatic stale-cleanup; their removal requires deliberate human sign-off.
