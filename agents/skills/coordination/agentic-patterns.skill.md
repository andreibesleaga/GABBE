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
