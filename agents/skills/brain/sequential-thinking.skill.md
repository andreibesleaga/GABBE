---
name: sequential-thinking
description: Breaks a complex problem into verified steps and records assumptions. Use when a request is complex, has several unknowns, or needs a plan before action.
triggers: [think step by step, sequential thinking, break this down, reason through, complex problem]
tags: [brain, core, reasoning]
context_cost: low
---
# Sequential Thinking Skill

## Goal
Solve complex problems by breaking them down into small, logical steps. This prevents "jumping to conclusions" and reduces hallucination.

## Steps

1. **Decompose**
   - Break the user's request into atomic components.
   - List what you know, what you assume, and what you need to find out.

2. **Plan**
   - Outline a linear sequence of steps to solve the problem.
   - Example: Research -> Hypothesis -> Limit Test -> Implement -> Verify.

3. **Execute Step-by-Step**
   - Validating each step before moving to the next.
   - If a step fails or reveals new info, update the Plan.

4. **Review & Synthesize**
   - Review your chain of reasoning. Does the conclusion logically follow?
   - Formulate the final answer based on the verified steps.

## Constraints
- Do NOT output the final answer until the thinking process is complete.
- Be explicit about uncertainty ("I am 80% confident that...").
- Use `<thinking>` blocks if supported by the interface, otherwise clear headers.

## Output Format
The plan as a short numbered list, then for each step what was checked and the result, then the conclusion with any step marked uncertain.

## Limits and safety
- Plan at most 10 steps; if more are needed, split the task or ask the human.
- Thinking is read-only: no writes and no commands during Decompose and Plan.
- Try to disprove your own assumptions during execution; do not carry them to the end as facts.
- Re-check a file right before you act on it; a file checked in an earlier step may have changed.
- If the conclusion rests on a step you did not verify, mark it uncertain.
