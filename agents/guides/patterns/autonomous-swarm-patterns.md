# Autonomous Swarm Patterns

This guide defines advanced patterns for multi-agent collaboration, self-correction, and tool building.

## 1. The Consensus Pattern (Voting)
When agents disagree, use `coordination/swarm-consensus.skill.md`.

### Protocol
1.  **Coordinator** detects conflict (e.g., `prod-architect` wants Microservices, `ops-cost` wants Monolith).
2.  **Coordinator** calls for a vote using `weighted` protocol.
3.  **Agents** cast votes based on their persona constraints.
4.  **Coordinator** logs result to `core/AUDIT_LOG_TEMPLATE.md` and enforces the decision.

## 2. The Toolsmith Pattern (Self-Expansion)
When the swarm lacks a capability, it builds it.

### Workflow
1.  **Detection**: Agent fails to perform task due to missing tool.
2.  **Request**: Agent invokes `eng-tooling`. "Build a script to parse this binary format."
3.  **Build**: `eng-tooling` writes `tools/parser.py` and validates it.
4.  **Usage**: The original agent uses the new tool to complete the task.

## 3. The Meta-Cognition Loop (Reflection)
Agents should think before acting, and reflect after acting.

### Pre-Action (Planning)
- "I am about to edit 5 files. Is this the safest way? Let me simulate the outcome."

### Post-Action (Reflection)
- "I edited the file. Did I break the tests? Let me run `integrity-check`."

## 4. Memory Optimization
- Context windows are finite.
- Use `ops/memory-optimization.skill.md` to:
  - Summarize completed tasks into `core/AUDIT_LOG_TEMPLATE.md`.
  - "Forget" detailed code snippets once the file is saved.
  - Keep only the "High-Level Plan" in active memory.

## 5. Swarm Topology
- **Hierarchical**: `orch-coordinator` commands `eng-*` agents. (Standard).
- **Parliamentary**: All agents vote on decisions. (Use for Architecture/Strategy).
- **Relay**: Agent A passes output to Agent B (e.g., `spec-writer` -> `eng-backend` -> `eng-qa`).
