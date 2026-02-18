# Advanced Agentic Systems Guide

Building AI that can act, plan, and self-correct.

## 1. The Core Loop: ReAct
**Reason + Act**. The fundamental pattern for autonomous agents.
1.  **Thought**: The model reasons about the current state.
2.  **Action**: The model decides to call a tool.
3.  **Observation**: The tool output is fed back to the model.
4.  **Repeat**: Until the goal is met.

## 2. Reflection & Self-Correction
Models are prone to hallucination. Reflection mitigates this.
-   **The Pattern**: `Draft` -> `Critique` -> `Refine`.
-   **Implementation**:
    -   Generate a solution.
    -   Prompt the model: "Review the solution above for errors in logic or syntax."
    -   Prompt the model: "Based on the critique, generate a fixed version."

## 3. Memory Architecture
Agents need context beyond the immediate prompt.
-   **Short-Term (Working Memory)**: The current context window. Summary management is key here.
-   **Long-Term (Episodic)**: Vector Database (RAG). Stores past interactions.
-   **Semantic (Knowledge)**: Knowledge Graph. Stores facts and relationships.

## 4. Planning (Chain of Thought)
For complex tasks, "winging it" fails.
-   **Plan-and-Solve**:
    1.  Ask model to generate a step-by-step plan.
    2.  Execute step 1.
    3.  Feed result back.
    4.  Update plan if needed.

## 5. Tools & Function Calling
The agent's hands.
-   **Safety**: Always validate tool inputs with JSON Schema (Zod/Pydantic).
-   **Granularity**: Atomic tools (`readFile`, `writeFile`) are better than god-tools (`doEverything`).
-   **Feedback**: Tool outputs must be descriptive. "Error: File not found" is better than "Error".

## 6. Multi-Agent Orchestration
(See `guides/multi-agent-systems.md` for details)
-   **Orchestrator-Worker**: Delegating sub-tasks.
-   **Consensus**: Multiple agents voting on an answer.
