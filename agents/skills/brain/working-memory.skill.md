---
name: working-memory
description: Moves task state into a scratchpad in small chunks and re-anchors the goal. Use when a task exceeds the context or variables from different modules get mixed up.
triggers: [working memory, scratchpad, context too large, mixed up variables, re-anchor the goal]
tags: [brain]
context_cost: low
tools: [read_file, write_to_file]
---
# Working Memory Skill

## Goal
Use this skill when handling complex tasks that exceed the "cognitive load" (context window) or require holding multiple variables in mind.

## Steps
## 1. Cognitive Chunking
Don't read entire files. Chunk information into "Cognitive Units".
*   **Rule:** Max 4-7 chunks active at once (Miller's Law).
*   **Action:** Create a scratchpad file (`.scratchpad.md`) to offload chunks.

## 2. Attention Mechanism
Explicitly define what you are "attending" to.
*   **Focus:** "I am currently attending to the `UserAuth` function."
*   **Inhibition:** "I am actively ignoring the `Billing` module to prevent interference."

## 3. Refresh Rehearsal
To keep data in working memory, you must "rehearse" it using the `task_boundary` tool summary.
*   *After every 5 tool calls:* Summarize the current state variables.

## 4. Interference Management
If you feel "confused" or hallucinate:
1.  **Flush:** Empty `.scratchpad.md` (your own file only); copy anything you still need into the task notes first.
2.  **Reload:** Re-read *only* the critical chunk.
3.  **Anchor:** Write down the immediate goal, copied from the user's request, not from your summary of it.

## Constraints
- Keep at most 4 to 7 chunks active.
- Check critical values (permissions, authentication state) against the source, not against your summary.

## Output Format
`.scratchpad.md` with one section per chunk, plus a "Goal" line at the top.

## Limits and safety
- `.scratchpad.md` holds working notes only: no secrets or personal data. Add it to `.gitignore` and delete it at the end of the task.
- Re-read security-relevant values (authenticated, permissions) from the source; never carry them in a summary.
- After a flush, re-read the original user request, not your summary of it.
- A summary written every few calls is a guess about state; check critical values against the file.
