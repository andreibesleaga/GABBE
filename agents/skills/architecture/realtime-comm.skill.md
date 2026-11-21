---
name: realtime-comm
description: Design of real-time features — WebSocket, SSE or long polling choice, scaling with Redis pub/sub, heartbeats, authentication and limits. Use when adding chat, live updates or any persistent connection.
triggers: [realtime comm, websocket, server-sent events, pub/sub, live updates, long polling]
tags: [architecture]
role: eng-backend
context_cost: low
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

## Constraints
- State lives in shared storage (Redis), not in local memory.
- Clients reconnect with exponential backoff.

## Output Format
The protocol choice with its reason and the implementation following the checklist in section 3.

## Limits and safety
- Authenticate before the upgrade to WebSocket and check the `Origin` header in the handshake.
- Set a maximum message size and a rate limit on the server; a fallback transport (long polling) gets the same authentication and limits.
- Handle token expiry or revoked permissions mid-session: close the connection or re-check authorization on each message.
- Channel names include the tenant; a user can subscribe only to channels they may read.
