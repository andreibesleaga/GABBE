# GABBE — extras (Claude Code plugin)

GABBE extras skills (8): kit maintenance and research helpers: skill registry imports, update scan, state export and import, traceability matrix, agent analytics, empirical methods, emerging technology and knowledge connectors.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-extras@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.2.0. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-analytics` — Logs token use, task duration and retries per task to a metrics file and flags retry loops and cost spikes. Use when the human asks about token usage, cost or agent efficiency, or when a task keeps retrying.
- `emerging-tech` — Gives design guidance and a short plan for 6G edge placement, Matter IoT devices and vector search with RAG. Use when a design involves low-latency edge compute, smart-home devices, embeddings or semantic search.
- `empirical-methods` — Designs a measurement or experiment (metric, hypothesis, controls, sample size) and reports results with effect size and confidence interval. Use when comparing benchmarks, reading A/B results, choosing a metric or tracing a root cause.
- `knowledge-connect` — Connects the agent to documentation, project files and vector stores and sets up retrieval with a fallback chain. Use when the human wants to index project docs, set up a RAG pipeline, or query a knowledge base.
- `skills-registry` — Imports skills from external registries through validation gates and prepares kit skills for publishing. Use when the human wants to add a skill from a registry or share kit skills.
- `state-portability` — Exports the working state to STATE_HANDOFF.md and a tarball, and imports it in another agent. Use when switching coding agent or LLM, or moving the project to another machine.
- `system-lifecycle` — Keeps a traceability matrix from requirement ID to design, code and test, and checks the Definition of Done. Use when asked what a change affects, whether every requirement has a test, or whether a task is done.
- `update-scan` — Scans the kit, skill registries and the ecosystem for newer skills, tools, MCP servers or models and recommends or adopts them within cost and permission limits. Use at preflight, or when the human asks what is new or better.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
