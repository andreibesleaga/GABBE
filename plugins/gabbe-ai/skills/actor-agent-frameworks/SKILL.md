---
name: actor-agent-frameworks
description: "Set up an agent or actor graph (LangGraph, Akka or custom) with state schema, checkpoints and failure recovery. Use when you build or change a multi-step agent graph or actor system that must survive restarts."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ai/actor-agent-frameworks.skill.md"
  tags: "ai"
  core: "false"
  context_cost: "high"
---
# actor-agent-frameworks

## Goal
Implement, configure, and maintain robust Agent and Actor-based frameworks (such as LangGraph, Akka, or custom implementations).

## Steps
1. **Topology Definition**: Define the nodes, edges, and state schema for the agent graph.
2. **Actor Implementation**: Define the explicit behaviors, inbox/message queues, and lifecycle of individual actors.
3. **Integration**: Connect the framework to persistent memory stores (e.g., SQLite, PostgreSQL) for state checkpoints.
4. **Verification**: Simulate actor failures and verify that the graph/supervisor recovers state correctly.

## Constraints
- Every message between actors has a schema; a message that does not validate goes to the dead-letter queue.
- Every graph has a maximum step count and a defined end state.

## Output Format
A short topology note `docs/AGENT_GRAPH.md` (nodes, edges, state schema, checkpoint store, failure handling) and the framework code with its failure-recovery test.

## Limits and safety
- Actors that run model output execute in a sandbox without access to the host or project secrets.
- Checkpoints must not contain API keys or tokens; grep a saved checkpoint for them before relying on the store.
- Set a maximum number of steps per run and a size limit on the dead-letter queue.
- After repeated failure of one actor, stop and report to the human with the saved state; do not drop the context.
