---
name: working-memory
description: Manage Short-Term 'Working Memory' using Cognitive Chunking and Attention.
context_cost: low
tools: [read_file, write_to_file]
---

# Working Memory Skill

Use this skill when handling complex tasks that exceed the "cognitive load" (context window) or require holding multiple variables in mind.

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
*   *Every 5 steps:* Summarize the current state variables.

## 4. Interference Management
If you feel "confused" or hallucinate:
1.  **Flush:** Clear the scratchpad.
2.  **Reload:** Re-read *only* the critical chunk.
3.  **Anchor:** Write down the immediate goal.
