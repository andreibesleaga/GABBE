---
name: state-management
description: "Frontend state architecture — which data is server, UI, global or URL state, library choice and state machines. Use when a web app has prop drilling, duplicated state or an unclear data flow."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/state-management.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "low"
---
# state-management Skill

## Goal
This skill guides the architecture of frontend state, avoiding "prop drilling" and "spaghetti state."

## Steps
## 1. Types of State

| Type | Definition | Solution |
|---|---|---|
| **Server State** | Data from API (Users, Posts). | **React Query / SWR / TanStack Query**. Do not use Redux for this. |
| **UI State** | Modals open, Sidebar toggle, Form inputs. | **Local `useState`** or **Context API** or **Zustand**. |
| **Global State** | User session, Theme, Shopping Cart. | **Redux Toolkit / Zustand / Context**. |
| **URL State** | Filters, Pagination, Search Query. | **URL Query Params**. (The URL is the source of truth). |

## 2. Selection Guide

- **Simple App**: `useState` + Context.
- **Medium App (Dashboard)**: Zustand (UI) + TanStack Query (Server).
- **Complex App (Editor, Enterprise)**: Redux Toolkit (if strict structure needed) or XState (state machines).

## 3. Implementation Rules

### 1. Minimal State
- Don't store derived data.
- **Bad**: `{ firstName: 'John', lastName: 'Doe', fullName: 'John Doe' }`
- **Good**: `const fullName = firstName + ' ' + lastName;`

### 2. Single Source of Truth
- If data exists in the URL (`?page=2`), do not duplicate it in a Store.
- The Store should sync *from* the URL, or the URL acts as the store.

### 3. Immutability
- Never mutate state directly (`state.value = 1`).
- Use libraries that enforce this (Immer is built into Redux Toolkit) or spread operators (`...state`).

### 4. Context Performance
- Don't put everything in one `AppProvider`.
- Split contexts: `UserProvider`, `ThemeProvider`, `SettingsProvider`.
- Use `useMemo` for context values to prevent re-renders.

## 4. State Machines (XState)
- Use for complex logic: Payment Flows, Wizards, Game Logic.
- Define explicit states: `idle` -> `loading` -> `success` | `error`.
- Prevents "impossible states" (e.g., `loading: true` AND `error: true`).

## 5. Debugging
- Use Redux DevTools or Zustand DevTools.
- Log state changes in development.
- Monitor render counts (React DevTools Profiler).

## Constraints
- Store no derived data.
- One source of truth: data in the URL is not copied into a store.

## Output Format
A table of the app's state by type (server, UI, global, URL) with the chosen solution for each.

## Limits and safety
- Do not keep access tokens, personal data or secrets in `localStorage`, `sessionStorage` or persisted stores; confirm with the human where the session token lives.
- Client state is untrusted: price, permission and workflow checks, including state machine transitions, are repeated on the server.
- Serialise server-rendered initial state safely (escape it before putting JSON into HTML).
- Cached server data has an expiry or invalidation tied to permission changes.
- Grep the state files for key and secret patterns before handing over.
