# Skills index (lite)
> Generated file. Do not edit. Regenerate: `python3 agents/scripts/build_skills_index_lite.py` (CI runs it with `--check`).
> One line per skill: name — when to use it — context cost (the heading is the category). The full index is `agents/skills/00-index.md`; read a skill's file in full before you use it.
Skills: 231

## ai
a2ui-protocols — Design the message schema and streaming events an agent uses to send UI to a… — medium
actor-agent-frameworks — Set up an agent or actor graph (LangGraph, Akka or custom) with state schema… — high
agent-communication — Choose and wire the channel between agents - MCP, A2A, ACP, gossip or a broker… — medium
agent-ui — Build a UI that shows what an agent thinks, calls and does - traces, tool… — low
autonomous-swarm-patterns — Build a self-organising swarm of agents that coordinate through shared markers… — high
beyond-llms — Combine an LLM with deterministic rules, genetic algorithms or an… — high
context-engineering — Plan what enters an agent's context window with Write, Select, Compress and… — medium
llm-as-judge — Score open-ended LLM or agent output with another LLM as evaluator - rubric… — medium
multi-agent-systems — Design a multi-agent system - topology (hierarchical, network, swarm), role… — high
rag-evaluation — Evaluate a RAG pipeline without gold answers - faithfulness, answer relevance… — medium
reasoning-patterns — Pick a test-time reasoning technique (chain-of-thought, self-consistency… — medium

## architecture
adaptive-architecture — Design offline-first and local-first systems — sync strategy (CRDT or… — medium
api-design — API contract (OpenAPI, GraphQL SDL or proto) written before code, with… — medium
api-standards — Review of OpenAPI or GraphQL schemas against naming, status code, versioning… — medium
arch-debt — Architecture debt report with coupling metrics, dependency cycles, layer… — high
arch-design — Architecture design from approved requirements — quality scenarios, style… — high
arch-patterns — Shortlist of one or two architecture patterns (modular monolith… — medium
arch-review — ATAM-lite review of an existing architecture — scenario verdicts, smells… — high
architecture-governance — Enforce layer and dependency rules as architecture tests in CI (ArchUnit… — low
attribute-driven-design — ADD 3.0 workbook that traces each structural decision to a quality scenario… — medium
blockchain-dlt — Architecture and security notes for blockchain and smart contract systems… — high
code-archaeology — Use to recover the structure and intent of code you did not write. Maps entry… — medium
compatibility-design — Plan for changing a system without breaking users — expand-contract database… — medium
critical-systems-arch — Architecture for safety-critical systems — hazard analysis, fault tolerance… — high
design-patterns — Match a design problem to a standard pattern (strategy, adapter, facade… — low
diagramming — Pick the right diagram type and draw it in Mermaid (or PlantUML) — C4… — low
domain-model — Domain model document — glossary, bounded contexts, aggregates, domain events… — medium
enterprise-migration-scenario — Phased plan for moving a large legacy system to a modern platform with… — high
enterprise-patterns — Choose and specify an enterprise resilience pattern (saga, circuit breaker… — medium
error-handling-strategy — Design of one error model for a service — RFC 9457 problem details, global… — low
event-driven-architecture — Event-driven design — events, producers and consumers, broker choice, schemas… — medium
event-governance — Rules for events as data contracts — CloudEvents envelope, schema registry… — low
existing-project-onboarding — Use at the first session in a codebase that already exists and has no GABBE… — medium
fitness-functions — Set of measurable architecture checks (dependency rules, complexity, latency… — medium
graphql-schema — Design of a GraphQL schema — nullability, DataLoader batching, cursor… — low
legacy-modernization — Plan to understand and modernise legacy code (COBOL, mainframe, Fortran)… — medium
microservices — Service boundaries, API contracts, data ownership and failure isolation for a… — high
middleware-design — Request pipeline design with a fixed order — request id, CORS, rate limit… — low
monolith — Module boundaries, dependency rules and architecture checks for a modular… — medium
realtime-comm — Design of real-time features — WebSocket, SSE or long polling choice, scaling… — low
state-management — Frontend state architecture — which data is server, UI, global or URL state… — low
system-qualities — Measurable quality requirements (SLIs and SLOs) mapped to architecture… — low
system-scalability — Scaling audit — bottlenecks, vertical or horizontal options, externalised… — medium
systems-architecture — C4 model (context, container, component) as Mermaid diagrams with an… — high
visual-whiteboarding — Drawing architecture or flows on a Miro, Draw.io or Figma board through their… — low

## brain
active-inference — Frames an agent's predict, act, compare loop as surprise minimisation… — medium
brain-mode — Adds a plan-and-review layer over the normal work loop. Picks the cheapest… — high
cognitive-architectures — Describes SOAR, ACT-R and LIDA patterns (propose, evaluate, select… — low
cognitive-testing — Tests cognitive and agentic loops by invariants, convergence, memory integrity… — medium
consciousness-loop — Adds an explicit observe, orient, decide, act trace with a breakout after 3… — high
cost-benefit-router — Chooses a local or remote model and a model tier for a task from complexity… — low
episodic-consolidation — Turns a finished task's audit log into reusable rules and prunes scratch… — high
epistemology-knowledge — Explains how to hold beliefs as hypotheses until verified, combine a knowledge… — low
global-workspace — Runs a salience-filtered shared blackboard where sub-agents compete to… — high
learning-adaptation — Turns successful outcomes into a few-shot example bank and reviewed rule… — high
loki-mode — Orchestrates personas through the 14-phase lifecycle S00 to S13 with… — high
neuroscience-foundations — Describes thalamic gating, basal-ganglia action selection and… — low
self-improvement — Proposes gated, reversible edits to the agent's own prompts or skills from… — high
sensory-motor — Checks tool access, watches running commands and aborts them on a timeout. Use… — medium
sequential-thinking — Breaks a complex problem into verified steps and records assumptions. Use when… — low
working-memory — Moves task state into a scratchpad in small chunks and re-anchors the goal… — low

## coding
agent-trajectory-eval — Score an agent's run by its tool calls and state transitions, not only its… — medium
artisan-commands — Run Laravel Artisan commands safely: check the project and environment, run… — low
assurance-ladder — Choose how strongly a component must be verified, from plain tests (level 0)… — medium
browser-tdd — Write Playwright tests that check a UI in a real browser (DOM, computed… — medium
chaos-fault-injection — Produce a fault-injection matrix: each fault (dropped connection, corrupt… — medium
characterization-tests — Use before changing code that has no tests or weak tests. Pins what the code… — medium
ci-autofix — Fix a failing CI run: read the log, find the first root cause (lint, types… — high
clean-coder — Review code for Clean Code smells and SOLID violations and suggest… — medium
code-review — Review a change for security, architecture, performance, quality and tests, in… — medium
debug — Find the root cause of a bug by reproducing it, writing a failing test… — medium
design-by-contract — State preconditions, postconditions and invariants at module boundaries and… — low
documentation — Write or update docstrings, API docs and the README so they match the current… — medium
eval-driven-development — Build an offline eval suite for LLM or agent output: golden dataset, tiered… — medium
excalidraw — Create Excalidraw diagrams through the MCP server: architecture views… — medium
file-processing — Handle large files and uploads without exhausting memory: streaming, presigned… — low
formal-spec-lightweight — Write a small design-level model (TLA+, Quint, Alloy or P) of concurrency, a… — high
fuzz-differential-testing — Fuzz parsers and decoders with a coverage-guided fuzzer, compare an… — medium
git-workflow — Make Conventional Commits, branches and pull requests with the quality gates… — low
incremental-feature — Use to add or change a feature in an existing system with the least risk. Find… — medium
metamorphic-testing — Write a suite of metamorphic relations (an input change plus the required… — medium
mobile-dev — Build iOS, Android and React Native screens, navigation and device… — medium
mutation-testing — Measure how well tests detect faults by mutating changed code, reading… — medium
nodejs-expert — Resolve deep Node.js, Fastify and advanced TypeScript problems: event loop… — low
output-validation — Validate LLM output against a schema with bounded retries, and mask personal… — medium
pbt-strategy — Write a property-based test plan: the invariants, the generators and, for… — medium
performant-ai — Cut token cost and latency in LLM systems: context pruning, prompt size, RAG… — medium
performant-go — Profile and speed up Go services: goroutine lifecycle, allocations, struct… — medium
performant-laravel — Speed up Laravel apps: eager loading and indexes, queues, caching, Octane or… — medium
performant-nodejs — Speed up Node.js services: profile first, then worker threads, streams with… — medium
performant-php — Speed up modern PHP (8.4 and later): OPcache and JIT, worker-mode servers, N+1… — medium
performant-python — Speed up Python services: async I/O, FastAPI and Pydantic v2, connection… — medium
proof-core-verification — Scope a small safety- or security-critical core, have the human review its… — high
refactor — Restructure code in small steps while a green test suite guards behaviour, and… — low
safe-refactoring — Use to change the structure of existing code that has no reliable safety net… — medium
secure-coding — Apply OWASP Proactive Controls while writing code: validation, output… — low
sketch-to-diagram — Turn a hand-drawn sketch or whiteboard photo into an editable diagram… — high
spec-driven-development — Run a spec-first workflow: executable spec, acceptance criteria, tasks, then… — medium
tdd-cycle — Implement a feature test-first: write a failing test, confirm it fails for the… — low
testing-strategy — Choose a testing strategy (pyramid, trophy, contract, property, mutation) and… — medium
time-complexity — Estimate the Big-O of functions, files or directories by static analysis with… — medium
tldraw-canvas — Create, edit and search tldraw canvases (.tldr files) for wireframes… — medium
tool-construction — Build a small script or MCP server for a one-off or recurring task, with one… — low
ui-gen — Generate a user interface (React with Tailwind, HTMX fragments, a terminal UI… — medium
verification-anti-cheating — Rules and reviewer checks that stop an implementing agent from gaming its own… — low
vibe-coding — Turn a mood request (90s cyberpunk, Apple-style minimalism) into design… — medium
visual-design — Design high-fidelity UI: tokens, colour palette, typography, spacing and… — medium

## coordination
agent-interop — Manage connections, handshakes, and protocol negotiation between agents (MCP… — medium
agent-protocol — Defines and validates standard communication protocols between agents (A2A). — low
agent-workflow-patterns — Build LLM systems from composable workflow patterns (prompt chaining, routing… — medium
agentic-linter — Enforce architecture layer boundaries defined in AGENTS.md — detect and fix… — medium
agentic-patterns — Implements advanced AI patterns like Reflection, ReAct, Planning, and Tool Use. — high
meta-optimize — Self-refining engine — analyze repeated failures in other skills and rewrite… — high
meta-prompting — Write or tighten a prompt for a sub-agent: role, context, constraints… — low
multi-agent-orch — Plans and orchestrates multi-agent swarms, defining roles, topologies, and… — medium
persona-selector — Rank/select the best Loki persona(s) per task; persona delegation, consensus… — medium
self-optimize — Tune skill/guide/persona/model selection to the project for quality+cost… — medium
swarm-consensus — Resolve agent or persona disagreement with a stated vote rule (majority… — low

## core
agent-analytics — Logs token use, task duration and retries per task to a metrics file and flags… — low
audit-trail — Appends one structured row per decision, phase change, approval or failure to… — low
clarify — Produces ranked clarifying questions with recommended defaults before acting… — low
emerging-tech — Gives design guidance and a short plan for 6G edge placement, Matter IoT… — medium
empirical-methods — Designs a measurement or experiment (metric, hypothesis, controls, sample… — medium
final-review — Runs an independent expert review of finished work and returns a verdict… — medium
gabbe-start — Entry point to GABBE. Gives the operating rules, how to choose the way of… — medium
integrity-check — Rates eight dimensions (requirements, architecture, implementation, tests… — high
knowledge-connect — Connects the agent to documentation, project files and vector stores and sets… — medium
knowledge-gap — Stops the agent before it uses an API, library, security mechanism or legal… — low
preflight — Mandated first action — auto-check, load the lite skill index + memory + cost… — medium
research — Finds answers in official docs, RFCs and standards, cross-checks two sources… — medium
retrospective — Runs a blameless retrospective that turns a timeline into a few owned, dated… — medium
sdlc-checkpoint — Verifies the gate criteria of an SDLC phase, writes the S<NN>_<name>.md… — low
self-heal — Runs a bounded diagnose, research, fix, verify loop with a 5-attempt cap and a… — medium
session-resume — Loads the memory files in order and produces a resume report so a new session… — medium
skills-registry — Imports skills from external registries through validation gates and prepares… — medium
state-portability — Exports the working state to STATE_HANDOFF.md and a tarball, and imports it in… — low
state-preserve — Keeps RESUME_POINTER.md and a snapshot current after each step so a cutoff… — low
system-lifecycle — Keeps a traceability matrix from requirement ID to design, code and test, and… — medium
update-scan — Scans the kit, skill registries and the ecosystem for newer skills, tools, MCP… — medium

## data
data-engineering — Pipeline and warehouse design — ELT, orchestration, dbt models, idempotent… — medium
data-governance — Data classification, lineage, integrity and retention rules with a deletion… — low
db-migration — Schema change workflow — forward and rollback migration, compatibility check… — medium
semantic-web — Ontology and RDF design with a mapping from existing data and SPARQL access… — medium
sql-optimization — Query tuning plan — reading EXPLAIN ANALYZE, index design, keyset pagination… — low

## industry
engineering-standards — Compliance review against ISO/IEC/IEEE 42010 and 12207, SWEBOK and the ACM… — medium
global-standards — Audit against UN SDG, ITU-T and open source (OSI, OpenSSF) requirements… — medium
healthcare-fhir — FHIR resource mapping, profiles and REST interactions for clinical data… — high
industrial-iot — Edge-to-cloud design for industrial telemetry with Purdue levels, OPC UA, MQTT… — medium
telecom-networks — Telecom API and architecture map using TM Forum ODA and Open APIs, GSMA CAMARA… — high

## ops
caching-strategy — Choose a cache pattern (cache-aside, read-through, write-through… — low
capacity-planning — Estimate how many instances, how much memory, IO and connections a service… — low
cloud-deploy — Configure and deploy an app to Vercel, Railway or AWS (SST) with config files… — medium
configuration-management — Write a software configuration management plan - branching model, baselines… — medium
cost-optimization — Find cloud spend that can be cut (idle compute, unused storage, network… — medium
decommission-sunset — Plan the retirement of a service or product - deprecation timeline, data… — medium
dependency-lifecycle — Set the policy for keeping dependencies current - patch, minor and major… — medium
dependency-upgrade — Use to upgrade one dependency in an existing project, safely. Inventory, read… — medium
deployment — Check a release before and after it ships - pipeline health, container and IaC… — medium
dev-environments — Set up a team-wide development environment with DevContainers, DevSpace or… — medium
dev-workflow — Handle git and GitHub tasks with the gh CLI and organise documentation with… — low
docker-dev — Set up local development with Docker - Compose with watch mode, DevContainers… — medium
enterprise-integration — Design integrations between a modern app and ERP, CRM or legacy systems… — medium
feature-flag-management — Plan a feature flag from dark launch to removal - flag type, safe default… — medium
incident-response — Run a production incident as incident commander - coordinate, communicate… — high
infra-devops — Write infrastructure as code (Terraform, OpenTofu), Kubernetes manifests and… — medium
k8s-dev — Set up development against a remote Kubernetes cluster with Telepresence… — medium
memory-optimization — Keep an agent's context small and cheap - rolling summaries, entity… — low
observability-stack-setup — Plan OpenTelemetry traces, metrics and logs, GenAI span attributes, SLIs and… — medium
performance-audit — Find bottlenecks by measurement - load tests, CPU and memory profiles, Web… — high
performance-optimization — Choose and apply speed and scale fixes after profiling - caching, read… — medium
production-health — Check the operational health of an agentic system in production - loop and… — medium
production-verifier — Verify a live deploy with read-only smoke checks, a 10% canary on error rate… — low
queue-management — Set rules for message queues - dead-letter queues, idempotent consumers… — low
release-management — Prepare a release - group commits by Conventional Commits type, choose the… — low
release-validation — Run the go or no-go check before production - freeze, traceability audit, full… — low
reliability-sre — Apply SRE practice - SLIs and SLOs, error budgets and freeze policy, golden… — medium
runbook-authoring — Write an operational runbook for one alert - symptom, impact, read-only… — medium
system-benchmark — Design and run load, stress, soak and resilience tests on a staging system… — medium
tech-debt — Find technical debt (markers, complexity, duplication, coverage gaps… — medium
troubleshooting-guide — Diagnose a system failure step by step - gather facts, list and rule out… — high

## product
accessibility — WCAG 2.2 compliance audit — keyboard navigation, screen reader testing, ARIA… — medium
adr-writer — Generate Architecture Decision Records for significant technical decisions — low
business-case — Generate comprehensive business cases, ROI analysis, and strategic… — medium
change-management — Plan and drive organizational change through ADKAR, stakeholder comms cadence… — medium
decompose — Decompose specs/plans into atomic, testable tasks — enforces the 15-Minute… — medium
design-thinking — Apply the Design Thinking process (Empathize, Define, Ideate, Prototype, Test)… — medium
estimation-sizing — Size a backlog with reference-class forecasting, probabilistic ranges, and… — medium
financial-governance — Govern product spend with budget tracking, cost showback, unit economics, and… — medium
green-software — Review a system for carbon and energy efficiency: architecture, region… — low
ideation-facilitation — Facilitate divergent and convergent ideation to turn a framed problem into a… — medium
market-analysis — Produce a competitor comparison matrix, SWOT, differentiation options and… — low
opportunity-assessment — Assess a product opportunity with Wardley mapping, market sizing, a North-Star… — medium
product-analytics — Design event taxonomy, funnels and retention, rigorous A/B experiments, plus… — medium
professional-practice — Apply professional, ethical, and teamwork standards to software work using the… — medium
req-elicitation — Structured requirements elicitation — derive complete, verifiable requirements… — medium
req-review — Review requirements docs for quality/completeness/consistency (IEEE 29148, ISO… — medium
spec-analyze — Check consistency and alignment between spec.md, plan.md, and project/TASKS.md… — low
spec-writer — Generate Product Requirements Document with EARS syntax and structured… — medium
stakeholder-management — Build a power/interest grid, a RACI matrix and a communication plan for the… — low
sustainability-checks — Evaluate software architecture for ESG and sustainability impact — medium
systems-thinking — Analyze complex systems, feedback loops, and leverage points. Avoid linear… — medium
user-research-synthesis — Synthesize raw user-research data into personas, a journey map, and… — medium
user-story-mapping — Produce a user story map (activities, tasks, release slices, walking skeleton)… — low
visual-specs — Process visual inputs (scans, sketches, diagrams) into structured product… — high

## security
access-control — Design roles and permissions with least privilege and review authorisation… — low
agent-sandboxing — Intrinsic least-privilege isolation for agents touching a local OS, shell, or… — medium
agent-tool-review — Review which tools, permissions and data an AI agent in the software has, and… — medium
ai-ethics-compliance — Check an AI feature against EU AI Act and GDPR duties, test for bias and proxy… — low
ai-red-teaming — Proactively attack your own AI and agent system to find failures before… — medium
ai-safety-guardrails — Add input, output, retrieval and execution rails around an LLM feature: PII… — low
api-security — Audit and harden REST or GraphQL endpoints against broken object-level… — medium
backup-recovery — Set recovery objectives (RPO, RTO), choose a backup method and run a restore… — low
compliance-review — Regulatory compliance check for SOC2, PCI-DSS, GDPR, HIPAA — checklists, audit… — high
cryptography-standards — Choose and check cryptographic algorithms, password hashing and TLS settings… — low
dependency-security — Scan dependencies for known vulnerabilities, pin versions, produce an SBOM and… — low
hazard-analysis — Run FMEA and STPA on a safety-relevant design and fill the hazard log. Use… — low
legal-review — Check for license compliance, PII, and IP risks — medium
log-analysis — Read structured logs to find a cause: scope the time range, group by message… — low
network-security — Design and review network segmentation, firewall rules, TLS and egress… — low
privacy-audit — PII detection, data flow mapping, GDPR/CCPA/HIPAA compliance verification — medium
privacy-data-protection — Map personal data, minimise it, protect it, and design deletion and export for… — medium
prompt-injection-defense — Defend agentic systems against direct and indirect prompt injection using… — medium
reliability-engineering — Design failover, redundancy and stability patterns, and compute availability… — low
safety-scan — Active security enforcement — scan for vulnerabilities (SAST), secrets… — medium
secrets-management — Handle API keys and credentials safely: storage levels, runtime injection… — low
secure-architecture — Design defence in depth: trust zones, least-privilege access policy and… — high
security-audit — OWASP Top 10 security audit, SAST/DAST/SCA scanning, secrets detection, and… — high
security-baseline — Sets what every project built with the kit does for security, phase by phase… — medium
security-requirements — Turn a feature list into security and privacy requirements and abuse cases… — low
threat-model — STRIDE threat modeling before implementing security-sensitive features — medium
traceability-audit — Check that every requirement ID has a test and code, and flag code with no… — low
