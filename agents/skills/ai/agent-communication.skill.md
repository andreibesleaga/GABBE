---
name: agent-communication
description: Choose and wire the channel between agents - MCP, A2A, ACP, gossip or a broker (Kafka, RabbitMQ, MQTT), with a capability handshake. Use when two or more agents must exchange messages or delegate work across processes or vendors.
triggers: [setup swarm communication, implement a2a protocol, connect agents using mcp, design gossip protocol, agent handshake]
tags: [ai]
context_cost: medium
---
# agent-communication

## Goal
Establish, negotiate, and enforce structured Agent-to-Agent communication channels using emerging standards (MCP, A2A, ACP) alongside enterprise protocols (Kafka, Gossip) to ensure interoperability and secure data exchange.

## Steps
1. **Protocol Analysis & Selection**: Select the appropriate protocol tier based on the architectural need:
   - **MCP (Model Context Protocol)**: Use Anthropic's universal standard for agents to access external data, context, and tools (Client-Server model).
   - **A2A (Agent-to-Agent Protocol)**: Implement the Linux Foundation's standard for horizontal interoperability, allowing vendor-agnostic agents to communicate, delegate workflows, and exchange "Agent Cards" capabilities.
   - **ACP (Agent Communication Protocol)**: Use for real-time, local-first collaboration (e.g., edge or IoT), ensuring minimal latency over HTTP.
   - **Distributed Gossip / Epidemic Protocols**: Implement decentralized peer-to-peer state sharing for autonomous swarms needing high fault tolerance and no central broker.
   - **Enterprise Brokers**: Connect agents via Kafka, RabbitMQ, or MQTT for high-throughput asynchronous event streaming.
2. **Handshake Definition**: Implement the `AGENT_HANDSHAKE_TEMPLATE.json` constraints between agents to negotiate capabilities before execution.
3. **Message Routing**: Setup the broker, service mesh, or P2P topology.
4. **Verification**: Execute end-to-end communication tests ensuring agents correctly serialize/deserialize standard schemas. If an agent must also stream UI to a browser, see `a2ui-protocols.skill`.

## Constraints
- Pick one protocol per boundary and write down why; do not mix protocols on the same link.
- Every message type has a schema; a message outside the schema is rejected and logged.

## Output Format
A communication note `docs/AGENT_COMMUNICATION.md` (protocol per link, handshake, message schemas, rate limits, trust zones) and the broker or topology configuration.

## Limits and safety
- An agent in a lower trust zone (for example a public research agent) must not send commands that change state to an agent in a higher zone (for example CI); test that such a message is refused.
- If your platform provides mutual TLS or signed messages, use them between instances that cross a network boundary.
- Set rate limits on agent inboxes and on gossip intervals before starting more than one agent.
- Facts received from another agent are checked by a command or a source before they enter the context; log message schemas to spot an invented protocol variant.
