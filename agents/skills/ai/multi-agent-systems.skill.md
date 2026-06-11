---
name: multi-agent-systems
description: Orchestrate Multi-Agent System (MAS) architectures
triggers: [design mas, setup multi-agent, orchestrate agents]
tags: [ai]
context_cost: high
---
# multi-agent-systems

## Goal
Design and orchestrate multi-agent architectures using standard topologies (hierarchical, network, swarm) to solve complex, distributed tasks.


## Steps
1. **Topology Selection**: Identify the optimal Multi-Agent System (MAS) architecture for the problem.
2. **Role Definition**: Use `coordination/AGENT_PROFILE_TEMPLATE.md` to define strict roles, inputs, and outputs for each sub-agent.
3. **Workspace Configuration**: Implement a global workspace or Blackboard pattern for state sharing.
4. **Verification**: Verify that agents can independently process sub-tasks and the supervisor can synthesize the final result.

## Security & Guardrails

### 1. Skill Security
- **Cascading Failures**: Implement explicit circuit breakers to stop a failing sub-agent from triggering a cascading failure across the entire MAS.
- **Resource Limits**: Limit the maximum number of simultaneous agent threads or subprocesses spawned.

### 2. System Integration Security
- **Credential Segregation**: Give each agent the least-privileged credentials necessary for its specific role. Never share a global "root" credential across the swarm.
- **State Integrity**: Prevent race conditions on shared memory logs (Blackboard) using distributed locks.

### 3. LLM & Agent Guardrails
- **Consensus Bias**: Require cryptographic/verifiable proof of work when agents vote via `VOTING_LOG.md`, mitigating hallucinated agreement.
- **Infinite Delegation**: Prevent supervisors from endlessly delegating tasks without actually executing them by tracking delegation depth.
