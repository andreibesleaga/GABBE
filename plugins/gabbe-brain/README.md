# GABBE — brain (Claude Code plugin)

GABBE brain skills (16): Brain Mode internals: cognitive architectures, active inference, global workspace, working and episodic memory, self-improvement.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-brain@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.2.0. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `active-inference` — Frames an agent's predict, act, compare loop as surprise minimisation (conceptual, not a solver). Use when a tool result contradicts the agent's expectation and it must choose between probing and fixing.
- `brain-mode` — Adds a plan-and-review layer over the normal work loop. Picks the cheapest strategy that passes, watches a Loki run, and records one decision-log entry. Use when the human says "brain mode" or "activate brain" for a task that needs a chosen strategy and cost control.
- `cognitive-architectures` — Describes SOAR, ACT-R and LIDA patterns (propose, evaluate, select; activation-based retrieval; workspace broadcast) as ideas for agent design. Use when designing an agent's reasoning cycle or memory retrieval and you want a named pattern as a starting point.
- `cognitive-testing` — Tests cognitive and agentic loops by invariants, convergence, memory integrity and loop guards instead of exact output. Use when you must test an autonomous loop whose output varies, or check that its guards fire.
- `consciousness-loop` — Adds an explicit observe, orient, decide, act trace with a breakout after 3 idle spins. Use when an agent keeps reasoning without calling a tool, or when a decision trace is needed.
- `cost-benefit-router` — Chooses a local or remote model and a model tier for a task from complexity, privacy and context size. Use when asked to route a task, choose a model or cut cost, or when the task may involve sensitive data.
- `episodic-consolidation` — Turns a finished task's audit log into reusable rules and prunes scratch files. Use at the end of a long task to record lessons and to detect drift in the project's world model.
- `epistemology-knowledge` — Explains how to hold beliefs as hypotheses until verified, combine a knowledge graph with vector search, and tell probing actions from changing actions. Use when designing how an agent stores and updates what it knows.
- `global-workspace` — Runs a salience-filtered shared blackboard where sub-agents compete to broadcast findings. Use when several agents need one shared context, or their findings conflict.
- `learning-adaptation` — Turns successful outcomes into a few-shot example bank and reviewed rule changes with a way back. Use after a task to record what worked, or when a recurring failure should change behaviour.
- `loki-mode` — Orchestrates personas through the 14-phase lifecycle S00 to S13 with checkpoints, memory and six human gates. Use when the human says "loki mode", "activate loki" or "run the lifecycle" for a project too large for one context.
- `neuroscience-foundations` — Describes thalamic gating, basal-ganglia action selection and prompt-population selection as design analogies. Use when you want a named analogy for routing signals, choosing among candidate plans or evolving prompts.
- `self-improvement` — Proposes gated, reversible edits to the agent's own prompts or skills from successful runs only. Use only when a human asked the system to evolve its instructions.
- `sensory-motor` — Checks tool access, watches running commands and aborts them on a timeout. Use when a command may hang, a tool fails silently, or you need a state check before acting.
- `sequential-thinking` — Breaks a complex problem into verified steps and records assumptions. Use when a request is complex, has several unknowns, or needs a plan before action.
- `working-memory` — Moves task state into a scratchpad in small chunks and re-anchors the goal. Use when a task exceeds the context or variables from different modules get mixed up.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
