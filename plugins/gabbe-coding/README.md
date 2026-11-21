# GABBE — coding (Claude Code plugin)

GABBE coding skills (30): coding: language performance, testing strategies (browser TDD, property-based, metamorphic, chaos), evals, UI generation and diagram canvases.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-coding@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-trajectory-eval` — Score an agent's run by its tool calls and state transitions, not only its final answer: tool and parameter F1, in-order match, legal transitions, pass^k. Use when you evaluate how an agent reached an answer or need a reliability figure over repeated runs.
- `artisan-commands` — Run Laravel Artisan commands safely: check the project and environment, run the command, verify the result. Use when the user asks to scaffold a controller or model, run migrations or manage a Laravel app with php artisan.
- `browser-tdd` — Write Playwright tests that check a UI in a real browser (DOM, computed styles, scroll, screenshots) before the code. Use when a UI task is about layout, sticky or fixed elements, modals, animations or anything that only works when it renders correctly.
- `chaos-fault-injection` — Produce a fault-injection matrix: each fault (dropped connection, corrupt write, latency, bad response, resource exhaustion) with its expected recovery and an assertion. Use when you must show that a system recovers, rolls back or stops safely when a dependency fails.
- `ci-autofix` — Fix a failing CI run: read the log, find the first root cause (lint, types, test, build), apply a minimal change and verify it locally. Use when CI is red, a build is broken, or a lint, type or test job fails.
- `design-by-contract` — State preconditions, postconditions and invariants at module boundaries and make them runnable checks. Use at S03/S05 for level 1 code with logic, public module interfaces, or when a requirement says what must always hold.
- `eval-driven-development` — Build an offline eval suite for LLM or agent output: golden dataset, tiered checks, pass@k and pass^k, and a CI gate against a baseline. Use when output quality is probabilistic and unit tests cannot score it, or after a prompt change.
- `excalidraw` — Create Excalidraw diagrams through the MCP server: architecture views, flowcharts and system maps, with positions planned first. Use when the user asks for an Excalidraw or hand-drawn style diagram saved as a .excalidraw file.
- `file-processing` — Handle large files and uploads without exhausting memory: streaming, presigned uploads, malware scanning, background exports, file-type checks. Use when code reads or writes big files, accepts user uploads or exports large datasets.
- `formal-spec-lightweight` — Write a small design-level model (TLA+, Quint, Alloy or P) of concurrency, a protocol, a state machine, money flow or authorisation, check it exhaustively within bounds, and turn counterexamples into tests. Use at S02/S03 for assurance level 2.
- `fuzz-differential-testing` — Fuzz parsers and decoders with a coverage-guided fuzzer, compare an implementation with a reference by differential testing, and triage crashes into permanent regression tests. Use at S05/S06 for any code that reads untrusted or complex input, and for rewrites that must match an old implementation.
- `metamorphic-testing` — Write a suite of metamorphic relations (an input change plus the required output relationship) for systems with no reliable oracle, such as LLM and NLP output. Use when you cannot state the correct output but can state how outputs of related inputs must relate.
- `mobile-dev` — Build iOS, Android and React Native screens, navigation and device integrations with platform conventions and a checklist. Use when the user asks for a mobile app or screen, or reports an iOS or Android build or performance problem.
- `nodejs-expert` — Resolve deep Node.js, Fastify and advanced TypeScript problems: event loop, plugin encapsulation, type constraints. Use when a Node.js backend has a performance or architecture problem, a Fastify route needs review, or a TypeScript type error resists a normal fix.
- `output-validation` — Validate LLM output against a schema with bounded retries, and mask personal data before logs and external APIs. Use when model output feeds code, a tool or a database, or when personal data could reach a log or a third-party API.
- `performant-ai` — Cut token cost and latency in LLM systems: context pruning, prompt size, RAG chunking and re-ranking, model routing, caching. Use when an LLM feature is slow or expensive, or when its context window or retrieval quality is the limit.
- `performant-go` — Profile and speed up Go services: goroutine lifecycle, allocations, struct layout, pprof, GC settings, benchmarks. Use when a Go service is slow, uses too much memory, leaks goroutines or needs a benchmark.
- `performant-laravel` — Speed up Laravel apps: eager loading and indexes, queues, caching, Octane or FrankenPHP, measured with a load test. Use when a Laravel app has slow pages, N+1 queries or high load.
- `performant-nodejs` — Speed up Node.js services: profile first, then worker threads, streams with backpressure, ESM, structured logging and tracing. Use when a Node.js service is slow, blocks the event loop or uses too much memory.
- `performant-php` — Speed up modern PHP (8.4 and later): OPcache and JIT, worker-mode servers, N+1 fixes, static analysis, tests with Pest. Use when a PHP or Symfony service is slow, or when upgrading PHP versions and tooling.
- `performant-python` — Speed up Python services: async I/O, FastAPI and Pydantic v2, connection pooling, memory use, profiling with py-spy and load tests. Use when a Python service is slow, blocks the event loop or uses too much memory.
- `proof-core-verification` — Scope a small safety- or security-critical core, have the human review its specification, prove it with Dafny, Verus, Kani or Lean, and run the leak checklist. Use only at assurance level 3, after the human has decided to pay for a proof.
- `sketch-to-diagram` — Turn a hand-drawn sketch or whiteboard photo into an editable diagram (Excalidraw, Mermaid or Draw.io) after the human approves the recognised elements. Use when the user supplies an image of a diagram, wireframe or event-storming board.
- `spec-driven-development` — Run a spec-first workflow: executable spec, acceptance criteria, tasks, then code, with traceability from spec to test. Use when starting a feature or project and the spec should be written and reviewed before any code.
- `time-complexity` — Estimate the Big-O of functions, files or directories by static analysis with the time-complexity MCP server, and list hotspots. Use when the user asks about algorithm complexity, performance hotspots in code, or complexity before a review.
- `tldraw-canvas` — Create, edit and search tldraw canvases (.tldr files) for wireframes, architecture sketches and visual notes through the MCP server. Use when the user asks for a tldraw canvas, a UI wireframe or a visual scratchpad.
- `tool-construction` — Build a small script or MCP server for a one-off or recurring task, with one responsibility, least privilege and human review before it runs. Use when the user keeps repeating a manual step or asks for a new tool for the agent.
- `ui-gen` — Generate a user interface (React with Tailwind, HTMX fragments, a terminal UI or a Streamlit app) after choosing the paradigm that fits the stack. Use when the user asks for a dashboard, frontend, internal tool UI or CLI interface.
- `vibe-coding` — Turn a mood request (90s cyberpunk, Apple-style minimalism) into design tokens, CSS, motion and copy changes. Use when the user describes how a UI should feel rather than what it should do.
- `visual-design` — Design high-fidelity UI: tokens, colour palette, typography, spacing and interaction states, as Tailwind config or CSS variables. Use when the user asks to design or restyle a UI, create a palette or update a design system.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
