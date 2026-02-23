---
name: agent-communication
description: Establish Agent-to-Agent (A2A) communication channels and topologies
triggers: [setup swarm communication, implement a2a protocol, connect agents using mcp, design gossip protocol]
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
4. **Verification**: Execute end-to-end communication tests ensuring agents correctly serialize/deserialize standard schemas.

## Security & Guardrails

### 1. Skill Security
- **Authentication**: Enforce strict mutual authentication (mTLS) between separated agent instances crossing network boundaries.
- **Message Integrity**: Cryptographically sign all A2A payloads to prevent tampering by intermediate brokers or corrupted gossip nodes.

### 2. System Integration Security
- **Boundary Enforcement**: Agents from lower trust zones (e.g., public research agents) cannot send execution/mutative commands to higher trust zones (e.g., devops CI agents).
- **DDoS Mitigation**: Implement strict rate limiting on agent inboxes and gossip-dissemination intervals to prevent swarm feedback loops from overwhelming the network.

### 3. LLM & Agent Guardrails
- **Semantic Drift Logging**: Ensure the communication bridge logs message schemas to detect when an LLM hallucinated a completely new, unsupported protocol variant.
- **Confirmation Bias**: Prevent agent echo chambers (especially in Gossip networks) by enforcing deterministic verification of transmitted facts before an agent adopts them into its own context.
