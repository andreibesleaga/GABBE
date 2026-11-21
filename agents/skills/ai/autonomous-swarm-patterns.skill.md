---
name: autonomous-swarm-patterns
description: Build a self-organising swarm of agents that coordinate through shared markers and simple local rules. Use when one agent cannot cover a decentralised problem and you want many agents with no central planner.
triggers: [implement swarm, deploy autonomous agents, setup swarm consensus, ant colony pattern]
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

## Constraints
- Ask the human before starting more than one agent; state the agent count, token cap and run time first.
- Each agent has local rules only; the whole-swarm behaviour is checked by a simulation, not assumed.

## Output Format
`docs/SWARM_DESIGN.md` (marker design, agent rules, consensus rule, caps, stop command) and the simulation result showing the swarm converges.

## Limits and safety
- Set a hard cap on agents, iterations and tokens before the first run, and confirm it with the human.
- Bound the swarm to a written list of paths and services; any other target is out of scope.
- Provide one stop command or stop file that halts every agent; test it before a long run.
- Rate-limit the shared context store or database the swarm writes to.
- Agents must not validate each other's markers without a check a command can run.
