---
name: retrospective
description: Runs a blameless retrospective that turns a timeline into a few owned, dated actions and writes the lessons into CONTINUITY.md. Use when a sprint, milestone, incident or phase ends and the team wants lessons and actions recorded.
triggers:
  - run a retrospective for the release milestone
  - do a blameless retro on the sprint
  - what went well and what didnt
  - capture lessons learned into memory
  - hold a start stop continue review
  - retrospective with owned action items
  - feed these lessons into continuity
tags: [core, retrospective, learning, memory]
core: true
context_cost: medium
---
# Retrospective Skill

## Goal
Run a blameless retrospective that turns a completed period of work (sprint, milestone, incident, project phase) into a small set of owned, dated improvement actions and durable lessons. The retro is blameless: it examines the *system and process* that produced an outcome, never an individual's fault. Its lasting value is the feedback loop — lessons are written into `CONTINUITY.md` so future sessions inherit them. The output ties to `PROJECT_RETROSPECTIVE_TEMPLATE.md`.

## Steps
1. **Set the frame.** State the scope and time window under review and the blameless ground rule explicitly: assume everyone did their best with the information they had; focus on process and system, not people.
2. **Gather data — build the timeline.** Reconstruct what actually happened, in order, from objective sources: the audit trail (`audit-trail.skill`), commits, PRs, incidents, telemetry, and milestone dates. A shared factual timeline prevents the retro from drifting into opinion before the facts are agreed.
3. **Pick a format.** Choose one to structure insight-generation: **Start/Stop/Continue** (lightweight, action-oriented), **4Ls** (Liked / Learned / Lacked / Longed-for, reflective), or **Sailboat** (wind = what propels us, anchors = what holds us back, rocks = risks, island = goal). Match the format to the situation; do not run all three.
4. **Generate insights.** Using the chosen format, surface what went well, what didn't, and the *puzzles* — things the team genuinely doesn't understand yet and may need to investigate. Group and cluster related observations; look for root causes, not just symptoms.
5. **Decide actions — few, owned, dated.** Convert insights into a short list (ideally 1-3) of concrete improvement actions. Each action has a single named owner and a due date. Resist the trap of generating a long wish-list that no one executes; a few completed actions beat many ignored ones.
6. **Feed lessons into memory.** Distill durable, reusable lessons (not one-off task notes) and append them to `agents/memory/CONTINUITY.md` so future sessions start with this knowledge. Cross-reference the audit trail for the source events.
7. **Record the retro.** Assemble the timeline, insights, and owned actions into the Output Format below.

## Constraints
- Strictly blameless: no entry may name an individual as the cause of a failure; reframe to systemic factors.
- Build the factual timeline before generating insights — facts first, interpretation second.
- Use exactly one format per retro; do not blend Start/Stop/Continue, 4Ls, and Sailboat into one session.
- Action items are few, each with one named owner and a due date; an action with no owner or date is not recorded as an action.
- Durable lessons (not ephemeral task notes) are appended to `CONTINUITY.md`; appends do not overwrite prior memory.
- The skill facilitates and records; it does not assign blame, and it does not invent timeline facts not supported by sources.

## Output Format
A retrospective record in Markdown following `PROJECT_RETROSPECTIVE_TEMPLATE.md`:
- **Scope & window** — what and when is under review; blameless ground rule stated.
- **Timeline** — ordered factual events with sources (audit trail, PRs, incidents).
- **Format** — which framework was used.
- **Insights** — what went well / what didn't / puzzles, clustered to root causes.
- **Action items** — table of action, single owner, due date, success signal.
- **Lessons → CONTINUITY.md** — the durable lessons appended to memory.

## Limits and safety
- Blameless: name no person as the cause. If asked for a blame report, decline and offer the systemic version.
- Redact credentials, customer data and exploit detail before writing to `CONTINUITY.md`; a security retro keeps details in a restricted file and only the lesson in shared memory.
- Append to `CONTINUITY.md`; never overwrite older entries.
- At most 3 actions, each with one owner and a date; drop any that cannot be owned.
- Build the timeline from the audit log, commits and PRs; mark a fact "unverified" when no source backs it.
