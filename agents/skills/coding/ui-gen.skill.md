---
name: ui-gen
description: "Generate a user interface (React with Tailwind, HTMX fragments, a terminal UI or a Streamlit app) after choosing the paradigm that fits the stack. Use when the user asks for a dashboard, frontend, internal tool UI or CLI interface."
triggers: [generate a ui, build a dashboard, htmx page, terminal ui, react component with tailwind, internal tool frontend]
tags: [coding]
context_cost: medium
tools: [write_to_file, replace_file_content]
---
# UI Generation Skill

## Goal
Use this skill when the user asks for a User Interface, Dashboard, CLI tool, or Frontend.

## Steps
## 1. Paradigm Selection
First, determine the best paradigm based on the User's Stack and needs:

| Scenario | Recommended Paradigm |
|---|---|
| "Modern SaaS", "React", "Dashboard" | **Generative UI** (React/ShadCN/Tailwind) |
| "Internal Tool", "Go/PHP/Node Backend" | **HTMX** (Hypermedia-driven) |
| "Dev Tool", "Script", "Server Utils" | **TUI** (Bubble Tea / Ink) |
| "Quick Prototype", "Data App" | **Streamlit / Gradio** (Python) |

For native iOS, Android or React Native apps use `mobile-dev.skill`.

## 2. Generative UI Workflow (React/ShadCN)
1.  **Dependencies:** Ensure `lucide-react`, `clsx`, `tailwind-merge` are installed.
2.  **Component:** Create a single-file component if possible, or modularize if complex.
3.  **Style:** Use Tailwind CSS. Focus on "Vibe Coding" (Dark mode, gradients, glassmorphism).
4.  **Mocking:** If backend is missing, mock data inside the component.

## 3. HTMX Workflow
1.  **Route:** Create a backend route (e.g., `GET /partials/dashboard`).
2.  **Template:** Return *only* the HTML fragment (no `<html>` or `<body>` unless it's the full page).
3.  **Interactivity:** Use `hx-get`, `hx-post`, `hx-trigger`.
    *   Example: `<button hx-post="/update" hx-swap="outerHTML">Save</button>`

## 4. TUI Workflow
1.  **Library:** Use Bubble Tea (Go) or Ink (Node).
2.  **Model:** Define the State (Cursor position, Input value).
3.  **Update:** Define the Keypress handlers.
4.  **View:** Return the String representation of the UI.

## 5. Security Checklist
- [ ] **XSS Prevention:** Ensure all user input is escaped (React/Templ do this automatically).
- [ ] **Validation:** Client-side validation is UX, Server-side is Security. Do both.
- [ ] **Access Control:** UI elements should simply *not exist* if the user lacks permission.

## 6. Artifact Generation
When generating the UI, create a `UI_SPEC.md` first if the complexity is high ( > 5 components).
Otherwise, write the code directly.

## Constraints
- Escape all user input in the view layer; validate on the server as well as the client.
- Hide elements the user may not use by not rendering them, and enforce the same rule on the server.

## Output Format
The UI code files, and a `UI_SPEC.md` first when there are more than 5 components.

## Limits and safety
- Bind user data with the framework's safe bindings; use `dangerouslySetInnerHTML` only after a sanitiser such as DOMPurify.
- Client-side validation is cosmetic: confirm the server enforces the same rule and name the endpoint.
- HTMX fragment routes use the same authentication and permission middleware as full pages.
- In a TUI strip ANSI control sequences from untrusted text before drawing it.
- Build only the components asked for (or listed in `UI_SPEC.md`); add no unrequested admin actions.
- Use locally installed packages, not CDN script tags.
