---
name: systems-architecture
description: "C4 model (context, container, component) as Mermaid diagrams with an architecture document. Use when a system's structure must be documented or its diagrams are missing or stale."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/systems-architecture.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "high"
---
# systems-architecture

## Goal
Maintain the holistic, high-level structural map of the software system using the C4 model (Context, Container, Component, Code).

## Steps
1. **Context Mapping**: Define the System Context (users and external systems).
2. **Container Design**: Break the system into deployable containers (Web apps, APIs, Databases).
3. **Component Breakdown**: Detail the macro components within each container.
4. **Output Verification**: Generate proper `C4_ARCHITECTURE_TEMPLATE.md` diagrams and ensure the Mermaid syntax compiles.

## Constraints
- One C4 level per diagram.
- The Mermaid syntax compiles.

## Output Format
`C4_ARCHITECTURE_TEMPLATE.md` (`templates/architecture/`) filled in with the diagrams.

## Limits and safety
- Never replace an existing architecture diagram without an ADR giving the reason.
- Mark external and untrusted systems; each edge from outside states its protocol, or `[UNKNOWN]`.
- Use only patterns approved in `AGENTS.md`, and do not drop logging, dead letter queues or admin panels from the diagrams.
- Keep each diagram small enough to render; split by level.
