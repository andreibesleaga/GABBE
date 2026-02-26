---
name: stakeholder-management
description: Matrices for managing expectations and communication plans.
triggers: [stakeholder management]
tags: [product]
role: prod-pm
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

## Security & Guardrails

### 1. Skill Security (Stakeholder Management)
- **Role-Based Deception Prevention**: The Stakeholder map (Power/Interest Grid) must never be altered by the agent to artificially inflate the authority of an unauthorized user. A developer account cannot prompt the agent to move itself into the "Key Player / Executive" quadrant to bypass feature approval gates.
- **Communication Channel Integrity**: The "Communication Plan" generator must only schedule updates to verified, internal corporate channels (e.g., Slack `#internal-eng`, corporate email). The agent must actively decline requests to post roadmap updates or RACI charts to public/external platforms.

### 2. System Integration Security
- **Security Checkpoint Integration**: The RACI matrix MUST inherently include a `Consulted` (C) or `Accountable` (A) role for "Security/AppSec" on all deliverables involving customer data, authentication, or infrastructure changes. The agent must reject matrixes that isolate engineering from security review.
- **Need-to-Know Alignment**: When generating the weekly status reports, the agent must scrub highly sensitive vulnerability details, active incident data, and unpatched CVEs from the broad "Keep Informed" stakeholder newsletters to prevent the tactical leak of actionable intel to the wider crowd.

### 3. LLM & Agent Guardrails
- **Manipulative Persuasion Blocks**: The agent must refuse prompts instructing it to generate "gaslighting" communication templates or reports designed to actively deceive a stakeholder about a security incident, data breach, or slipped technical debt deadline.
- **Unauthorized Conflict Resolution**: While practicing "Disagree and Commit", the agent must never unilaterally override a stated security constraint (e.g., "We can skip the pen-test, it delays launch by 2 weeks. Is that acceptable?"). Security overrides require explicit, human, executive sign-off.
