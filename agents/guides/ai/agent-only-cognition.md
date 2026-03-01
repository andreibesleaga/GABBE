---
description: Guide to executing Brain Mode, Evaluation, and Self-Healing purely via Agent Prompts (No CLI)
---

# Agent-Only Cognitive Architecture

While the `gabbe` CLI tool offers robust, programmable programmatic control over Brain Mode, Structural Routing, and Genetic Evolution, **the core intelligence of the GABBE framework lives inside the `.skill.md` files.**

Because these skills are simply highly-structured markdown logic, you can natively invoke the entire GABBE Meta-Cognitive architecture purely via natural language in Cursor, Copilot Chat, or Claude Code **with 0 dependencies or CLI scripts.**

This guide explains how to manually trigger:
1. Active Inference (`brain-mode`)
2. Genetic Evolution (`meta-optimize`)
3. Autonomous Recovery (`self-heal`)

---

## 1. Manual Brain Mode (Active Inference)

If you have a massive feature to build and want the agent to use "System 2" Free Energy logic (thinking before typing), you can explicitly ask it to load the `brain-mode` skill.

### The Agent Prompt
> "Activate Brain Mode for this session by reading `agents/skills/brain/brain-mode.skill.md`. Your goal is to [build X feature]. Follow the Observe -> Orient -> Decide -> Act loop in that document before you write any code."

### What the Agent Does Automatically
Because `brain-mode.skill.md` contains strict procedural logic, the LLM will:
1. Check context files like `AGENTS.md` and `CONTINUITY.md`.
2. Generate an internal "Prediction" of what will happen.
3. Use a secondary skill (`cost-benefit-router` or `loki-mode`) to delegate tasks.

---

## 2. Manual Genetic Evolution (EPO)

If your agent is consistently failing at a specific task (e.g., repeatedly generating outdated React components), you don't need the CLI to fix it. You can order the agent to "evolve" its own rulebook.

### The Agent Prompt
> "We continually fail when writing React hooks. Invoke the `meta-optimize` skill. Read the last 5 chat messages, identify why your previous attempts failed, and directly edit `agents/skills/coding/react-components.skill.md` to add new constraints preventing this failure in the future. Log the change to `meta-evolution.log`."

### What the Agent Does Automatically
1. Retrospects the immediate chat failure.
2. Directly reads and modifies the specified `.skill.md` file on the file system.
3. Appends a new strict negative constraint (e.g., "- NEVER use `useEffect` for data fetching").
4. The next prompt in that repository will natively inherit the new rule.

---

## 3. Manual Self-Healing Loop

Agents often fail silently or give up when a test breaks. You can manually force them into the "Self-Heal" loop, trapping them in a diagnostic trace until the problem is verified as fixed by the console.

### The Agent Prompt
> "The build is failing. Invoke `agents/skills/core/self-heal.skill.md`. Do not ask me for permission between steps. Diagnose the error, hypothesize a fix, write the code, and run the tests. If it fails again, loop back to step 1. You have a maximum of 5 attempts before you must escalate to me."

### What the Agent Does Automatically
1. It reads the strict "1. Diagnose -> 2. Classify -> 3. Research -> 4. Fix -> 5. Verify" sequence.
2. It executes internal shell commands (e.g. `npm run build` or `pytest`).
3. If it fails, it prevents hallucination by writing down Attempt 1 strategies in `CONTINUITY.md` and trying a new route for Attempt 2.

---

## 4. Manual Cost-Benefit Routing

If you are using a local LLM or a cheaper model on Copilot and encounter a hyper-complex visual diagram or massive refactor, you can prompt the agent to "route" the task context to you, the human, to paste into a frontier model (like Claude 3.5 Sonnet or OpenAI o1).

### The Agent Prompt
> "Evaluate my request to [refactor the legacy COBOL module] using `cost-benefit-router.skill.md`. Provide a Complexity Score. If the score is > 50, do not attempt to solve it. Instead, generate a `REMOTE_PAYLOAD.md` containing exactly the context I need to copy-paste into an external AI interface."

## The "Pure Markdown AI" Philosophy

GABBE's core principle is that **System Logic == Markdown**. 

By treating specialized `.skill.md` files as executable functions, you gain Enterprise-grade reliability out of simple chat boxes. You are effectively using English as the compiler for an autonomous development lifecycle.
