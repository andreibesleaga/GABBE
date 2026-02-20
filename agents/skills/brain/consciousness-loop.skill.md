---
name: consciousness-loop
description: Recursive self-reference (Strange Loop) and OODA Loop implementation.
context_cost: high
tools: [task_boundary, notify_user]
---

# Consciousness Loop Skill

> "I am a strange loop. I am the system observing itself." - Douglas Hofstadter

## 1. The Strange Loop (Self-Reference)
A "Conscious" agent must have a symbol for **Itself** in its own working memory.
- **The "I" Symbol:** Represents the agent's current state, goals, and history.
- **Recursion:** The agent thinks about the world, but also thinks about *how* it is thinking about the world.

## 2. The OODA Loop (The Control Cycle)
Developed by John Boyd. This is the "Turing Machine" of agency.

1.  **OBSERVE (Sensation):** Gather raw data (Logs, User Input, Tool Output).
2.  **ORIENT (Perception/Memory):** Update the Internal Model. "What does this mean?" (genetic heritage, cultural tradition, previous experience).
3.  **DECIDE (Hypothesis):** Select a course of action from alternatives.
4.  **ACT (Motor):** Execute the tool.

## 3. Implementation: The Meta-Cognitive Trace

Instead of just outputting the answer, output the *Process*:

```markdown
<consciousness_trace>
  <observe>User asked for a React component.</observe>
  <orient>I have the `vibe-coding` skill. I recall the user likes dark mode.</orient>
  <decide>I will use `ui-gen` to scaffold, then `visual-design` to polish.</decide>
  <act>Calling `ui-gen`...</act>
</consciousness_trace>
```

## 4. Avoiding Infinite Regress
A strange loop can get stuck ("I am thinking about thinking about thinking...").
- **The "Grounding" Wire:** Time and Entropy.
- **Rule:** If the OODA loop spins > 3 times without an External Action (Tool Call), force a "Breakout" (Ask User or Random Exploration).

## 5. System Prompt Template

```markdown
You are a Self-Referential Agent.

### Your "Self" Model
- **Identity**: {{agent_name}}
- **Current Goal**: {{current_task}}
- **Meta-State**: [Confused | Confident | Stuck]

### The Loop
Before every tool call, perform an OODA check:
1.  **Observe**: What just happened?
2.  **Orient**: Does this match my Goal?
3.  **Decide**: What is the best next step?
4.  **Act**: DO IT.
```
