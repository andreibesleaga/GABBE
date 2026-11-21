---
name: episodic-consolidation
description: "Turns a finished task's audit log into reusable rules and prunes scratch files. Use at the end of a long task to record lessons and to detect drift in the project's world model. Use when: episodic consolidation, consolidate lessons, end of long task, prune scratch files, world model drift."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/episodic-consolidation.skill.md"
  tags: "brain"
  core: "false"
  context_cost: "high"
---
# Episodic Consolidation Skill

## Goal
This skill mimics the brain's "Sleep" process (Hippocampus to Neocortex transfer). Use it at the end of a long task (Task Boundary).

## Steps
## 1. The Consolidation Process
1.  **Replay:** Review the `AUDIT_LOG.md` or Session History.
2.  **Extract:** Identify "Generalized Rules" from specific events.
    *   *Event:* "I fixed a bug in `auth.go` caused by nil pointer."
    *   *Rule:* "Always check for nil in `auth.go` User structs."
3.  **Store:** Write this Rule to `agents/memory/semantic/rules.md` (create the file if it does not exist).

## 2. Identifying Episodic Drifts
Check if the "Story" of the project has changed.
*   **Drift:** "We used to use SQL, now we use NoSQL."
*   **Action:** Update `PROJECT_CONTEXT.md` (the world model; create it from `templates/brain/PROJECT_CONTEXT_TEMPLATE.md` if missing) to reflect this new reality.

## 3. Pruning (Forgetting)
Active forgetting is crucial.
*   **Action:** List temporary scratchpads and `tmp/` files that are no longer needed, then delete them only after the human confirms the list. Never list audit logs, snapshots or deployment records.

## Constraints
- A rule needs at least 3 observations and a source (log row, test or file).
- Rules are additive; a rule must not contradict the Constitution or an architecture rule.

## Output Format
The new or changed rules (with their sources), any change to `PROJECT_CONTEXT.md`, and the list of scratch files proposed for deletion.

## Limits and safety
- Write a rule only after the pattern appeared at least 3 times and a source backs it; check it against `architecture-governance.skill` and the Constitution.
- Strip names, credentials and personal data from every rule; keep the rule general.
- Never prune `AUDIT_LOG.md`, snapshots or deployment records. Delete scratch files only after the human confirms your list.
- A temporary waiver or hack is an incident, not a change to the world model; do not record it as drift.
- Ask the human to review `rules.md` at the next checkpoint.
