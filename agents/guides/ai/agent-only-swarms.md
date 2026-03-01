---
description: Guide to executing Loki Mode, Swarm Management, and Agent Delegation purely via Agent Prompts without the GABBE CLI.
---

# Agent-Only Swarms & Multi-Agent Orchestration

The `gabbe` CLI tool offers robust, programmable programmatic control over `loki-mode` and multi-agent coordination by spinning up independent API threads and enforcing filesystem constraints.

However, **all GABBE swarm coordination protocols are defined in Markdown.** This means you can unleash the power of the 10-Phase SDLC or orchestrate a swarm of specialized Personas inside a pure chat environment (like Cursor, Copilot, or Claude Code) without installing the CLI.

There are two primary ways to operate Swarms in "Agent-Only" mode:
1. **In-Context Simulation**: The LLM adopts multiple personas sequentially within the same chat thread.
2. **True Subagent Delegation (A2A)**: You act as the "Router," taking instructions from the Master Orchestrator and spinning up true, parallel LLM instances (like Gemini 1.5 Pro or Claude 3.5 Sonnet) to do isolated work.

---

## 1. Unsupervised Loki Mode (10-Phase SDLC)

If you have a massive project and want the agent to meticulously follow the 10-Phase framework (from `S01` to `S10`), you can invoke `loki-mode` directly.

### The Agent Prompt
> "Activate `agents/skills/brain/loki-mode.skill.md`. Our goal is to [build a new payment gateway]. We are starting from Phase S01. Do not ask me for permission unless you hit a mandatory Human Approval Gate or a task requires True A2A Delegation."

### What the Agent Does Automatically
1. Read `AGENTS.md` and define the required Personas.
2. Draft the `PRD.md` acting as the `prod-pm` persona.
3. Pause and ask you, the human, to review and approve the PRD (Mandatory S01 Gate).

---

## 2. Supervised Loki Mode (Triggered by the Brain)

If you aren't sure if a project is big enough to require a swarm, you can let `brain-mode` decide.

### The Agent Prompt
> "Activate `agents/skills/brain/brain-mode.skill.md`. Evaluate my request to [refactor the authentication module]. If it is a massive project, initialize `loki-mode`."

---

## 3. Simulating Swarms vs. Spawning Subagents

When the Orchestrator reaches Phase S05 (Implementation), tasks are partitioned for specific worker Personas (e.g., `eng-qa`, `ops-security`). 

You can instruct your LLM on *how* to execute these.

### Tactic A: In-Context Simulation (Fast, Single-Threaded)
Use this for simple projects where context window limits are not a concern. The LLM simply role-plays.

> "Execute the next 3 tasks using **In-Context Simulation**. Act as the `eng-backend` persona to write the code, then immediately adopt the `eng-qa` persona in the next paragraph to test it."

### Tactic B: True Subagent Delegation A2A (For Massive Scale)
Use this when you need true isolation, zero context-pollution, or want to utilize different frontier models for different tasks (e.g., Cursor for coding, OpenAI o1 for Architecture review).

> "For the next task, use **True Subagent Delegation**. Do not write the code yourself. Instead, generate a `delegation-payload.md` file. Include the specific `persona` file to load, the exact task context, and the expected output format. I will copy-paste this file into a separate AI model and return the result to you here."

**Your Workflow:**
1. The Orchestrator generates `delegation-payload.md`.
2. You open a new browser tab for an advanced model (e.g., Gemini Advanced).
3. You paste the payload: *"You are now adopting the GABBE `eng-qa` persona based on the following payload..."*
4. The Subagent works in isolation and gives you the final test suite.
5. You paste the test suite back to the Orchestrator in Cursor: *"Here is the output from the `eng-qa` subagent. Proceed to S06."*

---

## 4. Ad-Hoc Swarm Debate (No SDLC)

You don't need the 10 phases to use Swarms. You can invoke a specific matrix of personas to debate a complex architecture decision.

### The Agent Prompt
> "Invoke `agents/skills/coordination/multi-agent-orch.skill.md`. I need to decide between PostgreSQL and MongoDB. Load the `prod-architect`, `eng-database`, and `ops-cost` personas. Facilitate a sequential debate simulating their perspectives. Synthesize their arguments into a final recommendation."
