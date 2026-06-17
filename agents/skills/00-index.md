# Skills Registry — 00-index.md

> Complete catalog of all available skills.
> Skills = agent capability packages. Invoke by mentioning trigger keywords.
> Context cost: low (< 2k tokens) | medium (2-8k) | high (> 8k)

---

## Installation

### Method 1: This Kit (built-in — no install needed)
All 180 skills in this directory are ready to use immediately.
Run `setup-context.sh` to wire them to your AI tool's skill directory.

### Method 2: Skill Marketplaces & Registries
```bash
# Vercel Skills CLI (recommended for JS/TS projects)
npx skills install tdd-cycle
npx skills install code-review

# namnam-skills (300+ multi-platform skills)
npm install -g namnam-skills
namnam install --platform claude-code
```

### Method 3: Community Collections
- **SkillsMP** (skillsmp.com) — AI-evaluated skills marketplace
- **SkillHub** (skillhub.club) — 7,000+ skills for Claude, Codex, Gemini
- `karanb192/awesome-claude-skills` — 50+ verified skills (TDD, debug, git, docs)
- `VoltAgent/awesome-agent-skills` — 300+ skills for Codex/Antigravity/Gemini/Cursor
- `hesreallyhim/awesome-claude-code` — Skills, hooks, slash-commands
- `anthropics/skills` — Official Anthropic skills repository
- `vercel-labs/agent-skills` — Vercel's official collection (Next.js, deployment)

### Global vs Workspace Scope
```bash
# Workspace scope (this project only):
#   .claude/skills/ -> agents/skills/*/*.skill.md  (done by setup-context.sh)

# Global scope (all projects on this machine):
ln -sf /path/to/agents/skills/*/*.skill.md ~/.claude/skills/
# For Gemini/Antigravity:
ln -sf /path/to/agents/skills/*/*.skill.md ~/.agent/skills/
```

---

> **Total Skills**: 180
> *Registry auto-updated by init.py logic*

> **This index is the canonical skill catalog.** Native skill menus (e.g. Claude
> Code) cap how many skills they show by token budget, so they may not list all
> 180 — always consult THIS file to discover any skill, then invoke it by trigger
> or by reading its file. For a clean native menu, emit only the curated core set
> with `compile_skills.py --native-subset core` (37 skills flagged `core: true`);
> the full catalog stays here.

## Skills Registry

### 1. Coding & Development (`coding/`)
| Skill | File | Triggers | Context Cost | Purpose |
|---|---|---|---|---|
| Code Review | `coding/code-review.skill.md` | review, PR, audit | medium | Security, perf, style check |
| TDD Cycle | `coding/tdd-cycle.skill.md` | test, TDD, red-green | medium | Red-Green-Refactor loop |
| Browser TDD | `coding/browser-tdd.skill.md` | visual test, browser | medium | Playwright visual verification |
| Refactor | `coding/refactor.skill.md` | refactor, restructure | medium | Safe code restructuring |
| Debug | `coding/debug.skill.md` | fix, debug, bug | medium | Root Cause Analysis (RCA) |
| Git Workflow | `coding/git-workflow.skill.md` | commit, PR, branch | low | Conventional commits |
| Documentation | `coding/documentation.skill.md` | docs, readme | medium | Generate documentation |
| Clean Coder | `coding/clean-coder.skill.md` | clean code, refactor | low | Apply SOLID/DRY principles |
| Mobile Dev | `coding/mobile-dev.skill.md` | mobile, ios, android | medium | RN/Swift/Kotlin dev |
| Visual Design | `coding/visual-design.skill.md` | design, ui, tokens | medium | High-fidelity UI design |
| Vibe Coding | `coding/vibe-coding.skill.md` | vibe, aesthetic | medium | Creative frontend coding |
| CI Autofix | `coding/ci-autofix.skill.md` | ci fix, autofix | medium | Auto-fix CI failures |
| Secure Coding | `coding/secure-coding.skill.md` | secure code, input | medium | Shift-left security |
| Tool Construction | `coding/tool-construction.skill.md` | build tool, mcp | medium | Build new tools |
| UI Gen | `coding/ui-gen.skill.md` | ui, dashboard, cli | medium | Generate React/HTMX UIs |
| File Processing | `coding/file-processing.skill.md` | stream, large file | medium | Efficient file IO |
| Testing Strategy | `coding/testing-strategy.skill.md` | test strategy, pyramid | medium | Testing Pyramid Strategy |
| Node.js Expert | `coding/nodejs-expert.skill.md` | node internals, fastify, typescript | low | Node.js internals & Fastify |
| Artisan Commands | `coding/artisan-commands.skill.md` | artisan, laravel | low | Execute Laravel commands |
| Performant Node.js | `coding/performant-nodejs.skill.md` | nodejs, performance | medium | High-performance Node.js systems |
| Performant Laravel | `coding/performant-laravel.skill.md` | laravel, performance | medium | High-performance Laravel systems |
| Performant Python | `coding/performant-python.skill.md` | python, performance | medium | High-performance Python systems |
| Performant Go | `coding/performant-go.skill.md` | go, performance | medium | High-performance Go systems |
| Performant PHP | `coding/performant-php.skill.md` | php, composer, symfony, laravel | medium | Modern PHP ecosystem performance |
| Performant AI | `coding/performant-ai.skill.md` | ai, llm, performance | medium | High-performance AI/LLM systems |
| Time Complexity | `coding/time-complexity.skill.md` | complexity, big-o, hotspot | medium | Big-O static analysis via MCP |
| Excalidraw | `coding/excalidraw.skill.md` | excalidraw, whiteboard, visual | medium | Excalidraw diagram creation via MCP |
| Sketch-to-Diagram | `coding/sketch-to-diagram.skill.md` | sketch, hand-drawn, recognize | high | Hand-drawn sketch → formal diagram |
| tldraw Canvas | `coding/tldraw-canvas.skill.md` | tldraw, canvas, wireframe, UI sketch | medium | Visual canvas for wireframing and design |
| Eval-Driven Dev | `coding/eval-driven-development.skill.md` | eval suite, golden dataset, prompt regression, pass@k | medium | Score probabilistic LLM/agent quality |
| Agent Trajectory Eval | `coding/agent-trajectory-eval.skill.md` | trajectory eval, tool-use eval, tau-bench, swe-bench | medium | Evaluate tool-call trajectories |
| Output Validation | `coding/output-validation.skill.md` | schema validation, structured output, pii masking | medium | Validate + mask LLM output |
| Property-Based Testing | `coding/pbt-strategy.skill.md` | property test, hypothesis, invariant, stateful | medium | PBT invariants via Hypothesis |
| Metamorphic Testing | `coding/metamorphic-testing.skill.md` | metamorphic, paraphrase invariance, oracle problem | medium | Metamorphic relations for LLM/NLP |
| Chaos & Fault Injection | `coding/chaos-fault-injection.skill.md` | chaos, fault injection, resilience, fallback | medium | Fault recipes to expected recovery |
| Spec-Driven Development | `coding/spec-driven-development.skill.md` | spec-first, spec kit, executable spec | medium | Spec-first workflow S01 to S04 |

### 2. Architecture & Design (`architecture/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Arch Design | `architecture/arch-design.skill.md` | design architecture | Create new architectures |
| Arch Review | `architecture/arch-review.skill.md` | review architecture | ATAM audit |
| Arch Patterns | `architecture/arch-patterns.skill.md` | microservices, mono | Select patterns |
| Design Patterns | `architecture/design-patterns.skill.md` | factory, strategy | GoF patterns |
| Diagramming | `architecture/diagramming.skill.md` | diagram, sequence | Mermaid diagrams |
| Domain Model | `architecture/domain-model.skill.md` | domain model, ddd | Context mapping |
| Adaptive Arch | `architecture/adaptive-architecture.skill.md` | local-first, crdt | Resilient systems |
| Compatibility | `architecture/compatibility-design.skill.md` | backward compat | Breaking changes check |
| Arch Gov | `architecture/architecture-governance.skill.md` | archunit, rules | Arch constraints |
| Error Handling | `architecture/error-handling-strategy.skill.md` | error, exception | RFC 7807 handling |
| Event Gov | `architecture/event-governance.skill.md` | schema, avro | Event registry |
| GraphQL Schema | `architecture/graphql-schema.skill.md` | graphql, typedefs | Schema design |
| Middleware | `architecture/middleware-design.skill.md` | middleware, tube | Pipeline design |
| State Mgmt | `architecture/state-management.skill.md` | redux, state | State architecture |
| Realtime | `architecture/realtime-comm.skill.md` | websocket, sse | Real-time patterns |
| Arch Debt | `architecture/arch-debt.skill.md` | coupling, cycles | Arch debt analysis |
| API Design | `architecture/api-design.skill.md` | api, rest, openapi | API contract design |
| Legacy Mod | `architecture/legacy-modernization.skill.md` | cobol, modernize | Legacy modernization |
| API Standards | `architecture/api-standards.skill.md` | api standards | API governance |
| Critical Sys | `architecture/critical-systems-arch.skill.md` | safety critical | DO-178C / robust arch |
| Event Driven | `architecture/event-driven-architecture.skill.md` | eda, event | EDA design |
| Microservices | `architecture/microservices.skill.md` | microservices | Decouple services |
| Monolith | `architecture/monolith.skill.md` | monolith | Modular monoliths |
| System Qualities | `architecture/system-qualities.skill.md` | nfr, qualities | NFR enforcement |
| Systems Arch | `architecture/systems-architecture.skill.md` | c4, systems | Holistic C4 models |
| Enterprise Migration | `architecture/enterprise-migration-scenario.skill.md` | migrate, legacy | Strangler fig rollouts |
| Enterprise Patterns | `architecture/enterprise-patterns.skill.md` | saga, bff | Enterprise design |
| Scalability | `architecture/system-scalability.skill.md` | horizontal, scale | Auditing system bottlenecks |
| Blockchain DLT | `architecture/blockchain-dlt.skill.md` | dlt, web3 | Smart contracts & Ledgers |
| Visual Whiteboard | `architecture/visual-whiteboarding.skill.md` | drawio, miro, figma | Map spatial architecture |
| Attribute-Driven Design | `architecture/attribute-driven-design.skill.md` | add 3.0, quality attributes, drivers | Iterative ADD 3.0 design |
| Fitness Functions | `architecture/fitness-functions.skill.md` | fitness function, evolutionary architecture | Continuous arch governance |

### 3. Operations & SRE (`ops/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Reliability SRE | `ops/reliability-sre.skill.md` | sre, slo, chaos | Reliability engineering |
| Perf Opt | `ops/performance-optimization.skill.md` | fast, cache | Optimization |
| Perf Audit | `ops/performance-audit.skill.md` | profile, flamegraph | Deep profiling |
| Tech Debt | `ops/tech-debt.skill.md` | debt, todo | Debt management |
| Memory Opt | `ops/memory-optimization.skill.md` | leak, heap | Memory profiling |
| Prod Verifier | `ops/production-verifier.skill.md` | verify prod | Post-deploy check |
| Release Val | `ops/release-validation.skill.md` | go no go | Release gating |
| Incident Resp | `ops/incident-response.skill.md` | outage, page | Incident management |
| Docker Dev | `ops/docker-dev.skill.md` | docker, compose | Local containers |
| K8s Dev | `ops/k8s-dev.skill.md` | k8s, telepresence | Remote dev |
| Cloud Deploy | `ops/cloud-deploy.skill.md` | deploy, aws | Cloud deployment |
| Infra DevOps | `ops/infra-devops.skill.md` | terraform, iac | Infrastructure code |
| Deployment | `ops/deployment.skill.md` | ci, cd | Generic pipeline |
| Cost Opt | `ops/cost-optimization.skill.md` | bill, finops | Cost reduction |
| Release Mgmt | `ops/release-management.skill.md` | changelog, tag | Versioning |
| Queue Mgmt | `ops/queue-management.skill.md` | dlq, retry | Async reliability |
| Prod Health | `ops/production-health.skill.md` | health check | System vitals |
| Benchmark | `ops/system-benchmark.skill.md` | load test | Benchmarking |
| Capacity | `ops/capacity-planning.skill.md` | scale, forecast | Capacity planning |
| Caching | `ops/caching-strategy.skill.md` | redis, ttl | Caching patterns |
| Enterprise Int | `ops/enterprise-integration.skill.md` | erp, sap | Enterprise Integration |
| Dev Environments | `ops/dev-environments.skill.md` | devcontainer | Dev setups |
| Troubleshooting | `ops/troubleshooting-guide.skill.md` | troubleshoot | Incident diagnosis |
| Cost Optimization | `ops/cost-optimization.skill.md` | finops, costs | Analyze cloud spend |
| Dev Workflow | `ops/dev-workflow.skill.md` | git workflow, gh cli, docs | Git & Diátaxis docs |
| Observability Setup | `ops/observability-stack-setup.skill.md` | opentelemetry, otel, traces, dashboards | OTel instrumentation + dashboards |
| Feature Flags | `ops/feature-flag-management.skill.md` | feature flag, kill switch, canary | Flag lifecycle + progressive delivery |
| Runbook Authoring | `ops/runbook-authoring.skill.md` | runbook, alert response, remediation | Operational runbooks per alert |
| Dependency Lifecycle | `ops/dependency-lifecycle.skill.md` | dependency upgrade, sbom, cve triage, eol | Patch/upgrade cadence + SBOM |
| Decommission & Sunset | `ops/decommission-sunset.skill.md` | decommission, sunset, deprecation, retention | Sunset + data retention |
| Configuration Management | `ops/configuration-management.skill.md` | scm, branching, baseline, reproducible build | SCM discipline (SWEBOK) |

### 4. Security & Compliance (`security/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Sec Audit | `security/security-audit.skill.md` | owasp, audit | Security review |
| Threat Model | `security/threat-model.skill.md` | stride, threat | Threat modeling |
| Privacy Audit | `security/privacy-audit.skill.md` | pii, gdpr | Privacy impact |
| Compliance | `security/compliance-review.skill.md` | soc2, pci | Compliance check |
| Legal Review | `security/legal-review.skill.md` | license, ip | Legal check |
| Access Control| `security/access-control.skill.md` | rbac, iam | Identity/Access |
| Backup | `security/backup-recovery.skill.md` | backup, restore | DR planning |
| Hazard Analysis| `security/hazard-analysis.skill.md` | fmea, stpa | Safety analysis |
| Reliability Eng| `security/reliability-engineering.skill.md` | tmr, redundancy | Critical systems |
| Network Sec | `security/network-security.skill.md` | firewall, vpc | Network hardening |
| Log Analysis | `security/log-analysis.skill.md` | logs, siem | Security monitoring |
| Traceability | `security/traceability-audit.skill.md` | trace, link | Requirements trace |
| Dep Security | `security/dependency-security.skill.md` | sbom, supply | Supply chain sec |
| AI Ethics | `security/ai-ethics-compliance.skill.md` | bias, ethics | AI safety check |
| AI Guardrails | `security/ai-safety-guardrails.skill.md` | injection, jailbreak | AI defense |
| Secrets | `security/secrets-management.skill.md` | vault, key | Secrets handling |
| Safety Scan | `security/safety-scan.skill.md` | safety scan | Pre-commit safety |
| API Security | `security/api-security.skill.md` | secure api | API vulnerabilities |
| Crypto Standards | `security/cryptography-standards.skill.md` | encrypt | Crypto algorithms |
| Privacy Protection | `security/privacy-data-protection.skill.md` | gdpr, pii | Data privacy |
| Secure Arch | `security/secure-architecture.skill.md` | zero trust | Defense-in-depth |
| Prompt Injection Defense | `security/prompt-injection-defense.skill.md` | prompt injection, indirect injection, lethal trifecta, jailbreak | Defense-in-depth vs injection |

### 5. Data & Analytics (`data/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Data Eng | `data/data-engineering.skill.md` | etl, spark | Data pipelines |
| Data Gov | `data/data-governance.skill.md` | lineage, catalog | Data governance |
| DB Migration | `data/db-migration.skill.md` | migration, sql | Schema changes |
| SQL Opt | `data/sql-optimization.skill.md` | slow query | Query tuning |
| Semantic Web | `data/semantic-web.skill.md` | ontology, rdf | Meta-knowledge graphs |

### 6. Product & Strategy (`product/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Business Case | `product/business-case.skill.md` | roi, cost | Project justification |
| Design Thinking| `product/design-thinking.skill.md` | empathy, ideate | User-centric design |
| Systems Think | `product/systems-thinking.skill.md` | loop, causal | System dynamics |
| Req Elicit | `product/req-elicitation.skill.md` | gather reqs | Interviewing |
| Req Review | `product/req-review.skill.md` | review reqs | Quality gate |
| Spec Writer | `product/spec-writer.skill.md` | write spec | RFC/PRD writing |
| Spec Analyze | `product/spec-analyze.skill.md` | drift, check | Spec verification |
| Decompose | `product/decompose.skill.md` | decompose, break down tasks | Task decomposition (15-min) |
| ADR Writer | `product/adr-writer.skill.md` | adr, decision | Architect decisions |
| Market Analysis| `product/market-analysis.skill.md` | competitors | API/Market research |
| Stakeholder | `product/stakeholder-management.skill.md` | raci, comms | Stakeholder maps |
| User Mapping | `product/user-story-mapping.skill.md` | user journey | User story maps |
| Accessibility | `product/accessibility.skill.md` | a11y, wcag | Accessibility audit |
| Green Software | `product/green-software.skill.md` | green, carbon | medium | Sustainable Software |
| Sustainability | `product/sustainability-checks.skill.md` | esg, sustain | ESG & Sustainability checks |
| Visual Specs | `product/visual-specs.skill.md` | visual spec, diagram spec | Visual inputs → spec package |
| Ideation Facilitation | `product/ideation-facilitation.skill.md` | brainstorm, how-might-we, scamper, crazy-8s | Divergent/convergent ideation |
| User Research Synthesis | `product/user-research-synthesis.skill.md` | affinity map, jtbd, persona synthesis, journey | Synthesize research into personas |
| Opportunity Assessment | `product/opportunity-assessment.skill.md` | wardley, north-star, rice, opportunity sizing | Opportunity brief + RICE |
| Change Management | `product/change-management.skill.md` | adkar, adoption, rollout comms | ADKAR change plan |
| Estimation & Sizing | `product/estimation-sizing.skill.md` | estimation, reference-class, story points | Probabilistic sizing |
| Product Analytics | `product/product-analytics.skill.md` | funnel, a/b test, dora, space, retention | Analytics + delivery metrics |
| Financial Governance | `product/financial-governance.skill.md` | budget, roi, unit economics, cost allocation | Budget + unit economics |
| Professional Practice | `product/professional-practice.skill.md` | ethics code, professional conduct, teamwork, stakeholder comms | SE ethics + professionalism (SWEBOK) |

### 7. Coordination & Agents (`coordination/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Orch | `coordination/multi-agent-orch.skill.md` | swarm, delegate | Agent coordination |
| Interop | `coordination/agent-interop.skill.md` | handshake | Agent connection |
| Protocol | `coordination/agent-protocol.skill.md` | a2a | Message schema |
| Consensus | `coordination/swarm-consensus.skill.md` | vote | Distributed consensus |
| Meta Opt | `coordination/meta-optimize.skill.md` | improve skill | Self-improvement |
| Persona Selector | `coordination/persona-selector.skill.md` | best persona, delegate, route task | Dynamic persona selection + delegation + voting (cost-gated) |
| Self Optimize | `coordination/self-optimize.skill.md` | optimize for project, autonomy level | Tune selection to project for quality+cost; autonomy levels |
| Meta Prompt | `coordination/meta-prompting.skill.md` | system prompt | Prompt engineering |
| Patterns | `coordination/agentic-patterns.skill.md` | react, plan | Agent patterns |
| Linter | `coordination/agentic-linter.skill.md` | boundary | Interaction validity |

### 8. Core System (`core/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Preflight | `core/preflight.skill.md` | preflight, session start, orient | First action: auto-check + load summaries + cost + clarify |
| Clarify | `core/clarify.skill.md` | clarify, ambiguous, what to ask | Uncertainty-aware clarifying questions, every step |
| Update Scan | `core/update-scan.skill.md` | check for updates, new tools, self-evolve | Discover + adopt best skills/tools/MCPs/models (gated) |
| State Preserve | `core/state-preserve.skill.md` | save state, checkpoint, dont lose progress | Continuous + pre-cutoff state save for lossless resume |
| State Portability | `core/state-portability.skill.md` | hydrate, dehydrate, switch agent | Portable state export/import across any agent/LLM |
| Skills Registry | `core/skills-registry.skill.md` | skills registry, import skill, publish skill, agent garden | Import/publish skills to/from universal registries (validated) |
| Final Review | `core/final-review.skill.md` | final review, expert review, anything missing, make it better | Expert end-of-work review: catch gaps + propose optimizations |
| Research | `core/research.skill.md` | research, find | Deep research |
| Gap Analysis | `core/knowledge-gap.skill.md` | unknown | Identify unknowns |
| Self Heal | `core/self-heal.skill.md` | fix error | Auto-recovery |
| Resume | `core/session-resume.skill.md` | resume | Context loading |
| Checkpoint | `core/sdlc-checkpoint.skill.md` | phase done | Project tracking |
| Integrity | `core/integrity-check.skill.md` | verify all | System wide check |
| Audit Trail | `core/audit-trail.skill.md` | log decision | Decision history |
| System Lifecycle | `core/system-lifecycle.skill.md` | lifecycle, traceability, requirement, golden thread | Traceability |
| Emerging | `core/emerging-tech.skill.md` | future | Tech radar |
| Analytics | `core/agent-analytics.skill.md` | token usage | Agent metrics |
| Connectors | `core/knowledge-connect.skill.md` | rag, doc | RAG ingestion |
| Retrospective | `core/retrospective.skill.md` | retro, blameless, lessons learned | Blameless retrospective |
| Empirical Methods | `core/empirical-methods.skill.md` | experiment design, measurement, statistics, root cause | Empirical/measurement methods (SWEBOK) |

### 9. Neuro-Architecture (`brain/`)
*See separate index in `brain/README.md`*
| Skill | File | Context | Purpose |
|---|---|---|---|
| Active Inference | `brain/active-inference.skill.md` | high | Predictive error minimization loop |

### 10. AI & Swarms (`ai/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| A2UI Protocols | `ai/a2ui-protocols.skill.md` | a2ui, genui | Agent-to-UI |
| Actor Frameworks | `ai/actor-agent-frameworks.skill.md` | langgraph | Actor frameworks |
| Agent Comm | `ai/agent-communication.skill.md` | a2a | Agent-to-Agent |
| Agent UI | `ai/agent-ui.skill.md` | agent ui | Specialized UI |
| Beyond LLMs | `ai/beyond-llms.skill.md` | neuro-symbolic | Non-LLM techniques |
| Multi-Agent Sys | `ai/multi-agent-systems.skill.md` | mas, swarm | Orchestrate MAS |
| Auto Swarm Pat. | `ai/autonomous-swarm-patterns.skill.md` | swarm patterns | Self-organizing swarms |
| Cognitive Architectures | `brain/cognitive-architectures.skill.md` | ref | Cognitive Turing Machine theory |
| Consciousness Loop | `brain/consciousness-loop.skill.md` | high | OODA + Strange Loops |
| Cost-Benefit Router | `brain/cost-benefit-router.skill.md` | high | Local vs Remote model routing |
| Episodic Consolidation | `brain/episodic-consolidation.skill.md` | high | Long-term vector storage |
| Epistemology Knowledge | `brain/epistemology-knowledge.skill.md` | ref | Knowledge theory foundations |
| Global Workspace | `brain/global-workspace.skill.md` | high | Central attention management |
| Learning Adaptation | `brain/learning-adaptation.skill.md` | med | Neuroplasticity mechanisms |
| Neuroscience Foundations | `brain/neuroscience-foundations.skill.md` | ref | Cortico-Thalamic theory |
| Self Improvement | `brain/self-improvement.skill.md` | high | Recursive self-editing |
| Sensory Motor | `brain/sensory-motor.skill.md` | med | Embodied tool use |
| Sequential Thinking | `brain/sequential-thinking.skill.md` | think, reason | medium | Step-by-step reasoning |
| Working Memory | `brain/working-memory.skill.md` | high | Session state management |
| LLM-as-Judge | `ai/llm-as-judge.skill.md` | llm judge, rubric scoring, eval bias | Score outputs with an LLM judge |
| RAG Evaluation | `ai/rag-evaluation.skill.md` | rag eval, faithfulness, context precision | Reference-free RAG metrics |
| Cognitive Testing | `brain/cognitive-testing.skill.md` | cognitive test, invariant, convergence, shadow test | Test cognitive loops by invariants |

### 10. Activation Modes (`brain/`)
| Skill | File | Triggers | Context | Purpose |
|---|---|---|---|---|
| **Brain Mode** | `brain/brain-mode.skill.md` | brain activate, supermode | high | **Meta-Cognitive Orchestrator** (Active Inference + Routing) |
| Loki Mode | `brain/loki-mode.skill.md` | loki, swarm | high | Standard 10-phase SDLC Orchestrator |

### 11. Industry Specifications (`industry/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Healthcare FHIR | `industry/healthcare-fhir.skill.md` | fhir, hl7 | Clinical integration |
| Industrial IoT | `industry/industrial-iot.skill.md` | iot, opc | Edge telemetry |
| Telecom Networks | `industry/telecom-networks.skill.md` | tmf, camara | Telecom networking |
| Global Standards | `industry/global-standards.skill.md` | un, itu | UN/ITU/OSI standards |
| Engineering Standards | `industry/engineering-standards.skill.md` | ieee, acm | IEEE/ACM/ISO compliance |
