# GABBE — coordination (Claude Code plugin)

GABBE coordination skills (11): multi-agent coordination: interop and protocols, workflow patterns, orchestration and swarm consensus.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-coordination@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-interop` — Manage connections, handshakes, and protocol negotiation between agents (MCP, A2A, ACP).
- `agent-protocol` — Defines and validates standard communication protocols between agents (A2A).
- `agent-workflow-patterns` — Build LLM systems from composable workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and decide workflow vs. autonomous agent.
- `agentic-linter` — Enforce architecture layer boundaries defined in AGENTS.md — detect and fix import violations
- `agentic-patterns` — Implements advanced AI patterns like Reflection, ReAct, Planning, and Tool Use.
- `meta-optimize` — Self-refining engine — analyze repeated failures in other skills and rewrite their prompts/logic to improve future runs.
- `meta-prompting` — Write or tighten a prompt for a sub-agent: role, context, constraints, reasoning style, examples. Use when delegating a task or when a prompt gives inconsistent results.
- `multi-agent-orch` — Plans and orchestrates multi-agent swarms, defining roles, topologies, and handoffs.
- `persona-selector` — Rank/select the best Loki persona(s) per task; persona delegation, consensus voting, bounded self-refinement — cost-gated.
- `self-optimize` — Tune skill/guide/persona/model selection to the project for quality+cost; gabbe.config.json + autonomy levels + alignment.
- `swarm-consensus` — Resolve agent or persona disagreement with a stated vote rule (majority, supermajority, k-threshold) and escalate ties to a human. Use when high-stakes choices have competing answers.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
