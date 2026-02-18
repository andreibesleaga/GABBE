---
name: realtime-comm
description: WebSocket handling, Pub/Sub patterns, and persistent connections.
role: eng-backend
triggers:
  - websocket
  - socket.io
  - realtime
  - pubsub
  - streaming
  - sse
---

# realtime-comm Skill

This skill guides the implementation of bi-directional, stateful communication.

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
