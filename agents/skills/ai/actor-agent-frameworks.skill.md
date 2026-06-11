---
name: actor-agent-frameworks
description: Implement and manage Actor and Agent Frameworks (e.g. LangGraph)
triggers: [setup langgraph, implement actor framework, configure agent framework]
tags: [ai]
context_cost: high
---
# actor-agent-frameworks

## Goal
Implement, configure, and maintain robust Agent and Actor-based frameworks (such as LangGraph, Akka, or custom implementations).


## Steps
1. **Topology Definition**: Define the nodes, edges, and state schema for the agent graph.
2. **Actor Implementation**: Define the explicit behaviors, inbox/message queues, and lifecycle of individual actors.
3. **Integration**: Connect the framework to persistent memory stores (e.g., SQLite, PostgreSQL) for state checkpoints.
4. **Verification**: Simulate actor failures and verify that the graph/supervisor recovers state correctly.

## Security & Guardrails

### 1. Skill Security
- **Sandbox Isolation**: Ensure actors executing untrusted LLM output run in a sandboxed environment without implicit system access.
- **State Poisoning Prevention**: Validate all messages passed between actors against a strict schema (e.g., Pydantic).

### 2. System Integration Security
- **Secure Persistence**: Checkpoints written to the database must not serialize and log plaintext sensitive secrets (API keys).
- **Dead-Letter Handling**: Implement secure dead-letter queues for unhandled messages to prevent memory exhaustion.

### 3. LLM & Agent Guardrails
- **Routing Loop Prevention**: Impose a maximum step/recursion limit on graph traversals to prevent infinite loops.
- **Fail-Safe Constraints**: When an actor fails repeatedly, gracefully escalate to a human operator instead of dropping the context.
