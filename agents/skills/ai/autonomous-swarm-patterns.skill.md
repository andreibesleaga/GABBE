---
name: autonomous-swarm-patterns
description: Implement self-organizing autonomous swarm architectures
triggers: [implement swarm, deploy autonomous agents, setup swarm consensus]
tags: [ai]
context_cost: high
---
# autonomous-swarm-patterns

## Goal
Implement advanced autonomous swarm patterns (e.g., ant-colony optimization, particle swarm, or self-organizing agent clusters) for decentralized problem-solving.


## Steps
1. **Pheromone/Marker Design**: Define how agents leave structural markers (like `CONTINUITY.md` or git commits) to influence other agents asynchronously.
2. **Behavioral Rules**: Give each agent simple, localized rules rather than complex global knowledge.
3. **Consensus Protocols**: Implement decentralized consensus (e.g., voting, threshold signatures) for collective decisions.
4. **Verification**: Run a simulation to verify the swarm stabilizes and converges on a solution without diverging into chaos.

## Security & Guardrails

### 1. Skill Security
- **Swarm Containment**: Explicitly bound the swarm's domain. They must not crawl or interact with external systems outside the predefined whitelist.
- **Cost Runaway Mitigation**: Hard-cap API token usage and agent iterations. A swarm can bankrupt a project in minutes if unconstrained.

### 2. System Integration Security
- **Emergent Malice Detection**: Monitor the aggregate behavior of the swarm. Even if individual rules are safe, the swarm could collectively launch a Denial of Service attack against internal systems.
- **Rate Limiting**: Enforce strict rate limits on the shared context/database layer to prevent the swarm from crashing infrastructure.

### 3. LLM & Agent Guardrails
- **Echo Chamber Hallucinations**: Prevent agents from recursively training on or validating each other’s hallucinated markers.
- **Kill Switch Mandate**: The developer must be able to issue a single `KILL` command that immediately halts all swarm activity universally.
