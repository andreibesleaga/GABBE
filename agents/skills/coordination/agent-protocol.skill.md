---
name: agent-protocol
description: Defines and validates standard communication protocols between agents (A2A).
triggers: [protocol, handshake, ipc, agent-messaging, a2a]
tags: [coordination]
context_cost: low
---
# Agent Protocol Skill

## Goal
To establish standard interfaces for agents to communicate, ensuring reliable data exchange and preventing format hallucinations.

## Steps
When defining how agents talk to each other:

1.  **Define the Schema**: Use JSON Schema to define the structure of messages.
    -   `type`: (request, response, event, error)
    -   `payload`: The actual data content.
    -   `meta`: Timestamp, sender_id, correlation_id.
2.  **Establish the Handshake**:
    -   **Ping/Pong**: Verify availability.
    -   **Capability Query**: "What tools do you have?" -> "I have [tool_a, tool_b]".
3.  **Standardize Error Handling**:
    -   Define standard error codes (e.g., `AGENT_BUSY`, `INVALID_INPUT`, `CONTEXT_OVERFLOW`).
    -   Define retry policies (exponential backoff).
4.  **Documentation**:
    -   Write the protocol definition to a shared `contracts/` directory or a markdown file.

## Example Protocol (JSON)
```json
{
  "protocol": "v1",
  "type": "task_request",
  "id": "uuid-1234",
  "sender": "orchestrator",
  "recipient": "coder_agent",
  "payload": {
    "task": "Implement login function",
    "context": "User needs email/password auth...",
    "constraints": ["Use bcrypt", "No external auth providers"]
  }
}
```

## Best Practices
-   **Strict Typing**: Always validate payloads against the schema.
-   **Idempotency**: Ensure task requests can be retried without side effects if possible.
-   **Async First**: assume communication is asynchronous; use correlation IDs to match requests and responses.

## Security & Guardrails

### 1. Skill Security (Agent Protocol)
- **Schema Strictness**: All inter-agent message schemas must reject unknown or extraneous fields (`additionalProperties: false` in JSON Schema) to prevent unexpected payload execution or memory bloat.
- **Cryptographic Signatures**: For sensitive commands (e.g., "Deploy to Prod"), the protocol payload must include a verifiable signature (JWT or raw ed25519) proving the sender's identity.

### 2. System Integration Security
- **Replay Attack Defense**: Include and verify timestamps, nounces, or unique `correlation_id` fields in every message to ensure a malicious actor cannot capture and replay a valid action.
- **Error Obfuscation**: Standard error codes (`INVALID_INPUT`) must not leak sensitive stack traces or internal environment variables back to the sender, especially across different trust domains.

### 3. LLM & Agent Guardrails
- **Semantic Injection Blocks**: The receiving agent's LLM prompt must treat incoming `payload.context` as untrusted user input, carefully escaping it to prevent a compromised sender agent from executing prompt injection on the receiver.
- **Capability Falsification Prevention**: During the capability query ("What tools do you have?"), agents must have their claims verified by a central registry or signed certificate, preventing a rogue agent from claiming `admin-level` capabilities it doesn't possess.
