# GABBE — coordination (Claude Code plugin)

GABBE coordination skills (7): multi-agent coordination: interop and protocols, workflow patterns, orchestration and swarm consensus.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-coordination@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.3. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-interop` — Manage connections, handshakes, and protocol negotiation between agents (MCP, A2A, ACP).
- `agent-protocol` — Defines and validates standard communication protocols between agents (A2A).
- `agent-workflow-patterns` — Build LLM systems from composable workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and decide workflow vs. autonomous agent.
- `agentic-patterns` — Implements advanced AI patterns like Reflection, ReAct, Planning, and Tool Use.
- `meta-optimize` — Self-refining engine — analyze repeated failures in other skills and rewrite their prompts/logic to improve future runs.
- `multi-agent-orch` — Plans and orchestrates multi-agent swarms, defining roles, topologies, and handoffs.
- `swarm-consensus` — Implement voting mechanisms (majority, weighted) to resolve inter-agent conflicts.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
