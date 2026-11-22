---
name: enterprise-migration-scenario
description: "Phased plan for moving a large legacy system to a modern platform with strangler fig, anti-corruption layer or change data capture, parallel runs and rollback. Use when a mainframe or on-premises system must migrate without dropping traffic or data."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/enterprise-migration-scenario.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "high"
---
# enterprise-migration-scenario

## Goal
Design and execute large-scale migrations from legacy systems (mainframe/on-prem) to modern, cloud-native architectures without dropping traffic or data.

## Steps
1. **Audit Legacy**: Parse existing legacy docs using `architecture/LEGACY_AUDIT_TEMPLATE.md`.
2. **Select Pattern**: Choose migration strategies like Strangler Fig, Anti-Corruption Layer (ACL), or CDC (Change Data Capture).
3. **Execution Plan**: Output a phased `core/PLAN.md` with incremental rollout checkpoints.
4. **Verification**: Verify backward-compatibility testing (parallel runs) and automated rollback plans are explicitly documented.

## Constraints
- No big-bang cutover; phases with checkpoints and a rollback each.
- Legacy data is only added to or shadowed until cutover is approved.

## Output Format
`LEGACY_AUDIT_TEMPLATE.md` (`templates/architecture/`) filled in, and a phased plan with rollout checkpoints.

## Limits and safety
- Output no command that drops, truncates or overwrites legacy data; the migration stays additive (shadow writes, parallel runs) until the human approves cutover.
- Run generated migration SQL or scripts first on a copy and review them.
- Do not assume how an undocumented legacy system behaves; put it in an open-questions list for the human.
- Sync between old and new systems is encrypted, and the anti-corruption layer checks types and rejects malformed input.
- Reject a one-weekend big-bang plan; plan phases with a rollback for each.
