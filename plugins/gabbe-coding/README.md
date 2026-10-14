# GABBE — coding (Claude Code plugin)

GABBE coding skills (28): coding: language performance, testing strategies (browser TDD, property-based, metamorphic, chaos), evals, UI generation and diagram canvases.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-coding@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-trajectory-eval` — Evaluate an agent's trajectory — its sequence of tool calls and state transitions — not just its final answer.
- `artisan-commands` — Execute Laravel Artisan commands safely
- `browser-tdd` — Browser-based visual TDD using Playwright — verify UI produces correct visual output, not just syntactic correctness
- `chaos-fault-injection` — Deliberately inject faults — dropped connections, corrupted writes, latency, malformed responses, resource exhaustion — and assert the system's expected recovery (escalation, hardstop, rollback).
- `ci-autofix` — Autonomous CI/CD remediation — parse GitHub/GitLab failure logs, find the root cause (lint/type/test), generate and commit a fix.
- `eval-driven-development` — Build offline evaluation suites that score probabilistic LLM/agent quality, distinct from deterministic tests.
- `excalidraw` — Create and manage Excalidraw diagrams via MCP for architecture visualization.
- `file-processing` — Stream processing, large file uploads, and IO efficiency.
- `metamorphic-testing` — Test systems with no reliable oracle using metamorphic relations — equivalence-preserving input transforms whose outputs must agree, with concrete relations for LLM/NLP stability.
- `mobile-dev` — Mobile application development (iOS, Android, React Native)
- `nodejs-expert` — Deep expertise in Node.js internals, Fastify architecture, and advanced TypeScript
- `output-validation` — Make LLM and agent outputs safe and machine-reliable via schema validation and PII masking.
- `pbt-strategy` — Property-based testing with Python Hypothesis — find invariants, write @given strategies, and model stateful systems with RuleBasedStateMachine.
- `performant-ai` — Strategies for high-performance AI/LLM systems (Context Management, Prompt Engineering, RAG, Inference Tuning).
- `performant-go` — Strategies for high-performance Go systems (Goroutines, Channels, Pprof, Memory Alignment).
- `performant-laravel` — Strategies for high-performance, scalable Laravel systems (Octane, DB Optimization, Redis, Microservices).
- `performant-nodejs` — Strategies for high-performance, scalable Node.js systems (Worker Threads, ESM, Observability, Clean Architecture).
- `performant-php` — High-performance modern PHP — PHP 8.4/8.5, OPcache+JIT, FrankenPHP workers, Composer, Symfony/Laravel, PHPStan/Psalm, Pest.
- `performant-python` — Strategies for high-performance Python systems (FastAPI, Asyncio, UVloop, Memory Optimization).
- `sketch-to-diagram` — Convert hand-drawn sketches and photos into formal digital diagrams using image recognition + diagram generation.
- `spec-driven-development` — Spec-first workflow where an executable, testable specification is written before code and becomes the single source of truth that tests verify against, flowing spec → acceptance criteria → tasks → implementation.
- `testing-strategy` — Formulates a comprehensive testing strategy (Pyramid vs Trophy) and selects appropriate tools.
- `time-complexity` — Estimate Big-O time complexity of code via static analysis (tree-sitter MCP).
- `tldraw-canvas` — Create, manage, and search tldraw canvases for visual design, wireframing, and UI prototyping.
- `tool-construction` — Dynamically building simple MCP servers or Python scripts to solve unique problems.
- `ui-gen` — Generate User Interfaces (Web, CLI, Mobile) using GenUI, HTMX, or TUI patterns.
- `vibe-coding` — Translate aesthetic 'vibe' requests (e.g. 90s cyberpunk, Apple minimalism) into concrete CSS/animation/copy changes.
- `visual-design` — Create high-fidelity UI designs, color palettes, and design systems

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
