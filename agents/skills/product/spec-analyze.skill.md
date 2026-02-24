---
name: spec-analyze
description: Check consistency and alignment between spec.md, plan.md, and project/TASKS.md — detect drift and mismatches
triggers: [analyze spec, consistency check, alignment, drift, spec vs plan, are specs aligned, spec mismatch]
tags: [product]
context_cost: low
---
# Spec Analyze Skill

## Goal
Verify that the three core planning artifacts — PRD.md/spec.md, plan.md, and project/TASKS.md — are fully aligned. Detect any requirements that have no implementation plan, any plan items with no tasks, and any tasks with no requirement.

## Steps

1. **Load all three artifacts**
   - Read PRD.md (or spec.md) — get all EARS requirements
   - Read plan.md (or PLAN.md) — get all implementation phases and decisions
   - Read project/TASKS.md — get all atomic tasks with their status

2. **Check Requirement → Plan coverage**
   For each EARS requirement in PRD.md:
   - Does plan.md have at least one item addressing this requirement?
   - Are there requirements with no corresponding plan entry?
   - Flag: `[UNCOVERED] Requirement: "WHEN user resets password THE SYSTEM SHALL..." — no plan entry`

3. **Check Plan → Task coverage**
   For each implementation phase/item in plan.md:
   - Does project/TASKS.md have at least one task for this plan item?
   - Are there plan items with no corresponding tasks?
   - Flag: `[NO_TASKS] Plan item: "Implement email verification" — 0 tasks in project/TASKS.md`

4. **Check Task → Requirement traceability**
   For each task in project/TASKS.md:
   - Can this task be traced back to a requirement in PRD.md?
   - Are there tasks that don't correspond to any stated requirement (scope creep)?
   - Flag: `[ORPHAN_TASK] Task: "Add admin dashboard" — no corresponding requirement`

5. **Check status consistency**
   - Are there tasks marked DONE for requirements that haven't been approved yet?
   - Are there tasks IN_PROGRESS while a dependency task is still TODO?
   - Are there DONE tasks that don't have corresponding test coverage?

6. **Check EARS syntax compliance**
   - Scan all requirements for vague language: "should", "might", "user-friendly", "fast"
   - Flag: `[VAGUE] "The API should be fast" — not a testable requirement. Rewrite with measurable criterion.`

7. **Generate alignment report**
   ```markdown
   ## Spec Alignment Report

   ### Coverage: Requirements → Plan
   - COVERED: [N] requirements
   - UNCOVERED: [N] requirements (listed below)

   ### Coverage: Plan → Tasks
   - COVERED: [N] plan items
   - NO_TASKS: [N] plan items (listed below)

   ### Orphan Tasks (no requirement)
   - [list any tasks with no corresponding requirement]

   ### EARS Compliance Issues
   - [list vague requirements]

   ### Status Inconsistencies
   - [list any status conflicts]

   ### Verdict
   ALIGNED: [YES/NO]
   Blocking issues: [count]
   Recommended actions: [list]
   ```

8. **If mismatches found**: present to human and ask which artifact should be updated
   - If requirement missing from plan: "Should I add this to plan.md?"
   - If task has no requirement: "Should I add a requirement to PRD.md or remove this task?"

## Constraints
- This skill reads artifacts only — it does NOT modify them without explicit instruction
- After human decision, re-run the analysis to confirm alignment
- Run this skill whenever any of the three artifacts changes

## Output Format
Alignment report in markdown with categorized findings and clear ALIGNED: YES/NO verdict.

## Security & Guardrails

### 1. Skill Security (Spec Analyze)
- **Security Scope Creep Detection**: When analyzing "Orphan Tasks" (Step 4), the agent must apply extra scrutiny to tasks modifying authentication, cryptography, logging, or authorization logic that lack a traced requirement. Undocumented security changes are a primary vector for backdoors.
- **Silent Security Drops**: If a security requirement in `PRD.md` (e.g., "Data at rest must be encrypted") is flagged as `[UNCOVERED]` in `plan.md`, the agent must escalate this not just as an alignment issue, but as a critical compliance breach preventing system deployment.

### 2. System Integration Security
- **Test Coverage vs. Security Specs**: In Step 5, when checking status consistency, the agent must verify that any task traced to a Security requirement (e.g., Rate Limiting) is not marked `DONE` unless the corresponding integration test file explicitly asserts the security failure modes (e.g., HTTP 429 generation).
- **Dependency Drift Alerts**: If `plan.md` assumes the use of a specific security library, but `project/TASKS.md` implements a different tool (a mismatch), the agent must halt the SDLC phase until an ADR writer justifies the library swap.

### 3. LLM & Agent Guardrails
- **Automated Deletion Veto**: The agent is strictly a read-only analyst. If it finds "Orphan Tasks" with no requirement, it MUST NOT autonomously delete the task from the repository. It must only report the anomaly, as the task might be a legitimate hotfix that simply hasn't been documented yet.
- **Hallucinated Alignment**: The LLM must not synthesize "implied" traceability to make the report look clean. If Task X is "Setup HTTPS loop" and Requirement Y is "System must be fast", the agent must not invent a link between them. Traceability must be explicit and deterministic.
