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
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.2.0. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `a2ui-protocols` — Design the message schema and streaming events an agent uses to send UI to a frontend (JSON, WebSocket, SSE, HTMX). Use when an agent must stream components or UI updates to a browser.
- `actor-agent-frameworks` — Set up an agent or actor graph (LangGraph, Akka or custom) with state schema, checkpoints and failure recovery. Use when you build or change a multi-step agent graph or actor system that must survive restarts.
- `agent-communication` — Choose and wire the channel between agents - MCP, A2A, ACP, gossip or a broker (Kafka, RabbitMQ, MQTT), with a capability handshake. Use when two or more agents must exchange messages or delegate work across processes or vendors.
- `agent-ui` — Build a UI that shows what an agent thinks, calls and does - traces, tool calls, streamed markdown or JSON. Use when you add a tracing view, an approval screen or a front end for an agent.
- `autonomous-swarm-patterns` — Build a self-organising swarm of agents that coordinate through shared markers and simple local rules. Use when one agent cannot cover a decentralised problem and you want many agents with no central planner.
- `beyond-llms` — Combine an LLM with deterministic rules, genetic algorithms or an active-inference loop so hard constraints override model output. Use when a problem needs guaranteed rules, search or optimisation that a prompt alone cannot give.
- `context-engineering` — Plan what enters an agent's context window with Write, Select, Compress and Isolate - budget, retrieval, compaction, sub-agents, prompt caching. Use when a long task loses quality or cost grows with history.
- `llm-as-judge` — Score open-ended LLM or agent output with another LLM as evaluator - rubric, pairwise comparison, bias controls, calibration against human labels. Use when no reference answer exists and you need a repeatable score.
- `multi-agent-systems` — Design a multi-agent system - topology (hierarchical, network, swarm), role profiles, shared workspace and supervisor. Use when a task needs several agents with defined roles and one result.
- `rag-evaluation` — Evaluate a RAG pipeline without gold answers - faithfulness, answer relevance, context precision and recall over (query, context, answer) triples. Use when a RAG system gives fluent answers you cannot trust, or after a retrieval change.
- `reasoning-patterns` — Pick a test-time reasoning technique (chain-of-thought, self-consistency, tree-of-thoughts, least-to-most, step-back, reflexion) by problem shape, cost and latency. Use when one-shot answers are unreliable or reasoning cost needs a budget.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
