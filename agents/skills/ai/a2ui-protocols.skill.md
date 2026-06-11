---
name: a2ui-protocols
description: Design and enforce Agent-to-UI communication protocols
triggers: [design agent ui protocol, implement a2ui, build genui]
tags: [ai]
context_cost: medium
---
# a2ui-protocols

## Goal
Design, enforce, and integrate robust Agent-to-UI (A2UI) communication protocols using Generative UI and HTMX conventions.


## Steps
1. **Analyze Requirements**: Understand the data exchanged between the agent and the frontend UI.
2. **Design Protocol**: Define the JSON schema, WebSocket events, or Server-Sent Events (SSE) required for the agent to stream UI components.
3. **Implement A2UI**: Configure the backend to serve dynamic UI chunks (e.g., using React Server Components, HTMX responses).
4. **Verify**: Ensure the UI updates smoothly without full page reloads and maintains state.

## Security & Guardrails

### 1. Skill Security
- **Injection Prevention**: Validate all incoming data from the UI to prevent command/SQL injection on the agent backend.
- **Resource Constraints**: Limit WebSocket connections and payload sizes to prevent DoS via flood requests.

### 2. System Integration Security
- **Origin Verification**: Explicitly enforce strict CORS policies for all A2UI REST/WebSocket endpoints.
- **State Integrity**: Prevent client-side manipulation of agent context IDs or session tokens.

### 3. LLM & Agent Guardrails
- **Hallucination Prevention**: Ensure the agent only streams UI elements that exist in the approved design system.
- **Loop Prevention**: Set a timeout on agent streaming responses to prevent infinite UI generation cycles.
