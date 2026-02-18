# WORKING_MEMORY_TEMPLATE.md — Cognitive Context

> **Purpose**: Snapshot of the Agent's current "headspace" (short-term memory).
> **Updated by**: `working-memory.skill.md`
> **Read by**: All skills (to understand immediate context)

## 1. Current Focus (The "Spotlight")
*What is the ONE thing we are doing right now?*
- **Task**: [e.g., Debugging the auth middleware]
- **Goal**: [e.g., Fix the 401 error on login]
- **Step**: [e.g., Analyzing the JWT token payload]

## 2. Active Context (The "Stage")
*What files/variables/concepts are currently "loaded" in mind?*
- **Files**:
  - `src/auth/middleware.ts`
  - `src/utils/jwt.ts`
- **Variables/Data**:
  - `token_expiry` (seems short)
  - `user_id` (undefined in logs)
- **Constraints**:
  - Must not break existing session flow
  - Must work with mobile app

## 3. Immediate Sketchpad
*Scratchpad for intermediate thoughts, calculations, or temporary logic.*
- `token` is generated at `10:00`, expires at `10:05`.
- User tries to use it at `10:06`.
- *Hypothesis*: Clock skew between server and client?

## 4. Pending Interrupts
*Things we pushed to the background to focus on the Spotlight.*
- [ ] Check if Redis is full (low priority)
- [ ] Review PR #123 (after this bug fix)
