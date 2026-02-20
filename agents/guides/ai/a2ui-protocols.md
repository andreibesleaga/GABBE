# A2UI & Generative UI Protocols

**Standardizing how Agents draw Interfaces.**

This guide covers the **A2UI (Agent-to-User Interface)** protocol and related standards for 2026.

---

## 1. What is A2UI?

A2UI is a **Declarative JSON Protocol** that allows an AI Agent to describe a UI without writing executable code (JS/Swift).
*   **Security:** Agent cannot execute arbitrary scripts (XSS protection).
*   **Native:** The Client (Web, iOS, Flutter) decides how to render the JSON.

### The A2UI Payload Structure
```json
{
  "type": "column",
  "children": [
    { "type": "text", "content": "System Status", "style": "h1" },
    { "type": "card", "status": "critical", "children": [
        { "type": "text", "content": "Database Latency High" },
        { "type": "button", "action": "restart_db", "label": "Fix it" }
    ]}
  ]
}
```

---

## 2. AG-UI (Agent-User Interaction)

While A2UI defines the *View*, AG-UI defines the *Transport*.
*   **Streaming:** AG-UI supports JSON-Patch streaming, so the UI builds up token-by-token.
*   **Events:** How the "Click" on the UI gets sent back to the Agent.

**Flow:**
1.  User clicks "Fix it" (Client).
2.  AG-UI sends event `{"action": "restart_db"}` to Agent.
3.  Agent processes, tool calls, and sends new A2UI patch `{"op": "replace", "path": "/card/status", "value": "healthy"}`.

---

## 3. Implementation Strategies

### Strategy A: Vercel AI SDK (RSC)
*   **Tech:** React Server Components.
*   **Mechanism:** Agent streams actual React Components.
*   **Pros:** Full power of React.
*   **Cons:** Web only (React).

### Strategy B: Google A2UI (JSON)
*   **Tech:** JSON Schema.
*   **Mechanism:** Agent streams JSON, Client maps to Flutter/Swift/DOM.
*   **Pros:** True Cross-Platform (Mobile/Web/CLI).
*   **Cons:** Limited to supported primitives.

---

## 4. Designing for A2UI

When building skills for A2UI (like `coding/ui-gen.skill.md`), teach the Agent to:
1.  **Prefer Semantics:** Use "Card", "Alert", "List" (A2UI types) instead of `div` or `span`.
2.  **Statelessness:** Assume the UI is projected state. Don't ask the UI to remember things; the Agent remembers.
3.  **Progressive Disclosure:** Start with a summary, offer a "Drill Down" action.

---

## 5. Future 2027+
*   **Generative ASM (App State Matrix):** Agents controlling the entire app state via Redux/MobX updates.
*   **Neuro-Symbolic UI:** UI elements that adapt their layout based on the user's cognitive load (sensed via webcam/biometrics).
