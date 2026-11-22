---
name: change-management
description: Plan and drive organizational change through ADKAR, stakeholder comms cadence, training, and resistance management.
triggers: [plan organizational change, adkar change model, stakeholder communication cadence, build training plan, manage resistance to change, rollout adoption plan, write change management plan]
tags: [product, change, adoption]
core: false
context_cost: medium
---
# Change Management

## Goal
Drive a change — a new product, process, tool, or way of working — to successful, durable adoption by
managing the **people** side of the transition, not just the technical rollout. The core model is **ADKAR**:
individuals adopt change by moving through five sequential states, and an initiative stalls at whichever
state the population is weakest in. The output is a change-management plan that maps the path from current
state to reinforced adoption, ties to `CHANGE_MANAGEMENT_PLAN_TEMPLATE.md`, and is honest that adoption is
earned over time, not announced once.

## Steps
1. **Diagnose the change and its impact.**
   - Define what is changing, who is affected, and how their day-to-day work shifts. Size the change
     (incremental vs disruptive) — the magnitude sets how much effort each ADKAR state needs.
2. **Work the ADKAR sequence.**
   - **Awareness** — make people understand *why* the change is happening and the risk of not changing.
     Without a credible "why," every later step erodes.
   - **Desire** — build the personal motivation to participate. Desire cannot be mandated; address
     "what's in it for me" and the real concerns honestly.
   - **Knowledge** — provide the information and skills (the "how") via training and documentation.
   - **Ability** — convert knowledge into demonstrated capability through practice, coaching, and
     hands-on support; knowing is not the same as being able.
   - **Reinforcement** — sustain the change with recognition, metrics, and corrective action so people do
     not revert. Most change failures happen here, after the launch spotlight fades.
3. **Set the stakeholder communication cadence.**
   - Map sponsors, managers, and affected groups, then schedule layered communications: frequent early
     (Awareness/Desire), shifting to training-focused (Knowledge/Ability), then reinforcement updates.
   - Use the active, visible sponsor as the primary messenger for "why" — the sponsor's credibility is the
     single biggest predictor of success.
4. **Build the training plan.**
   - Define audiences, learning objectives, formats (live, self-serve, job aids), and timing tied to
     go-live so Knowledge lands close to when Ability is needed, not months early.
5. **Manage resistance proactively.**
   - Anticipate likely objections per group, identify root causes (fear, loss, competence, trust), and
     plan specific responses. Treat resistance as signal about real gaps, not as noise to suppress.
6. **Assemble the plan and adoption metrics.**
   - Combine the above into the plan and define how adoption and reinforcement will be measured over time.

## Constraints
- ADKAR states are sequential; the agent MUST NOT plan Knowledge or Ability activities for a population that
  lacks Awareness or Desire — training people who don't want to change wastes effort.
- Adoption is earned progressively and can regress; the plan MUST include reinforcement and never treat a
  launch announcement as completion.
- Desire and resistance cannot be manufactured by coercion or spin; the agent MUST address concerns
  honestly and surface, not suppress, legitimate objections.
- Communications go only to verified internal channels and audiences; do not broadcast internal change
  plans externally.

## Output Format
Produce a change-management plan (aligned to `CHANGE_MANAGEMENT_PLAN_TEMPLATE.md`) containing:
- Change description, impact assessment, and affected groups.
- An ADKAR plan: per state, the goal, the activities, the owner, and the risk if that state is weak.
- A communication cadence: audience, message, channel, frequency, and messenger (with the sponsor named).
- A training plan: audiences, objectives, formats, and timing relative to go-live.
- A resistance-management section: anticipated objections, root causes, and planned responses.
- Adoption and reinforcement metrics with target timeframes.

## Limits and safety
- Do not write messages that misstate the change's impact; list real objections in the resistance section.
- Attribute a message to the sponsor only when the human confirms the sponsor said or approved it.
- Keep reorganisation, layoff and other sensitive detail out of broadly distributed drafts; ask the human who may see each draft.
- Draft only. Do not send communications or grant training access; the human sends after confirming the audience list.
