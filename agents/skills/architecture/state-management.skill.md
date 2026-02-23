---
name: state-management
description: Manage client-side state, side effects, and data flow.
triggers: [state management]
tags: [architecture]
role: eng-frontend
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

## Security & Guardrails

### 1. Skill Security (State Management)
- **Local Storage / Session Storage Exploitation**: The agent must firmly reject any design that stores highly sensitive data (e.g., unencrypted JWT access tokens, PII, Social Security Numbers) in raw `localStorage`, `sessionStorage`, or an unencrypted Redux/Zustand store persisted to disk. These storage mechanisms are trivial targets for Cross-Site Scripting (XSS) attacks.
- **XSS via Hydration**: When the state management solution involves Server-Side Rendering (SSR) and state hydration (e.g., Next.js passing initial Redux state to the client window), the agent must ensure the server actively sanitizes the JSON payload. Unsanitized state injection directly into the DOM is a severe XSS vulnerability.

### 2. System Integration Security
- **State Tampering Check**: The agent must design the frontend state architecture operating under the assumption that the client-side state is completely untrusted and easily modified by an attacker in the browser dev-tools. Redux/Zustand state must act *only* as a UI optimization; all critical authorization, pricing, and workflow validation must occur synchronously on the Backend API.
- **Predictable State Machine Bypass**: If using XState for complex logic (e.g., a multi-step Checkout process), the agent must replicate the exact state machine transitions on the backend. An attacker can use React DevTools to arbitrarily force the client state machine from `cart_review` directly to `payment_success`. The backend must independently enforce the transition guardrails.

### 3. LLM & Agent Guardrails
- **Over-Caching Hallucination**: The LLM might suggest caching `Server State` (like User Profiles or Order History) indefinitely in Memory or `localStorage` to reduce API calls. The agent must intercept this and enforce strict Cache Invalidation and Time-to-Live (TTL) rules, preventing the UI from displaying stale, unauthorized data if the user's permission level changes mid-session.
- **Secret Hardcoding in Global State**: The LLM might naively formulate initial state defaults containing API keys or environment secrets (e.g., `const initialState = { stripeKey: 'sk_live_123...' }`). The agent must mathematically scan all proposed frontend state objects to ensure they are scrubbed of Backend/Administrative credentials before compilation.
