# GABBE — architecture (Claude Code plugin)

GABBE architecture skills (30): software architecture: patterns, C4 and diagrams, domain models, event-driven and microservice design, governance, migration and scalability.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-architecture@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.1.4. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `adaptive-architecture` — Design offline-first and local-first systems — sync strategy (CRDT or last-write-wins), WASM plugin boundaries, edge versus cloud AI split. Use when an app must work offline, sync between devices, or run plugins or models on the user's device.
- `api-standards` — Review of OpenAPI or GraphQL schemas against naming, status code, versioning, pagination and error standards, with an updated spec. Use when API conventions must be checked across services or API governance rules set.
- `arch-debt` — Architecture debt report with coupling metrics, dependency cycles, layer violations and a phased migration plan. Use when modules depend on each other in circles, one class does everything, or structure blocks change.
- `arch-patterns` — Shortlist of one or two architecture patterns (modular monolith, microservices, event-driven, serverless, CQRS) with pros and cons for the project. Use when someone asks which architecture style fits the requirements.
- `arch-review` — ATAM-lite review of an existing architecture — scenario verdicts, smells, sensitivity and tradeoff points, fitness functions and prioritised recommendations. Use when you must judge whether an architecture still fits its requirements before a change, growth or a commitment.
- `architecture-governance` — Enforce layer and dependency rules as architecture tests in CI (ArchUnit, dependency-cruiser, Deptrac). Use when a layering rule keeps being broken or a pipeline needs an architecture gate.
- `attribute-driven-design` — ADD 3.0 workbook that traces each structural decision to a quality scenario, one element per round. Use when architecture must be derived step by step from drivers and each choice must be explainable.
- `blockchain-dlt` — Architecture and security notes for blockchain and smart contract systems — network choice, contract design, key handling, oracles. Use when a design involves a ledger, Solidity code or a web3 integration with an enterprise system.
- `compatibility-design` — Plan for changing a system without breaking users — expand-contract database migrations, API versioning, deprecation notices, feature flags. Use when a change would break clients or needs zero downtime.
- `critical-systems-arch` — Architecture for safety-critical systems — hazard analysis, fault tolerance, fail-safe states and a safety case outline. Use when failure could harm people or assets (medical, automotive, aerospace) and the design must follow DO-178C or IEC 62304.
- `design-patterns` — Match a design problem to a standard pattern (strategy, adapter, facade, observer, circuit breaker) and refactor to it. Use when code has long if/else chains, tangled integrations or repeated construction logic.
- `diagramming` — Pick the right diagram type and draw it in Mermaid (or PlantUML) — C4, sequence, state, ER, flowchart, data flow, context map. Use when the human asks for a diagram or when structure or flow must be shown.
- `domain-model` — Domain model document — glossary, bounded contexts, aggregates, domain events and a context map, in business language. Use when starting a product, reviewing a model against the domain, or finding where to split a monolith.
- `enterprise-migration-scenario` — Phased plan for moving a large legacy system to a modern platform with strangler fig, anti-corruption layer or change data capture, parallel runs and rollback. Use when a mainframe or on-premises system must migrate without dropping traffic or data.
- `enterprise-patterns` — Choose and specify an enterprise resilience pattern (saga, circuit breaker, BFF, API gateway) with retries, timeouts, fallbacks and failure tests. Use when a distributed call chain needs a transaction or fault-isolation design.
- `error-handling-strategy` — Design of one error model for a service — RFC 9457 problem details, global handler, retries with jitter, circuit breakers and fallbacks. Use when error responses are inconsistent or one dependency takes the service down.
- `event-driven-architecture` — Event-driven design — events, producers and consumers, broker choice, schemas and idempotent consumers. Use when services should communicate through events or queues instead of direct calls.
- `event-governance` — Rules for events as data contracts — CloudEvents envelope, schema registry checks, compatibility rules and AsyncAPI documentation. Use when event schemas change or several teams consume the same topics.
- `fitness-functions` — Set of measurable architecture checks (dependency rules, complexity, latency budgets) with thresholds, tools and CI wiring. Use when architectural properties should be tested automatically instead of reviewed by hand.
- `graphql-schema` — Design of a GraphQL schema — nullability, DataLoader batching, cursor pagination, depth and cost limits, federation. Use when writing or reviewing a GraphQL API or fixing N+1 resolvers.
- `legacy-modernization` — Plan to understand and modernise legacy code (COBOL, mainframe, Fortran) — analysis, API wrapper, strangler plan and characterisation tests. Use when old code with little documentation must be explained, wrapped or replaced step by step.
- `microservices` — Service boundaries, API contracts, data ownership and failure isolation for a microservices design. Use when splitting a monolith or designing a distributed system with several deployable services.
- `middleware-design` — Request pipeline design with a fixed order — request id, CORS, rate limit, authentication, authorization, parsing, validation, error handler. Use when adding or reviewing middleware for a web API.
- `monolith` — Module boundaries, dependency rules and architecture checks for a modular monolith. Use when building a monolith that must stay modular, or when module boundaries in an existing one are being violated.
- `realtime-comm` — Design of real-time features — WebSocket, SSE or long polling choice, scaling with Redis pub/sub, heartbeats, authentication and limits. Use when adding chat, live updates or any persistent connection.
- `state-management` — Frontend state architecture — which data is server, UI, global or URL state, library choice and state machines. Use when a web app has prop drilling, duplicated state or an unclear data flow.
- `system-qualities` — Measurable quality requirements (SLIs and SLOs) mapped to architecture decisions. Use when requirements say "fast" or "reliable" without numbers, or when SLAs must be set.
- `system-scalability` — Scaling audit — bottlenecks, vertical or horizontal options, externalised state, database scaling and a cost note. Use when load is expected to grow or the system is slow under load.
- `systems-architecture` — C4 model (context, container, component) as Mermaid diagrams with an architecture document. Use when a system's structure must be documented or its diagrams are missing or stale.
- `visual-whiteboarding` — Drawing architecture or flows on a Miro, Draw.io or Figma board through their MCP tools, with a plan first and a re-read afterwards. Use when the human asks for a board or canvas, or for design-to-code from Figma.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
