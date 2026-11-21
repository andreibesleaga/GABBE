---
name: stakeholder-management
description: "Build a power/interest grid, a RACI matrix and a communication plan for the people a project affects. Use when you must align stakeholders, clarify who decides, or plan status updates."
triggers: [stakeholder management, power interest grid, raci matrix, who is accountable, plan status updates, stakeholder conflict]
tags: [product]
role: prod-pm
context_cost: low
---
# stakeholder-management Skill

## Goal
This skill helps Product Managers align diverse groups of people.

## Steps
## 1. Power/Interest Grid (The "Mendelow Matrix")

| Quadrant | Power | Interest | Strategy | Example |
|---|---|---|---|---|
| **Manage Closely** | High | High | **Key Players**. Engage daily/weekly. Co-create. | CTO, VP Product, Key Client. |
| **Keep Satisfied** | High | Low | **Gatekeepers**. Update monthly. Don't bore them. | CFO, Legal, Compliance. |
| **Keep Informed** | Low | High | **Advocates**. Send newsletters. Ask for feedback. | QA, Support Team, Sales Reps. |
| **Monitor** | Low | Low | **Crowd**. Minimal effort. | General employees. |

## 2. RACI Matrix (Who does what?)
- **Responsible**: The doer (Developer).
- **Accountable**: The owner (PM / Tech Lead). Only ONE person.
- **Consulted**: The expert (Architect / Security). Two-way comms.
- **Informed**: The notified (Support). One-way comms.

## 3. Communication Plan
- **Daily**: Standup (Team).
- **Weekly**: Status Report (Stakeholders).
  - Format: Green/Yellow/Red status, Highlights, Lowlights, Blockers.
- **Monthly**: Steering Committee (Execs).
  - Format: KPI trends, Roadmap adjustments, Budget.

## 4. Conflict Resolution ("Disagree and Commit")
1.  **Listen**: Ensure they feel heard. "I understand your concern about X".
2.  **Data**: Use data, not opinion. "Analytics show 99% of users don't use feature Y".
3.  **Trade-off**: "We can do X, but it delays Y by 2 weeks. Is that acceptable?"

## Constraints
- One Accountable person per deliverable in the RACI.
- Use data, not opinion, in a conflict, and record the trade-off agreed.

## Output Format
A stakeholder register with the power/interest grid, the RACI matrix and the communication plan (audience, message, channel, frequency), in `docs/stakeholders/STAKEHOLDER_REGISTER.md`.

## Limits and safety
- Do not change the stakeholder map to raise someone's authority; the human owns the map.
- Send plans and reports only to internal channels the human names; do not post roadmaps or RACI charts publicly.
- Keep security as C or A in the RACI for work that touches customer data, authentication or infrastructure.
- Remove vulnerability details, incident data and unpatched CVEs from broad status reports.
- Do not write messages that mislead stakeholders about an incident or a slipped deadline; skipping a security check needs the human's recorded sign-off.
