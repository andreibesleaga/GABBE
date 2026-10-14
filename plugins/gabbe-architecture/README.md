# GABBE — architecture (Claude Code plugin)

GABBE architecture skills (29): software architecture: patterns, C4 and diagrams, domain models, event-driven and microservice design, governance, migration and scalability.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-architecture@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `adaptive-architecture` — Design systems that evolve and work offline (Local-First, WASM, CRDTs).
- `api-standards` — Enforce REST/GraphQL API design and governance standards
- `arch-debt` — Identify architectural anti-patterns — coupling, circular dependencies, God objects — and propose concrete migration paths
- `arch-patterns` — Recommends and analyzes system architecture patterns (Microservices, EDA, Serverless, etc.) based on requirements.
- `architecture-governance` — Automated fitness functions (ArchUnit) to prevent architectural drift.
- `attribute-driven-design` — Drive architecture from quality-attribute scenarios using the iterative ADD 3.0 method, producing a reviewable design workbook.
- `blockchain-dlt` — Architect and audit Distributed Ledger/Blockchain systems and Smart Contracts
- `compatibility-design` — Manage breaking changes, migrations, and API evolution.
- `critical-systems-arch` — Design architecture for safety-critical and high-reliability systems
- `design-patterns` — Identifies, implements, and refactors code using standard Design Patterns (GoF + Modern).
- `diagramming` — Choose and create the right diagram type (UML, C4, ER, BPMN, domain) in standard notation; Mermaid-compatible output.
- `domain-model` — Create or review a domain model — bounded contexts, entities, value objects, aggregates, domain events, relationships.
- `enterprise-migration-scenario` — Plan and execute complex enterprise-scale legacy migrations
- `enterprise-patterns` — Implement robust Enterprise Architecture Patterns
- `error-handling-strategy` — Centralized error handling (RFC 7807), circuit breakers, and user-facing fallbacks.
- `event-driven-architecture` — Design and implement Event-Driven and Async Architectures
- `event-governance` — Schema Registry enforcement (Avro/JSON), CloudEvents standard, and Event Evolution rules.
- `fitness-functions` — Define objective, measurable tests for architectural characteristics and wire them into CI as automated, continuous architecture governance.
- `graphql-schema` — Schema design, federation, and resolution strategies.
- `legacy-modernization` — Analyze, document, and modernize legacy systems (COBOL, Mainframe, Fortran).
- `microservices` — Design and implement microservices architecture
- `middleware-design` — Designing robust middleware chains (Auth, Rate Limiting, Logging).
- `monolith` — Design and refactor Monolithic and Modular Monolithic architectures
- `realtime-comm` — WebSocket handling, Pub/Sub patterns, and persistent connections.
- `state-management` — Manage client-side state, side effects, and data flow.
- `system-qualities` — Define and enforce Quality Attributes (Non-Functional Requirements)
- `system-scalability` — Audit and architect scaling boundaries and bottlenecks
- `systems-architecture` — Generate comprehensive C4 models and System Architecture documents
- `visual-whiteboarding` — Use spatial-canvas MCP servers (Miro, Draw.io, Figma) to map architectures, user flows, and wireframes.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
