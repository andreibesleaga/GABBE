# AgentUI: Automatic & Generative User Interfaces

This guide details how to leverage the Agentic Engineering Kit to automatically generate, render, and interact with User Interfaces.

## 1. The Three UI Paradigms

In 2026, Agents build UIs using three distinct paradigms depending on the use case:

| Paradigm | Stack | Best For | Complexity |
|---|---|---|---|
| **Generative UI** | React, Tailwind, ShadCN, Vercel AI SDK | SaaS products, complex dashboards | High |
| **Hypermedia (HTMX)** | Go (Templ), PHP (Blade), Node (EJS) + HTMX | Internal tools, admin panels, low-latency | Low |
| **Terminal (TUI)** | Go (Bubble Tea), Node (Ink), Python (Textual) | Dev tools, scripts, headless servers | Medium |

---

## 2. Generative UI (The "v0" Style)

**Concept:** The Agent doesn't just write code; it streams UI components that render in real-time.

### Stack Recommendations
*   **Framework:** Next.js (App Router) / Vite
*   **Styling:** Tailwind CSS v4
*   **Components:** ShadCN UI (Radix Primitives)
*   **Icons:** Lucide React

### Agent Pattern
To generate a UI, the agent must:
1.  **Visualize:** Describe the component tree first.
2.  **Scaffold:** Generate the wrapping code (imports, exports).
3.  **Refine:** Add Tailwind classes for "Vibe Coding" (see `coding/vibe-coding.skill.md`).

**Example Prompt:**
> "Create a dashboard for a FinOps Agent. Use a dark glassmorphism theme. Include a LineChart for daily spend and a DataTable for recent transactions. Use ShadCN cards."

---

## 3. HTMX-First Agent UIs

**Concept:** "HTML over the Wire". The Agent generates semantic HTML fragments instead of JSON. This is often *faster* because the Agent understands HTML structure better than complex JSON schemas.

### Why Agents Love HTMX
*   **Self-Describing:** HTML contains both data and layout.
*   **No State Sync:** The DOM is the source of truth.
*   **Low Hallucination:** Agent simply outputs `<div class="alert">Success</div>` rather than complex state mutations.

### Backend Patterns

#### Go (Golang) + Templ
```go
// agent_view.templ
templ AgentResponse(msg string) {
  <div class="p-4 bg-blue-100 rounded-lg" hx-swap="outerHTML">
    <p>{ msg }</p>
  </div>
}
```

#### PHP + Laravel Blade
```blade
<!-- agent-response.blade.php -->
<div hx-target="this" hx-swap="outerHTML">
    @if($agent->isThinking)
        <span class="animate-pulse">Thinking...</span>
    @else
        {{ $response }}
    @endif
</div>
```

---

## 4. TUI: Command Line Interfaces

**Concept:** For infrastructure agents or developer tools, a TUI is often superior to a web UI.

### Stack Recommendations
*   **Go:** [Bubble Tea](https://github.com/charmbracelet/bubbletea) (The gold standard)
*   **TypeScript:** [Ink](https://github.com/vadimdemedes/ink) (React for CLI)
*   **Python:** [Textual](https://github.com/textualize/textual)

### Auto-Generation Strategy
1.  **Define Schema:** Agent reads `openapi.yaml` or `config.json`.
2.  **Generate Model:** Agent maps schema fields to TUI inputs (TextInputs, Selects).
3.  **Generate View:** Agent layouts the TUI (Lists on left, Details on right).
4.  **Generate Update:** Agent wires keypress events (Enter to submit).

---

## 5. Agent-to-No-Code Bridge

Sometimes the best UI is *no code*.

*   **v0 / Bolt.new**: Agent generates the prompt for these tools.
*   **Retool / Appsmith**: Agent generates a JSON config to import.
*   **Streamlit / Gradio**: Agent writes a single Python script for an instant Data UI.

---

## 6. Optimization & Performance

*   **Streaming:** Always stream Agent responses. For HTMX, utilize Server-Sent Events (SSE).
*   **Optimistic UI:** Agent should generate "Skeleton Loaders" while "thinking".
*   **Caching:** Cache generated UI fragments if they are static (e.g., headers, layouts).

See `skills/coding/ui-gen.skill.md` for the specific instructions on how to invoke these patterns.
