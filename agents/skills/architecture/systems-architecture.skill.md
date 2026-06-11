---
name: systems-architecture
description: Generate comprehensive C4 models and System Architecture documents
triggers: [generate c4 model, document system architecture, architect entire system]
tags: [architecture]
context_cost: high
---
# systems-architecture

## Goal
Maintain the holistic, high-level structural map of the software system using the C4 model (Context, Container, Component, Code).


## Steps
1. **Context Mapping**: Define the System Context (users and external systems).
2. **Container Design**: Break the system into deployable containers (Web apps, APIs, Databases).
3. **Component Breakdown**: Detail the macro components within each container.
4. **Output Verification**: Generate proper `C4_ARCHITECTURE_TEMPLATE.md` diagrams and ensure the Mermaid syntax compiles.

## Security & Guardrails

### 1. Skill Security
- **Diagram Bomb**: Prevent the generation of massively interconnected Mermaid diagrams that will crash Markdown renderers. Implement a node/edge limit.
- **Source of Truth Mutation**: The agent must never override existing architecture diagrams without explicitly writing an ADR justifying the change.

### 2. System Integration Security
- **Boundary Identification**: External, untrusted systems must always be explicitly marked with dashed boundaries or designated red-flag colors.
- **Data Flow Security**: Every edge on the diagram connecting an external client to an internal container must specify its encryption protocol (e.g., TLS 1.3).

### 3. LLM & Agent Guardrails
- **Pattern Hallucination**: The LLM must only use project-approved architecture patterns defined in `AGENTS.md` (e.g., sticking to Hexagonal Architecture if mandated).
- **Silent Dropping**: Ensure the LLM does not silently drop unglamorous but critical system components (like logging clusters, DLQs, or internal admin panels) from the diagrams.
