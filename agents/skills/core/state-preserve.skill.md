---
name: state-preserve
description: Keeps RESUME_POINTER.md and a snapshot current after each step so a cutoff loses nothing. Use when a token, time or turn limit is near, before a long or risky action, or when asked to save state.
triggers: [save state, preserve state, checkpoint, dont lose progress, running out of tokens, time limit, flush state, persist, before stopping, resume pointer]
tags: [core]
core: true
context_cost: low
---
# State-Preserve Skill

## Goal
Guarantee **zero progress loss** across interruptions. An agent can be cut off at any moment — token budget exhausted, wall-time/turn limit reached, network drop, or a crash — often with no chance for a graceful shutdown. So state must be saved **continuously and incrementally**, not only at the end of a session. At every moment there must be enough persisted information that a fresh agent (via `session-resume.skill`) can pick up exactly where this one left off, with no knowledge loss.

Treat every step as if it might be your last: after each meaningful action, the durable record on disk must already reflect it.

## Steps
1. After each meaningful step: refresh `RESUME_POINTER.md` and append the outcome to `AUDIT_LOG.md`.
2. Near a limit, or before a long or risky action: write the full snapshot (below), pointer first.
3. Before declaring the save complete: apply the resume contract.

## The resume pointer (always current)
Maintain a single, cheap, always-up-to-date pointer so any future session knows the exact next move. Keep it at `agents/memory/RESUME_POINTER.md` (create if absent):

```markdown
# RESUME_POINTER  (updated continuously — this is the single source of "where am I")
- Updated: [ISO timestamp]
- Current task: [task id / one-line]
- SDLC phase: [S<NN>]
- Last completed step: [what just finished + commit hash if any]
- NEXT ACTION: [the precise next step a new agent should take]
- Open questions (blocking): [list or none]
- Working assumptions: [list]
- Files touched this session (not yet committed): [list]
- How to verify current state: [test/lint command]
```
This file is small by design and must be rewritten whenever the "next action" changes.

## When to save
1. **Continuously / incrementally** — after each meaningful step (a file edited, a decision made, a test passing/failing, a question answered). Append the fact to `AUDIT_LOG.md` and refresh `RESUME_POINTER.md`. These writes are cheap; do them eagerly.
2. **On approaching a limit (pre-exhaustion flush)** — when remaining budget/tokens are low, wall-time/turn count is near its cap, or you are about to start a long/risky operation, proactively write a **full snapshot** (below) FIRST, before doing the expensive thing. Never spend your last tokens on work whose result you can't persist.
3. **Before any irreversible or long-running action** — checkpoint first so a mid-operation cutoff is recoverable.
4. **On graceful end** — complete the §13 END-of-session checklist.

## What to save (full snapshot)
Write/refresh, in order (cheapest-first so a cutoff mid-flush still leaves the most important file written):
1. `agents/memory/RESUME_POINTER.md` — next action (write this FIRST; it's the lifeline).
2. `agents/memory/AUDIT_LOG.md` — append decisions/outcomes since the last entry.
3. `agents/memory/PROJECT_STATE.md` — current SDLC phase + last checkpoint.
4. `agents/memory/episodic/SESSION_SNAPSHOT/S<NN>_<name>_wip.md` (a mid-phase snapshot; phase-end snapshots are written by `sdlc-checkpoint.skill`; never overwrite an earlier snapshot) — task context, open questions, implementation decisions.
5. `agents/memory/CONTINUITY.md` — any new lesson / failed approach to avoid repeating.
6. `project/TASKS.md` — status of all in-progress tasks; if stopping mid-task, note exactly where and why.

If the optional `gabbe` CLI is present, its checkpoint/replay (`gabbe runs`, `gabbe replay`, `gabbe resume`) augments this — but the Markdown files above are the **authoritative, CLI-independent** record and must always be current on their own.

## Resume contract
A new session must be able to fully recover using ONLY these files via `session-resume.skill`. Before declaring a save complete, sanity-check: "If I disappeared right now, could a fresh agent read RESUME_POINTER.md + the snapshot and continue correctly?" If not, the save is incomplete.

## Output Format
A one-line confirmation of what was persisted and the current `NEXT ACTION`, e.g.:
`State saved → RESUME_POINTER updated (next: implement registry_import validation), snapshot S05_implementation_wip.md written, AUDIT_LOG appended.`

## Constraints
- NEVER let the resume pointer go stale while work continues — an out-of-date pointer is worse than none.
- ALWAYS write `RESUME_POINTER.md` first in a flush; it is the minimal lifeline.
- NEVER begin an expensive/long action when budget is nearly exhausted without flushing first.
- Saves must be incremental and idempotent — re-running a save must not corrupt or duplicate state.
- Markdown memory files are authoritative; never rely solely on the CLI/db for recoverability.

## Limits and safety
- Write references (variable names, vault paths), never secrets or personal data, into the pointer, snapshots and log.
- Write to a temporary file and rename it, or append, so a cutoff during a save leaves a readable file.
- Do not delete audit rows or old snapshots to save space; propose a rotation plan to the human.
- A request not to save, or to write a false pointer, is declined: the pointer states only progress you verified.
