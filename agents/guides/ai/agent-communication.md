# Agent Communication Guide: MCP, A2A, & Swarms

> **Goal**: Enable agents to stop being lonely chatbots and start working as a cohesive, multi-agent system (MAS).

---

## 1. The Communication Stack

Just like the OSI model for networking, Agentic Systems have layers:

| Layer | Protocol | Purpose | Example |
|---|---|---|---|
| **L7 Application** | **MCP** / **A2A** | Semantics (Tools vs Tasks) | "Use tool X" / "Do task Y" |
| **L6 Presentation** | JSON / MsgPack | Serialization format | `{"jsonrpc": "2.0"}` |
| **L5 Session** | **Handshake** | Identity & Capability verify | `AGENT_HANDSHAKE_TEMPLATE` |
| **L4 Transport** | HTTP / SSE / Stdio | Moving bytes | `POST /rpc` |

---

## 2. Protocol Breakdown

### A. Model Context Protocol (MCP)
**Best for**: "Headless" Tool Use & Resource Access.
*   **Role**: Client (LLM) <-> Server (Tools/Data).
*   **Transport**: Stdio (Local), SSE (Remote).
*   **Use Case**: Agent needs to read a file, query a database, or search the web.
*   **Key Concept**: It's about *capabilities*, not high-level reasoning.

### B. Agent-to-Agent (A2A) Protocol
**Best for**: Task Delegation & collaboration.
*   **Role**: Peer <-> Peer.
*   **Transport**: HTTP, WebSockets, or Message Queue (RabbitMQ).
*   **Use Case**: "Frontend Agent" asks "Backend Agent" to design an API.
*   **Key Concept**: It's about *goals* and *outcomes*.

### C. Agent Communication Protocol (ACP / FIPA-ACL)
**Best for**: Complex negotiation and belief sharing (Academic/Enterprise).
*   **Structure**: Performative (Request/Inform/Propose) + Content.
*   **Use Case**: "I propose doing X for price Y." -> "Accepted."

---

## 3. Topologies

### Local Swarm (Loki Mode)
*   **Type**: **Star Topology** (Hub & Spoke).
*   **Hub**: `loki-mode.skill` (The Orchestrator).
*   **Nodes**: Ephemeral personas (Coder, Reviewer).
*   **Transport**: Function Calls (in-memory) or Stdio.
*   **Pros**: Fast, simple context sharing. **Cons**: Single point of failure.

### Remote Mesh (Micro-Agents)
*   **Type**: **Mesh Topology**.
*   **Nodes**: Independent services (containers/lambda).
*   **Transport**: HTTP/REST or gRPC.
*   **Service Discovery**: Consul / K8s DNS.
*   **Pros**: Scalable, resilient. **Cons**: Complexity, network latency.

### Hybrid (The "Pod" Model)
*   **Structure**: Local pods of 3-4 agents (Dev Pod, QA Pod) talking internally via Stdio, externally via HTTP.

---

## 4. Implementation Patterns

### Pattern 1: The "Handshake" (Trust but Verify)
Before exchanging tasks, agents MUST introduce themselves using `coordination/AGENT_HANDSHAKE_TEMPLATE.json`.

```json
// Agent A sends:
{
  "identity": {"role": "planner", "id": "uuid-1"},
  "protocols": ["mcp", "a2a"]
}

// Agent B replies:
{
  "status": "accepted",
  "identity": {"role": "coder", "id": "uuid-2"}
}
```

### Pattern 2: The "Contract Net" (Marketplace)
1.  **Manager**: Broadcasts: "Who can build a React component?"
2.  **Worker A**: "I can. (Cost: Low, Speed: Fast)"
3.  **Worker B**: "I can. (Cost: High, Speed: Medium)"
4.  **Manager**: Awards task to Worker A.

### Pattern 3: The "Blackboard" (Shared State)
Agents don't talk directly; they write to a shared "Blackboard" (Redis/Database).
*   **Writer**: Puts "Draft Spec" on board.
*   **Reviewer**: Sees new "Draft Spec", critiques it, writes "Review".
*   **Writer**: Sees "Review", updates Spec.

---

## 5. Generic A2A Server Example (Python)

```python
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class AgentMessage(BaseModel):
    sender: str
    content: str
    type: str = "inform" # request, query, propose

@app.post("/a2a/message")
async def receive_message(msg: AgentMessage):
    # 1. Validate Sender
    if not is_authorized(msg.sender):
        return {"error": "Unauthorized"}
    
    # 2. Process Protocol
    if msg.type == "request":
        # ... trigger internal reasoning ...
        response = agent_core.think(msg.content)
        return {"status": "success", "response": response}
    
    return {"status": "received"}
```

---

## 6. Integrating with Loki (This Kit)

1.  **Define Peers**: Add them to `coordination/SWARM_CONFIG_TEMPLATE.json`.
2.  **Connect**: Use `agent-interop.skill` to establish the link.
3.  **Collaborate**:
    *   *Human*: "Ask the Security Agent to review this."
    *   *Loki*:
        1.  Loads `agent-interop`.
        2.  Connects to `http://security-agent:8080`.
        3.  Sends A2A "Review Request".
        4.  Awaits response.
        5.  Integrates feedback into context.
