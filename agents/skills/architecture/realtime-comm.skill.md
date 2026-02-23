---
name: realtime-comm
description: WebSocket handling, Pub/Sub patterns, and persistent connections.
triggers: [realtime comm]
tags: [architecture]
role: eng-backend
---
# realtime-comm Skill

## Goal
This skill guides the implementation of bi-directional, stateful communication.

## Steps
## 1. Protocol Selection

| Protocol | Use Case | Pros | Cons |
|---|---|---|---|
| **WebSockets** | Chat, Games, Collaboration | Full Duplex, Low Latency. | Stateful (hard to scale). |
| **SSE (Server-Sent Events)** | Stock Tickers, Notifications | Simple (HTTP), Auto-reconnect. | One-way (Server -> Client). |
| **Long Polling** | Legacy Support | Works everywhere. | High server resource usage. |

## 2. Scaling (The Hard Part)
- **Problem**: Client A connects to Server 1. Client B connects to Server 2. A sends message to B. Server 1 doesn't know B.
- **Solution**: **Redis Pub/Sub Adapter**.
  - Server 1 publishes event to Redis channel `room:123`.
  - Server 2 subscribes to `room:123` and forwards to Client B.

## 3. Implementation Checklist
- [ ] **Heartbeats**: Ping/Pong every 30s to keep connection alive through Load Balancers.
- [ ] **Authentication**: Authenticate *before* upgrade (pass Token in Query Param or Cookie).
- [ ] **Reconnection logic**: Exponential backoff on client.
- [ ] **State**: Store `socket_id` -> `user_id` mapping in Redis, not local memory.

## 4. Security
- **Origin Check**: Validate `Origin` header during handshake.
- **DoS Protection**: Limit message size (e.g., max 1KB).
- **Auth**: Validate token on every distinct action if connection is long-lived.

## Security & Guardrails

### 1. Skill Security (Realtime Communication)
- **Pre-Upgrade Authentication Mandate**: The agent must strictly forbid architectures that upgrade the HTTP connection to a WebSocket *before* verifying authentication. WebSocket connections consume significant stateful resources (RAM/TCP ports) per user. Authenticating *after* the upgrade exposes the server to trivial layer-7 DoS attacks holding open dead connections.
- **Message Size Limiting (BOMB Deflection)**: The agent must hardcode maximum payload sizes for incoming WebSocket messages (e.g., 1KB for chat, 10KB for sync). Without rigid chunking or drop limits, an attacker can crash the Node.js/Python event loop by streaming a gigabyte-sized JSON payload over a single persistent socket.

### 2. System Integration Security
- **Cross-Site WebSocket Hijacking (CSWSH)**: Unlike standard CORS, WebSockets do not strictly enforce Same-Origin Policies by default. The agent must explicitly configure the WebSocket server to validate the `Origin` header during the initial HTTP handshake, dropping connections from unapproved external domains attempting to hijack the user's active session.
- **Pub/Sub Tenant Isolation**: When scaling horizontally via a Redis Pub/Sub adapter (Step 2), the agent must heavily scrutinize channel naming conventions. A flaw in channel names (e.g., `room:user_input`) could allow a malicious user to subscribe to or publish messages to a different tenant's WebSocket stream, breaking data isolation bounds.

### 3. LLM & Agent Guardrails
- **Hallucinated Stateful Immunity**: The LLM might assume that because a user authenticated at connection time, they are trusted forever. The agent must correct this: if a JWT expires or a user's permissions are revoked mid-session, the architecture must include a mechanism to forcefully sever active WebSocket connections or re-validate authorization on every distinct incoming message.
- **Protocol Downgrade Exploits**: When configuring fallback mechanisms (e.g., Long Polling if WebSockets fail), the LLM might suggest loosening security rules for the fallback transport. The agent must enforce that all fallback mechanisms require the exact same stringent Authentication and Rate Limiting constraints as the primary WebSocket protocol.
