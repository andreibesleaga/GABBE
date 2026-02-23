---
name: Agent Interoperability
description: Manage connections, handshakes, and protocol negotiation between agents (MCP, A2A, ACP).
triggers: [Connect to agent [Name], Negotiate protocol, Send A2A message, Establish handshake, Join swarm]
tags: [coordination]
context_cost: medium
---
# Agent Interoperability Skill

## Goal

## Role
You are a Network Protocol Engineer responsible for the reliable transport and connection between autonomous agents.

## Steps

1.  **Discovery & Connection**
    -   **Local Swarm**: Read `SWARM_CONFIG_TEMPLATE.json` to find agent endpoints (ports/pipes).
    -   **Remote Mesh**: Query Service Discovery (Consul/mDNS) or check `known_peers` list.
    -   **MCP**: Connect via Stdio (local) or SSE (remote).

2.  **Handshake (The "Hello")**
    -   **Send**: `AGENT_HANDSHAKE_TEMPLATE.json` containing:
        -   `agent_id`: UUID
        -   `protocols`: ["mcp", "a2a-v1", "http-jsonrpc"]
        -   `capabilities`: ["search", "code-write", "review"]
    -   **Receive**: Peer's handshake.
    -   **Verify**: Do protocols match? If yes, upgrade connection.

3.  **Message Transport**
    -   **Format**: Wrap payload in standard envelope (JSON-RPC 2.0 or ACP).
    -   **Serialization**: JSON (text) or MsgPack (binary/performance).
    -   **delivery**:
        -   *Synchronous*: Await response (RPC).
        -   *Asynchronous*: Fire-and-forget (Event).

4.  **Protocol Negotiation**
    -   If Peer supports **MCP**: Use MCP for tool/resource access.
    -   If Peer supports **A2A**: Use A2A for high-level task delegation.
    -   Fallback: HTTP REST API.

## Tools & Commands

```bash
# Test MCP Connection (Stdio)
npx @modelcontextprotocol/inspector <command>

# Send HTTP JSON-RPC
curl -X POST http://agent-b:3000/rpc -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}'

# Check Port Availability
nc -zv localhost 3000
```

## Safety Rules
1.  **Authentication**: Verify `auth_token` in handshake if defined in config.
2.  **Rate Limiting**: Respect `retry-after` headers from peers.
3.  **Timeout**: Fail connection attempts after 10s (don't hang indefinitely).

## Security & Guardrails

### 1. Skill Security (Agent Interoperability)
- **Handshake Authentication**: Always verify `auth_token` or cryptographic signatures (mTLS) during the handshake to prevent unauthorized rogue agents from joining the swarm.
- **Protocol Downgrade Prevention**: Reject connection attempts that try to negotiate insecure fallback protocols (e.g., unencrypted HTTP REST) when secure protocols (MCP over SSE/WSS) are available.

### 2. System Integration Security
- **Strict Rate Limiting**: Enforce rate limits and respect `retry-after` headers to prevent both accidental self-DDoS (thundering herd) and intentional flooding attacks from compromised network segments.
- **Connection Timeouts**: Hardcode tight timeouts (e.g., 10s max) for all connection attempts and data streams to prevent slowloris-style resource exhaustion attacks on the orchestrator.

### 3. LLM & Agent Guardrails
- **Payload Validation Matrix**: Agents parsing inter-agent messages must strictly validate all JSON/RPC payloads against predefined schemas before acting on them, mitigating Cross-Agent Scripting (XAS) or payload injection.
- **Topology Sandboxing**: Ensure agents follow intended network typologies (e.g., a "Researcher" agent cannot directly open a socket to a "Database" agent if the topology mandates routing through a "Reviewer").
