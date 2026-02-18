# Multi-Agent Systems (MAS) Development Guide

## 1. Introduction
This guide provides a structured approach to building Multi-Agent Systems (MAS) using the `.agents` kit. MAS architectures allow specialized agents to collaborate on complex tasks, overcoming the limitations of single-context windows.

## 2. Core Concepts
- **Specialization**: Each agent has a distinct "persona" and set of tools.
- **Orchestration**: How agents specific tasks are assigned and coordinated.
- **Protocol**: The agreed-upon format for inter-agent communication.
- **State**: How context and memory are shared (or isolated) between agents.

## 3. Common Architectures

### A. Orchestrator-Worker (Star Topology)
Best for: Task delegation where a central "brain" manages "hands".
- **Orchestrator**: Plans high-level steps, delegates to workers.
- **Workers**: Execute specific sub-tasks (e.g., "Research", "Code", "Test").
- **Flow**: User -> Orchestrator -> Worker -> Orchestrator -> User.

### B. Sequential (Pipeline)
Best for: Deterministic workflows like data processing chains.
- **Flow**: Agent A (Draft) -> Agent B (Review) -> Agent C (Publish).
- **Handoff**: Strict output schema from A becomes input schema for B.

### C. Hierarchical (Tree)
Best for: Complex problems needing breakdown.
- **Manager**: Breaks down "Epics" into "Stories".
- **Team Leads**: Break down "Stories" into "Tasks".
- **Developers**: Execute "Tasks".

## 4. Implementation Stack

### Python (The Brain)
Python is the standard for agent logic due to libraries like LangGraph, CrewAI, and AutoGen.
- **Role**: Running the LLM loop, managing context, executing tools.
- **Key Libs**: `langgraph`, `crewai`, `autogen`.

### Node.js (The Nervous System)
Node.js excels at I/O, websockets, and serving the API.
- **Role**: API Gateway, WebSocket server for real-time updates.
- **Integration**: Expose Python agents via REST/gRPC to Node.js.

### React (The Face)
- **Role**: User Interface for chatting with agents and visualizing swarm state.
- **Pattern**: Use WebSockets to stream partial updates from the swarm.

## 5. Development Workflow

1.  **Define Roles**: Use `coordination/AGENT_PROFILE_TEMPLATE.md` to define each agent.
2.  **Design Topology**: Use `coordination/SWARM_ARCHITECTURE_TEMPLATE.md` to map interactions.
3.  **Establish Protocol**: Use `coordination/agent-protocol.skill.md` to define JSON schemas.
4.  **Implement**:
    -   Start with the Orchestrator.
    -   Mock the Workers.
    -   Implement connectivity (A2A).
5.  **Test**: Verified with `coordination/multi-agent-orch.skill.md`.

## 6. Testing Strategies
-   **Mocking**: specific agents to isolate behavior.
-   **Simulation**: Run the swarm against a set of predefined scenarios.
-   **Evals**: Use an "Evaluator Agent" to grade the output of the swarm.

## 7. Advanced Loki Patterns (Optimization)

### A. RAG-Augmented Swarms
Loki Mode now integrates with `knowledge-connect.skill` to give agents "Long-Term Semantic Memory".
1.  **Configure**: Fill `core/MCP_CONFIG_TEMPLATE.json`.
2.  **Indexing**: Run `knowledge-connect` to ingest docs/codebase into Vector DB.
3.  **Retrieval**: During Phase S05, Loki automatically queries the DB for implementation guides relevant to the current task.

### B. Parallel Execution (Batching)
Standard sequential chains are slow. Loki optimizes S05 via "Task Batching":
1.  **Decomposition**: `orch-planner` tags tasks as `[PARALLEL]` if they have no dependencies.
2.  **Execution**: Agents pick up a *batch* of tasks (e.g., T-101, T-102, T-103) and execute them concurrently.
3.  **Merge**: Results are merged, and the dependency graph is updated.

### C. Hybrid Swarms (A2A)
Loki allows delegation to external specialized swarms:
-   **Internal**: "Build the API" (Loki Persona `backend-coder`)
-   **External**: "Audit for vulnerabilities" -> Delegates to `Sec-Swarm-1` via `agent-interop.skill`.

### D. Cognitive Architectures (Global Workspace)
For highly dynamic environments, use the **Global Workspace** pattern ([`brain/global-workspace.skill.md`](../skills/brain/global-workspace.skill.md)).
-   **Concept**: Agents "compete" for attention rather than following a rigid pipeline.
-   **Use Case**: When the next step is ambiguous and requires the "most confident" agent to take over.

