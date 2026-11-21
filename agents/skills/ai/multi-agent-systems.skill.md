---
name: multi-agent-systems
description: Design a multi-agent system - topology (hierarchical, network, swarm), role profiles, shared workspace and supervisor. Use when a task needs several agents with defined roles and one result.
triggers: [design mas, setup multi-agent, orchestrate agents, supervisor and sub-agents]
tags: [ai]
context_cost: high
---
# multi-agent-systems

## Goal
Design and orchestrate multi-agent architectures using standard topologies (hierarchical, network, swarm) to solve complex, distributed tasks.

## Steps
1. **Topology Selection**: Identify the optimal Multi-Agent System (MAS) architecture for the problem.
2. **Role Definition**: Use `coordination/AGENT_PROFILE_TEMPLATE.md` to define strict roles, inputs, and outputs for each sub-agent.
3. **Workspace Configuration**: Implement a global workspace or Blackboard pattern for state sharing. For the channels between agents (MCP, A2A, gossip, brokers) see `agent-communication.skill`.
4. **Verification**: Verify that agents can independently process sub-tasks and the supervisor can synthesize the final result.

## Constraints
- Every sub-agent has one role, a defined input and a defined output (see the profile template).
- The supervisor records each delegation; delegation depth is limited.

## Output Format
`docs/MAS_DESIGN.md` (topology, roles, workspace, limits) with one profile per agent from `coordination/AGENT_PROFILE_TEMPLATE.md`.

## Limits and safety
- Set a maximum number of parallel agents and a maximum delegation depth; stop and report when either is reached.
- Give each agent only the credentials and paths its role needs; one shared root credential is a finding.
- Votes in `VOTING_LOG.md` must cite a check an agent can run (a test result, a diff); a vote with no evidence does not count.
- A failing sub-agent is stopped after a set number of retries so its failure does not spread to others.
