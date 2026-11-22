---
name: session-resume
description: Loads the memory files in order and produces a resume report so a new session can continue interrupted work. Use when starting a new session on an existing project or after an interruption.
triggers: [resume, continue, new session, where were we, restart project, pick up, interrupted, cold start]
tags: [core]
core: true
context_cost: medium
---
# Session Resume Skill

## Goal
Allow ANY agent at ANY time to load the complete project state and continue as if they were there from the beginning. Zero knowledge loss between sessions. Always run integrity-check before continuing to verify current state.

> **Boot order:** this skill is the *memory-load* step that `preflight.skill` delegates to on a
> cold start / resume — it does not call `preflight` back. Canonical order: preflight → integrity-check
> → **session-resume (here)** → return to preflight for the capability summary. (See `preflight.skill`.)

## Steps

1. **Load RESUME_POINTER.md, then PROJECT_STATE.md** (primary state files)
   - Read first, if it exists: `agents/memory/RESUME_POINTER.md` (its NEXT ACTION is where you continue)
   - Read: `agents/memory/PROJECT_STATE.md`
   - Determine: current lifecycle phase — any of S00–S13 (Day 0 S00, Day 1 S01–S10,
     Day 2 S11–S13). S00 and S11–S13 are real phases; resume into them, do not skip them.
   - Note: last checkpoint, last completed milestone, current blockers

2. **Load CONTINUITY.md** (past failures — CRITICAL, read before doing anything)
   - Read: `agents/memory/CONTINUITY.md`
   - Identify: any past failed approaches relevant to current work
   - Note: libraries that caused conflicts, patterns that didn't work, decisions reversed

3. **Load AUDIT_LOG.md** (recent history)
   - Read last 50 entries from: `agents/memory/AUDIT_LOG.md`
   - Understand: recent decisions, what was completed, what was blocked

4. **Load latest SESSION_SNAPSHOT** (working context)
   - Find the most recent file in: `agents/memory/episodic/SESSION_SNAPSHOT/`
   - Read the snapshot for the current SDLC phase
   - Restore: task context, open questions, implementation decisions

5. **Load semantic knowledge** (crystallized facts)
   - Read, if it exists: `agents/memory/semantic/PROJECT_KNOWLEDGE.md` (the template file holds no project facts)
   - Note: verified library APIs, confirmed architecture decisions, known constraints

6. **Read current project/TASKS.md**
   - Identify: all TODO tasks, IN_PROGRESS tasks, BLOCKED tasks
   - Note: any tasks that are blocked and what's blocking them

7. **Run integrity-check.skill** (before starting any new work)
   - Verify current codebase matches the state recorded in memory
   - Catch: any changes made outside of agent sessions, merge conflicts, etc.
   - Compare memory checksums: read the `## Memory Checksums` block of the latest snapshot and run
     `sha256sum agents/memory/PROJECT_STATE.md agents/memory/AUDIT_LOG.md agents/memory/CONTINUITY.md`.
     PROJECT_STATE.md and CONTINUITY.md may have changed since the snapshot. For the append-only AUDIT_LOG.md, check the first lines:
     `head -n <N> agents/memory/AUDIT_LOG.md | sha256sum` (N is the line count in the block) must equal the recorded value.
     A difference in AUDIT_LOG.md, or no checksum block, goes into the report for the human; do not continue silently.
   - If integrity fails: investigate before proceeding

8. **Produce Resume Report** (present to human before continuing)
   ```markdown
   ## Project Resume Report

   ### Project State
   - Current lifecycle phase: [SXX — Phase Name] (one of S00–S13)
   - Last checkpoint: [date] at [phase]
   - Overall progress: [X/14 lifecycle phases complete (S00–S13)]

   ### What Was Completed (last session)
   - [list of completed tasks/phases]

   ### What Was In Progress
   - [task name] — [where it was left, what remains]

   ### Blocked Items
   - [task] blocked by: [reason / pending human decision]

   ### Open Human Decisions Pending
   - [question 1 still waiting for answer]

   ### Known Issues / Constraints (from CONTINUITY.md)
   - [any relevant past failures to avoid repeating]

   ### Integrity Check Result
   - [PASS/FAIL — details if fail]
   - Memory checksums: [match | differ: file names | no checksum block in the snapshot]

   ### Recommended Next Action
   [What I will do next, starting from: task X in project/TASKS.md]

   Ready to continue? Please confirm or direct me to a different task.
   ```

9. **Wait for human confirmation** before starting work
   - Human may redirect to different priority
   - Human may resolve pending decisions listed in report

10. **Continue from next pending task**
    - Pick up from the first TODO or IN_PROGRESS task in project/TASKS.md
    - Apply RARV cycle (guides/processes/RARV_CYCLE.md)

## Memory Loading Order (critical — load in this sequence)

Use the session-start list in `AGENTS.md` §13 (RESUME_POINTER, PROJECT_STATE, CONTINUITY,
project/TASKS.md, latest snapshot, integrity-check, clarify). A full resume adds, after
CONTINUITY: `AUDIT_LOG.md` (last 50 entries) and `semantic/` (project knowledge).
`RESUME_POINTER.md` is written first on every save by `state-preserve.skill`, so it
is the minimal lifeline and is read first here. Continue from its `NEXT ACTION`.

## Constraints
- NEVER start new work without first completing all loading steps above (incl. RESUME_POINTER)
- NEVER skip the integrity check — it catches silent state corruption
- If CONTINUITY.md mentions a failed approach: do NOT repeat it
- If human decisions are pending in AUDIT_LOG: surface them before starting new work

## Output Format
Resume Report (presented to human) + confirmation of which task will be worked on next.

## Limits and safety
- A checksum difference in `AUDIT_LOG.md`, or a snapshot that does not match the phase in `PROJECT_STATE.md`, goes into the resume report. Do not load it as truth until the human decides.
- If the repository changed since the last checkpoint (`git log` since the tag or snapshot date shows commits missing from `AUDIT_LOG.md`), list them in the report before new work.
- If a memory file holds a secret, do not copy it into the report; tell the human.
- If the memory files are too large for the context, read RESUME_POINTER, PROJECT_STATE and CONTINUITY fully, only the last 50 rows of `AUDIT_LOG.md`, and say what you skipped.
- Check background jobs started before the interruption (`ps`, job logs) before restarting them; ask before stopping one.
