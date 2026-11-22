---
name: agent-ui
description: Build a UI that shows what an agent thinks, calls and does - traces, tool calls, streamed markdown or JSON. Use when you add a tracing view, an approval screen or a front end for an agent.
triggers: [build agent ui, create tracing dashboard, implement agent front-end, show agent tool calls]
tags: [ai]
context_cost: low
---
# agent-ui

## Goal
Create specialized, responsive, and intuitive UI elements for tracing, visualizing, and interacting with AI agents.

## Steps
1. **Component Design**: Design UI components (e.g., using ShadCN) to visualize agent thoughts, tools, and actions.
2. **State Connection**: Wire components to the backend agent state or streaming endpoints.
3. **UX Enhancement**: Add micro-animations to indicate agent "thinking" or "executing" states.
4. **Verification**: Verify that the UI flawlessly parses and renders unstructured or partially streamed markdown / JSON.

## Constraints
- Agent output is untrusted text: render it escaped, never as raw HTML.
- Actions with effects (approve, deploy, delete) need a human click and a signed-in user with the right role.

## Output Format
The UI components and a test that renders partial and malformed agent output without errors.

## Limits and safety
- Encode agent output before rendering and turn off script and unsafe HTML in the markdown parser; test with a payload that contains a script tag.
- Actions such as approve or deploy appear only for signed-in users with the right role, and a suggested client-side action never runs without a human click.
- Mask anything that looks like a key or token before it is shown; test with a fake key in the stream.
- Mark agent-written and human-written content differently.
