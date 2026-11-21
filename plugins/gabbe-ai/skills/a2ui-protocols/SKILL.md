---
name: a2ui-protocols
description: "Design the message schema and streaming events an agent uses to send UI to a frontend (JSON, WebSocket, SSE, HTMX). Use when an agent must stream components or UI updates to a browser."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ai/a2ui-protocols.skill.md"
  tags: "ai"
  core: "false"
  context_cost: "medium"
---
# a2ui-protocols

## Goal
Design, enforce, and integrate robust Agent-to-UI (A2UI) communication protocols using Generative UI and HTMX conventions.

## Steps
1. **Analyze Requirements**: Understand the data exchanged between the agent and the frontend UI.
2. **Design Protocol**: Define the JSON schema, WebSocket events, or Server-Sent Events (SSE) required for the agent to stream UI components.
3. **Implement A2UI**: Configure the backend to serve dynamic UI chunks (e.g., using React Server Components, HTMX responses).
4. **Verify**: Ensure the UI updates smoothly without full page reloads and maintains state. For the front-end views that show agent traces and tool calls, see `agent-ui.skill`.

## Constraints
- The agent may stream only components that exist in the project's design system; unknown component names are rejected by the receiver, not rendered.
- Every message type has a written schema; the UI never executes code or HTML taken from a message field.

## Output Format
A protocol note `docs/A2UI_PROTOCOL.md` (message types with their JSON schema, transport, ordering and error events) and the backend and frontend code that implements it.

## Limits and safety
- Reject UI messages that do not match the schema, and cap payload size and open connections; test both limits with an oversized message.
- Set an explicit CORS origin list on every REST, SSE and WebSocket endpoint; a wildcard origin is a finding.
- The client must not be able to set the agent context id or session token; check that a forged id is refused.
- Set a timeout on streaming responses so one agent run cannot stream UI forever.
