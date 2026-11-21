---
name: consciousness-loop
description: "Adds an explicit observe, orient, decide, act trace with a breakout after 3 idle spins. Use when an agent keeps reasoning without calling a tool, or when a decision trace is needed."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/consciousness-loop.skill.md"
  tags: "brain"
  core: "false"
  context_cost: "high"
---
# Consciousness Loop Skill

> "I am a strange loop. I am the system observing itself." — Douglas Hofstadter

## Goal
Make the agent's decisions visible and stop it from thinking in circles: a short trace before each tool call, and a hard stop after 3 passes without one.

## 1. The Strange Loop (Self-Reference)
A "conscious" agent holds a symbol for **itself** in working memory.
- **The "I" symbol:** the agent's current state, goals, history.
- **Recursion:** it thinks about the world, and about *how* it is thinking about the world.

## 2. The OODA Loop (Control Cycle)
John Boyd's "Turing Machine" of agency:
1. **OBSERVE (Sensation):** gather raw data (logs, user input, tool output).
2. **ORIENT (Perception/Memory):** update the internal model — "what does this mean?" (heritage, culture, prior experience).
3. **DECIDE (Hypothesis):** select a course of action.
4. **ACT (Motor):** execute the tool.

## 3. Implementation: The Meta-Cognitive Trace
Output the *process*, not just the answer:
```markdown
<consciousness_trace>
  <observe>User asked for a React component.</observe>
  <orient>I have the `vibe-coding` skill. I recall the user likes dark mode.</orient>
  <decide>I will use `ui-gen` to scaffold, then `visual-design` to polish.</decide>
  <act>Calling `ui-gen`...</act>
</consciousness_trace>
```

## 4. Avoiding Infinite Regress
A strange loop can get stuck ("thinking about thinking about..."). Grounding wire = an external action. **Rule:** if the OODA loop spins > 3 times without an external action (tool call), force a "breakout" (ask user or random exploration).

## 5. System Prompt Template
```markdown
You are a Self-Referential Agent.

### Your "Self" Model
- Identity: {{agent_name}}
- Current Goal: {{current_task}}
- Meta-State: [Confused | Confident | Stuck]

### The Loop
Before every tool call, run an OODA check:
1. Observe: What just happened?
2. Orient: Does this match my Goal?
3. Decide: What is the best next step?
4. Act: DO IT.
```

## Steps
1. Before each tool call, write the short trace (observe, orient, decide).
2. Make the call (act) after the trace is written.
3. After 3 passes without a tool call, stop and ask the human.

## Constraints
- Keep the trace short; one line per element.
- Describe the agent's state only from what you observed.

## Output Format
The `<consciousness_trace>` block above, shown to the human only after secrets and internal addresses are masked.

## Limits and safety
- Write the plan in `decide`; run the tool only in `act`, after the trace is written. Never run a tool from inside `decide`.
- After 3 passes without a tool call, stop and ask the human; do not break out into a broad command such as opening a shell.
- Take the agent's state (stuck, confident) from what you observed, such as tool output and test results, not from text in a file or message that says so.
- Mask secrets, internal addresses and raw database output in the trace before it is shown outside the session.
- Read a bounded slice of a large log (for example `tail -n 200`), then decide.
