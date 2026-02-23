---
name: sequential-thinking
description: Break down complex problems into a step-by-step chain of thought for better reasoning
triggers: [think, reason, complex, plan, analyze, sequential]
tags: [brain, core, reasoning]
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

4. **Review & Sythesize**
   - Review your chain of reasoning. Does the conclusion logically follow?
   - Formulate the final answer based on the verified steps.

## Constraints
- Do NOT output the final answer until the thinking process is complete.
- Be explicit about uncertainty ("I am 80% confident that...").
- Use `<thinking>` blocks if supported by the interface, otherwise clear headers.

## Security & Guardrails

### 1. Skill Security (Sequential Thinking)
- **Plan Immobilization (Analysis Paralysis)**: During the "Plan" phase (Step 2), an attacker can feed the agent an infinitely recursive logic puzzle or an undecidable dependency graph. The agent must enforce strict bounds on the "Decompose" and "Plan" mechanisms—if the sequence string exceeds a maximum token length or a defined depth (e.g., 10 steps), the agent must forcibly break the thinking chain and execute a fallback action (Ask User/Halt).
- **Execution Drift Exploitation**: In "Execute Step-by-Step" (Step 3), an attacker might manipulate the environment while the agent is between steps. If Step 1 verifies a file's safety, and Step 2 executes it, a Time-of-Check to Time-of-Use (TOCTOU) vulnerability exists. The agent must mathematically guarantee the integrity of artifacts across sequential steps, using file locks or cryptographic hashing directly in its reasoning chain.

### 2. System Integration Security
- **Thought-Space Data Leakage**: The skill mandates making the thinking process explicit (`<thinking>` blocks). While excellent for explainability, this forces the LLM to write out raw API keys, passwords, or PII as it evaluates them sequentially. The integration environment MUST intercept and aggressive mask `<thinking>` block outputs before they are routed to user-facing UIs or external telemetry dashboards.
- **State Mutation in Mental Drafts**: The agent is commanded to plan before acting. However, if the agent uses actual bash tools (like writing a rapid script) *during* the decomposition phase simply to "test a hypothesis," it violates the premise of sequential thought and risks executing arbitrary commands. "Thinking" steps must be explicitly bound to read-only or strictly sandboxed memory spaces.

### 3. LLM & Agent Guardrails
- **The Confident Conclusion Hallucination**: During "Review & Synthesize" (Step 4), the LLM might hallucinate a correlation between its sequential steps that does not mathematically exist (e.g., "Step 1 returned true, Step 2 returned the number 5, therefore the security breach is mitigated"). The agent must rigidly trace the logical dependency graph; if the final conclusion relies on assertions not explicitly proven in Steps 1-3, it must flag the output as uncertain.
- **Assumption Solidification**: The "Decompose" step (Step 1) requires listing "what you assume." The LLM has a tendency to treat assumptions declared in Step 1 as absolute, unassailable facts by Step 3. The sequential thinking prompt must explicitly force the agent to actively test and attempt to disprove its own stated assumptions during the execution phase.
