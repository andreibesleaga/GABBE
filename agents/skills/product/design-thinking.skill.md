---
name: design-thinking
description: Apply the Design Thinking process (Empathize, Define, Ideate, Prototype, Test) to solve complex user problems.
triggers: [design thinking, empathize, user journey, persona, ideation, brainstorming, prototype, user research]
tags: [product]
context_cost: medium
---
# Design Thinking Skill

## Goal
To solve problems from a human-centric perspective. This skill guides the agent and user through the double-diamond process: discovering the right problem (diverge/converge) and designing the right solution (diverge/converge).

## Steps

1.  **Empathize (Understand the User)**
    *   Create **Empathize Maps** (Says, Thinks, Does, Feels).
    *   Develop **Personas** (if not already existing in `agents/personas`).
    *   Capture **User Stories** from the user's perspective.
    *   *Output:* `docs/strategic/EMPATHY_MAP.md`

2.  **Define (The Problem Statement)**
    *   Synthesize findings into a clear Point of View (POV).
    *   Format: "User [X] needs [Y] because [Z] (insight)."
    *   Create **How Might We (HMW)** questions to frame the challenge.
    *   *Output:* Updated `docs/strategic/PROBLEM_STATEMENT.md`

3.  **Ideate (Generate Solutions)**
    *   Brainstorm wide range of solutions for the HMW questions.
    *   Techniques: Crazy 8s, SCAMPER, Worst Possible Idea.
    *   Select top ideas based on Desirability, Viability, Feasibility.
    *   *Output:* `docs/strategic/IDEATION_LOG.md`

4.  **Prototype (Low-Fidelity)**
    *   Describe key user flows (Text-based wireframes).
    *   Generate Mermaid sequence or state diagrams for flows.
    *   Concept validation before coding.

5.  **Test (Validation)**
    *   Define validation criteria for the prototype.
    *   Examples: "User can complete flow X in < 3 clicks".

## Integration with SDD
*   The output of *Define* and *Prototype* feeds directly into `spec-writer.skill` (S01 Requirements).
*   *Design Thinking* finds the "Right Thing to Build". *SDD* ensures we "Build the Thing Right".

## Constraints
*   Do not jump to solution code. Stay in the problem space during Empathize/Define.
*   Focus on user *needs*, not just business requirements.

## Output Format
The files named in each step under `docs/strategic/` (`EMPATHY_MAP.md`, `PROBLEM_STATEMENT.md`, `IDEATION_LOG.md`) and, for the prototype, a text flow or Mermaid diagram with its validation criteria.

## Limits and safety
- Personas and empathy maps are synthetic composites: no real names, customer transcripts or personal data.
- Mark `IDEATION_LOG.md` as DRAFT; ideas in it are not approved for implementation.
- Write at least one adversarial persona (abuse case) beside the happy-path personas.
- Prototypes are text or diagrams only; do not create cloud resources or executables.
- Do not frame a problem statement whose only solution is surveillance of users.
