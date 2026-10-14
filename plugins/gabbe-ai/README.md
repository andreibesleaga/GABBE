# GABBE — ai (Claude Code plugin)

GABBE ai skills (11): AI and agent engineering: multi-agent systems, agent UIs and protocols, context engineering, RAG evaluation, LLM-as-judge and reasoning patterns.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-ai@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `a2ui-protocols` — Design and enforce Agent-to-UI communication protocols
- `actor-agent-frameworks` — Implement and manage Actor and Agent Frameworks (e.g. LangGraph)
- `agent-communication` — Establish Agent-to-Agent (A2A) communication channels and topologies
- `agent-ui` — Build specialized user interfaces for interacting with Agents
- `autonomous-swarm-patterns` — Implement self-organizing autonomous swarm architectures
- `beyond-llms` — Implement advanced neuro-symbolic and genetic algorithm techniques
- `context-engineering` — Engineer what enters the model's context window for reliability and cost using Write, Select, Compress, and Isolate.
- `llm-as-judge` — Score open-ended LLM/agent outputs with another LLM as evaluator while controlling for known judge biases.
- `multi-agent-systems` — Orchestrate Multi-Agent System (MAS) architectures
- `rag-evaluation` — Evaluate retrieval-augmented-generation pipelines with reference-free metrics to detect silent retrieval and grounding failures.
- `reasoning-patterns` — Select and apply test-time reasoning techniques (chain-of-thought, self-consistency, tree-of-thoughts, least-to-most, step-back, ReAct, reflexion) by cost, latency, and problem shape.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
