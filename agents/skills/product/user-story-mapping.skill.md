---
name: user-story-mapping
description: Visualizing user journeys and slicing deliverables into releases.
triggers: [user story mapping]
tags: [product]
role: prod-pm
---
# user-story-mapping Skill

## Goal
This skill guides the creation of a 2D map of user needs (The Backbone) vs details (The Body) to scope releases.

## Steps
## 1. The Matrix (Backbone vs Body)
- **X-Axis (Backbone)**: The narrative flow. "User Signs Up" -> "Searches Product" -> "Adds to Cart" -> "Checks Out".
- **Y-Axis (Priority)**: Depth of implementation.
  - *Slice 1 (MVP)*: "Sign up via Email".
  - *Slice 2 (v1.1)*: "Sign up via Google".
  - *Slice 3 (v2)*: "Sign up via SSO".

## 2. Process
1.  **Define the Persona**: Who are we mapping for?
2.  **Map the Steps (Activities)**: High-level goals (e.g., "Manage Profile").
3.  **Break into Tasks**: Concrete actions (e.g., "Upload Avatar").
4.  **Slice Lines**: Draw horizontal lines to define Release 1, Release 2, Release 3.

## 3. Output Format
Use `templates/product/USER_STORY_MAP_TEMPLATE.md` to document the outcome.

## 4. The "Walking Skeleton" Strategy
- **Goal**: Implement a tiny slice of the *entire* backbone first.
- **Why**: Proves end-to-end connectivity (Frontend -> Backend -> DB) in Week 1.
- **Example**: "User clicks Buy -> DB records order -> Payment Stubbed -> Email Sent".

## 5. Prioritization Rules (MoSCoW)
- **Must Have**: Without this, it doesn't work.
- **Should Have**: Important constraints (Performance, key features).
- **Could Have**: Delightful add-ons.
- **Won't Have**: Out of scope for now.

## Security & Guardrails

### 1. Skill Security (User Story Mapping)
- **MVP Security Mandate**: The agent must enforce the rule that "Security is not an add-on." Basic authentication, authorization, and data validation tasks *must* be included in Slice 1 (MVP). The agent must actively fight prompts that attempt to push foundational security controls into "v1.1" or "v2".
- **Backbone Vulnerability Analysis**: Once the "Walking Skeleton" (The Backbone) is defined, the agent must trigger a specialized prompt to identify the single highest-risk security node in that end-to-end chain (e.g., the payment stub API interface) and mark it for immediate validation.

### 2. System Integration Security
- **Slice Dependency Integrity**: The agent must prevent the user from defining an integration sequence that causes a security paradox. (For example, attempting to place "Implement User Data Export" in Release 1, but "Implement User Authentication" in Release 2).
- **Graceful Degradation Mapping**: When prioritizing via MoSCoW, the agent must systematically map failure states. If a "Must Have" component fails, what is the defined fallback? The story map must include "Error Handling" stories as native "Body" elements, not as afterthoughts.

### 3. LLM & Agent Guardrails
- **Persona Privilege Escalation**: The LLM must verify that the defined Persona operating the User Journey map does not require unauthorized privilege escalation to complete the targeted "Activities" (e.g., mapping a standard "Client Persona" performing an "Admin Database Dump" activity).
- **Scope Creep Hallucination**: The agent must not spontaneously invent new "Could Have" features to make the story map look more comprehensive. The map must strictly represent the validated constraints defined in the original `PRD.md` or `BUSINESS_CASE.md`.
