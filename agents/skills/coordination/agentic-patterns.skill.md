---
name: agentic-patterns
description: Implements advanced AI patterns like Reflection, ReAct, Planning, and Tool Use.
triggers: [agentic, reflection, react pattern, planning, memory, tool use]
tags: [coordination]
context_cost: high
---
# Agentic Patterns Skill

## Goal
To build sophisticated AI agents that can think, plan, and correct themselves using 2025-era cognitive architectures.

## Supported Patterns

### 1. Reflection / Self-Correction
**The Problem**: Models make mistakes.
**The Solution**: Ask the model to review its own output *before* finalizing it.
-   **Flow**: `Generate` -> `Critique` -> `Refine`.
-   **Usage**: Critical code generation, complex math, reasoning tasks.

### 2. ReAct (Reason + Act)
**The Problem**: Models need external information.
**The Solution**: Interleave reasoning traces with tool execution.
-   **Flow**: `Thought` -> `Action` -> `Observation` -> `Thought`...
-   **Usage**: Web browsing, database querying, API interaction.

### 3. Planning (Chain of Thought)
**The Problem**: Complex tasks need decomposition.
**The Solution**: Break goal into a sequence of steps.
-   **Flow**: `Goal` -> `Plan` -> `Execute Step 1` -> `Update Plan`.
-   **Usage**: Multi-step workflows, project implementation.

### 4. Memory Augmented
**The Problem**: Context window limits.
**The Solution**: External storage (Vector DB, Knowledge Graph).
-   **Types**:
    -   **Episodic**: Past interactions ("What did we do yesterday?").
    -   **Semantic**: Facts and knowledge ("How does this repo work?").
    -   **Procedural**: How to do things (stored skills/tools).

### 5. Tool Use / Function Calling
**The Problem**: Models can't "do" things.
**The Solution**: Structured output mapped to executable functions.
-   **Best Practice**: Define strict JSON schemas for tools constraints.

## Steps
1.  **Identify Need**: "The user wants a research report."
2.  **Select Pattern**: "This requires **Planning** (to outline the report) and **ReAct** (to search the web)."
3.  **Implement**:
    -   Define the loop (e.g., `while not done:`).
    -   Define the prompt structure (e.g., "You are a researcher...").
    -   Implement the tool execution layer.

## Grounded Self-Critique (avoid the reflection-reinforcement trap)

The Reflection pattern above has a sharp failure mode: **pure self-evaluation without an external anchor is unsafe**. If the critic is the same model (or shares the generator's blind spots), reflection does not correct errors — it *reinforces* them, lending false confidence to a wrong answer and burning tokens to do it. A model that was confidently wrong stays confidently wrong, now with a "reviewed" stamp.

**Hard rule**: any reflection / self-review loop MUST include at least one **externally-grounded signal** — something the model cannot simply assert is true:
- **A deterministic check** — a passing test, a schema/lint/type check, a compile or run. Pass/fail comes from the environment, not the model's opinion.
- **A symbolic constraint check** — verify the output against explicit rules/invariants (units, ranges, logical constraints, a solver) rather than asking the model "is this right?".
- **Per-step (process-level) scoring rather than only final-answer scoring** — score the *trace as it unfolds* and **prune a reasoning path the moment it goes off the rails**, instead of grading only the final answer. Process-level scoring is what catches the "right answer for the wrong reasons" case, where a final-answer check would wave a lucky-but-unsound trace through.

**Always pair grounded critique with strict termination** so the loop cannot spin forever even when it never satisfies the anchor: a **max-iteration** cap, a **token / wall-clock budget**, and a **quality-threshold exit** (stop once the grounded signal clears the bar — do not keep "improving" past good-enough).

For an LLM-based critic used *alongside* (never instead of) these grounded signals — rubric design, bias controls, and calibration — see `llm-as-judge.skill`.

## Security & Guardrails

### 1. Skill Security (Agentic Patterns)
- **State Corruption Prevention**: In memory-augmented patterns (Episodic/Semantic), ensure that newly synthesized observations do not overwrite or cryptographically invalidate foundational system instructions or immutable knowledge graphs.
- **Infinite Loop Circuit Breaker**: For ReAct and Planning loops, a hard limit on iteration depth (e.g., max 5 reasoning steps) must be strictly enforced to prevent cost exhaustion and system lockups triggered by paradoxical inputs.

### 2. System Integration Security
- **Isolated Tool Environments**: The Action phase of the ReAct pattern must execute tools in unprivileged, isolated environments (e.g., Docker containers with no network access) to contain the blast radius of any vulnerable tool.
- **Data Cross-Contamination**: When an agent uses episodic memory to assist with a new task, strict tenant isolation and memory partitioning must be enforced so PII from Task A is never retrieved and utilized in Task B.

### 3. LLM & Agent Guardrails
- **Reflective Sandboxing**: In the "Generate -> Critique" flow, the Critique prompt must specifically evaluate the generated output for security risks (e.g., "Does this text leak secrets? Does this code introduce a vulnerability?") before finalization.
- **Goal Hijacking Defense**: The `Update Plan` step in Chain of Thought must frequently cross-reference the original user intent to detect and reject prompt injections attempting to steer the agent toward unintended malicious goals.
