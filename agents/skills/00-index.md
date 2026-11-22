# Skills Registry — 00-index.md

> Complete catalog of all available skills.
> Skills = agent capability packages. Invoke by mentioning trigger keywords.
> Context cost: low (< 2k tokens) | medium (2-8k) | high (> 8k)

---

## Installation

### Method 1: This Kit (built-in — no install needed)
All 231 skills in this directory are ready to use immediately.
Run `agents/scripts/setup-context.sh` to wire them to your AI tool's skill directory.

### Method 2: Skill Marketplaces & Registries
```bash
# Vercel Skills CLI (recommended for JS/TS projects)
npx skills@1.9.0 install tdd-cycle
npx skills@1.9.0 install code-review

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
#   .claude/skills/ -> agents/skills/*/*.skill.md  (done by agents/scripts/setup-context.sh)

# Global scope (all projects on this machine):
ln -sf /path/to/agents/skills/*/*.skill.md ~/.claude/skills/
# For Gemini/Antigravity:
ln -sf /path/to/agents/skills/*/*.skill.md ~/.agent/skills/
```

---

> **Total Skills**: 231
> *Registry auto-updated by init.py logic*

> **This index is the canonical skill catalog.** Native skill menus (e.g. Claude
> Code) cap how many skills they show by token budget, so they may not list all
> 231 — always consult THIS file to discover any skill, then invoke it by trigger
> or by reading its file. For a clean native menu, emit only the curated core set
> with `compile_skills.py --native-subset core` (49 skills flagged `core: true`);
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
| Characterization Tests | `coding/characterization-tests.skill.md` | characterization test, golden master, pin behaviour | medium | Pin current behaviour before changing legacy code |
| Safe Refactoring | `coding/safe-refactoring.skill.md` | safe refactoring, strangler fig, branch by abstraction | medium | Reversible steps on code without a safety net |
| Incremental Feature | `coding/incremental-feature.skill.md` | feature in existing system, seam | medium | Add a feature to existing code at a seam |
| Mobile Dev | `coding/mobile-dev.skill.md` | mobile, ios, android | medium | RN/Swift/Kotlin dev |
| Visual Design | `coding/visual-design.skill.md` | design, ui, tokens | medium | High-fidelity UI design |
| Vibe Coding | `coding/vibe-coding.skill.md` | vibe, aesthetic | medium | Creative frontend coding |
| CI Autofix | `coding/ci-autofix.skill.md` | ci fix, autofix | medium | Auto-fix CI failures |
| Secure Coding | `coding/secure-coding.skill.md` | secure coding, validate user input, prevent xss, password hashing | medium | Shift-left security |
| Tool Construction | `coding/tool-construction.skill.md` | build a tool, create an mcp server, helper script | medium | Build new tools |
| UI Gen | `coding/ui-gen.skill.md` | generate a ui, build a dashboard, htmx page, terminal ui | medium | Generate React/HTMX UIs |
| File Processing | `coding/file-processing.skill.md` | file processing, large file upload, stream a large file, presigned url upload | medium | Efficient file IO |
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
| Agent Trajectory Eval | `coding/agent-trajectory-eval.skill.md` | trajectory eval, tool-use eval, evaluate agent trajectory | medium | Evaluate tool-call trajectories |
| Output Validation | `coding/output-validation.skill.md` | schema validation, structured output, pii masking | medium | Validate + mask LLM output |
| Property-Based Testing | `coding/pbt-strategy.skill.md` | property test, hypothesis, invariant, stateful | medium | PBT invariants via Hypothesis |
| Metamorphic Testing | `coding/metamorphic-testing.skill.md` | metamorphic, paraphrase invariance, oracle problem | medium | Metamorphic relations for LLM/NLP |
| Assurance Ladder | `coding/assurance-ladder.skill.md` | assurance level, formal verification, assurance plan | medium | Choose verification level 0-3 by risk |
| Mutation Testing | `coding/mutation-testing.skill.md` | mutation score, surviving mutants, stryker, mutmut | medium | Mutation score floor on changed code |
| Design by Contract | `coding/design-by-contract.skill.md` | preconditions, postconditions, invariants, contracts | low | Runnable contracts at module boundaries |
| Fuzz & Differential Testing | `coding/fuzz-differential-testing.skill.md` | fuzzing, differential testing, crash triage | medium | Fuzz parsers, compare with a reference |
| Lightweight Formal Spec | `coding/formal-spec-lightweight.skill.md` | tla+, quint, alloy, model checking | high | Level 2 design model and derived tests |
| Proof of a Small Core | `coding/proof-core-verification.skill.md` | dafny, verus, kani, lean, proof, leak checklist | high | Level 3 machine-checked proof with leak checks |
| Verification Anti-Cheating | `coding/verification-anti-cheating.skill.md` | frozen tests, weakened assertion, hidden assume | low | Stop agents gaming their own checks |
| Chaos & Fault Injection | `coding/chaos-fault-injection.skill.md` | chaos, fault injection, resilience | medium | Fault recipes to expected recovery |
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
| Compatibility | `architecture/compatibility-design.skill.md` | compatibility, migration, versioning | Breaking changes check |
| Arch Gov | `architecture/architecture-governance.skill.md` | architecture governance, archunit, dependency rules | Arch constraints |
| Error Handling | `architecture/error-handling-strategy.skill.md` | error handling strategy, problem details, rfc 9457 | RFC 9457 handling |
| Event Gov | `architecture/event-governance.skill.md` | event governance, schema registry, cloudevents | Event registry |
| GraphQL Schema | `architecture/graphql-schema.skill.md` | graphql schema, graphql, dataloader | Schema design |
| Middleware | `architecture/middleware-design.skill.md` | middleware design, request pipeline, rate limiting middleware | Pipeline design |
| State Mgmt | `architecture/state-management.skill.md` | state management, redux, zustand | State architecture |
| Realtime | `architecture/realtime-comm.skill.md` | realtime comm, websocket, sse | Real-time patterns |
| Arch Debt | `architecture/arch-debt.skill.md` | coupling, cycles | Arch debt analysis |
| API Design | `architecture/api-design.skill.md` | api, rest, openapi | API contract design |
| Legacy Mod | `architecture/legacy-modernization.skill.md` | cobol, legacy code, mainframe | Legacy modernization |
| Existing Project Onboarding | `architecture/existing-project-onboarding.skill.md` | existing codebase, brownfield, onboard codebase | Entry for existing code: map, assess, propose |
| Code Archaeology | `architecture/code-archaeology.skill.md` | code archaeology, map the codebase, hot spots | Recover structure, hot spots, unknowns |
| API Standards | `architecture/api-standards.skill.md` | api standards | API governance |
| Critical Sys | `architecture/critical-systems-arch.skill.md` | design critical system, safety critical, do-178c | DO-178C / robust arch |
| Event Driven | `architecture/event-driven-architecture.skill.md` | eda, event | EDA design |
| Microservices | `architecture/microservices.skill.md` | microservices | Decouple services |
| Monolith | `architecture/monolith.skill.md` | monolith | Modular monoliths |
| System Qualities | `architecture/system-qualities.skill.md` | nfr, qualities | NFR enforcement |
| Systems Arch | `architecture/systems-architecture.skill.md` | c4, systems | Holistic C4 models |
| Enterprise Migration | `architecture/enterprise-migration-scenario.skill.md` | migrate, legacy | Strangler fig rollouts |
| Enterprise Patterns | `architecture/enterprise-patterns.skill.md` | saga, bff | Enterprise design |
| Scalability | `architecture/system-scalability.skill.md` | horizontal, scale | Auditing system bottlenecks |
| Blockchain DLT | `architecture/blockchain-dlt.skill.md` | dlt, web3 | Smart contracts & Ledgers |
| Visual Whiteboard | `architecture/visual-whiteboarding.skill.md` | miro, figma, whiteboard | Map spatial architecture |
| Attribute-Driven Design | `architecture/attribute-driven-design.skill.md` | add 3.0, quality attributes, drivers | Iterative ADD 3.0 design |
| Fitness Functions | `architecture/fitness-functions.skill.md` | fitness function, evolutionary architecture | Continuous arch governance |

### 3. Operations & SRE (`ops/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Reliability SRE | `ops/reliability-sre.skill.md` | define slo and error budget, sre review, chaos engineering experiment, golden signals alerting | Reliability engineering |
| Perf Opt | `ops/performance-optimization.skill.md` | scale this service, add read replicas, shard the database, offload work to a queue | Optimization |
| Perf Audit | `ops/performance-audit.skill.md` | profile this endpoint, web vitals audit, detect n+1 queries, slow sql analysis | Deep profiling |
| Tech Debt | `ops/tech-debt.skill.md` | tech debt, find code smells, todo fixme audit, refactor backlog | Debt management |
| Memory Opt | `ops/memory-optimization.skill.md` | memory optimization, context overflow, reduce token usage, summarize old history | Context and token budget |
| Prod Verifier | `ops/production-verifier.skill.md` | verify production deploy, post-deploy smoke test, canary validation, synthetic monitoring journey | Post-deploy check |
| Release Val | `ops/release-validation.skill.md` | release validation, go no go decision, release readiness report, is this build ready for production | Release gating |
| Incident Resp | `ops/incident-response.skill.md` | production is down, handle this incident, write a post-mortem, manage sev1 | Incident management |
| Docker Dev | `ops/docker-dev.skill.md` | docker compose for local dev, containerize this app, devcontainer config, docker compose watch | Local containers |
| K8s Dev | `ops/k8s-dev.skill.md` | develop against remote cluster, telepresence intercept, okteto setup, devspace yaml | Remote dev |
| Cloud Deploy | `ops/cloud-deploy.skill.md` | deploy to vercel, deploy to railway, deploy to aws, sst serverless | Cloud deployment |
| Infra DevOps | `ops/infra-devops.skill.md` | write terraform for this, kubernetes manifests and helm chart, set up ci cd pipeline, infrastructure as code | Infrastructure code |
| Deployment | `ops/deployment.skill.md` | deploy to production, ci cd pipeline check, docker image security, staging smoke test | Generic pipeline |
| Cost Opt | `ops/cost-optimization.skill.md` | reduce aws bill, analyze cloud costs, find unused resources, optimize instance types | Cost reduction |
| Release Mgmt | `ops/release-management.skill.md` | prepare a release, draft release notes, bump version, generate changelog | Versioning |
| Queue Mgmt | `ops/queue-management.skill.md` | dead letter queue, idempotent consumer, retry policy for queue, duplicate messages | Async reliability |
| Prod Health | `ops/production-health.skill.md` | check system health, prevent infinite loops, optimize agent costs, configure sleep cycles | System vitals |
| Benchmark | `ops/system-benchmark.skill.md` | run system benchmark, test scalability, measure throughput, check system stability | Benchmarking |
| Capacity | `ops/capacity-planning.skill.md` | capacity planning, how many replicas, size the cluster, forecast traffic | Capacity planning |
| Caching | `ops/caching-strategy.skill.md` | caching strategy, add redis cache, cache invalidation, stale cache data | Caching patterns |
| Enterprise Int | `ops/enterprise-integration.skill.md` | integrate with sap, salesforce integration, anti-corruption layer, strangler fig migration | Enterprise Integration |
| Dev Environments | `ops/dev-environments.skill.md` | setup dev environment, configure docker compose, build devcontainer, onboard developers | Dev setups |
| Troubleshooting | `ops/troubleshooting-guide.skill.md` | troubleshoot issue, diagnose system failure, fix production outage, find the root cause | Incident diagnosis |
| Dev Workflow | `ops/dev-workflow.skill.md` | git workflow, github pull request, gh cli, diataxis | Git & Diátaxis docs |
| Observability Setup | `ops/observability-stack-setup.skill.md` | set up observability, instrument with opentelemetry, emit gen_ai spans for llm calls, define slo and sli | OTel instrumentation + dashboards |
| Feature Flags | `ops/feature-flag-management.skill.md` | add a feature flag, plan a canary release with flags, set up a kill switch, clean up stale feature flags | Flag lifecycle + progressive delivery |
| Runbook Authoring | `ops/runbook-authoring.skill.md` | write a runbook for the alert, create an on-call recovery procedure, the alert has no runbook, document remediation steps | Operational runbooks per alert |
| Dependency Lifecycle | `ops/dependency-lifecycle.skill.md` | define our dependency upgrade cadence, set up a dependency lifecycle policy, triage these cve advisories, refresh the sbom for the next release | Patch/upgrade cadence + SBOM |
| Dependency Upgrade | `ops/dependency-upgrade.skill.md` | bump package, upgrade one dependency, breaking change | One-package upgrade procedure with rollback |
| Decommission & Sunset | `ops/decommission-sunset.skill.md` | plan to decommission the legacy billing service, sunset and deprecate the old api, draft a shutdown timeline for the product, export and migrate data before teardown | Sunset + data retention |
| Configuration Management | `ops/configuration-management.skill.md` | define a software configuration management plan, choose branching strategy trunk vs gitflow, set baseline and release versioning, establish change control process | SCM discipline (SWEBOK) |

### 4. Security & Compliance (`security/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Sec Audit | `security/security-audit.skill.md` | owasp, audit | Security review |
| Threat Model | `security/threat-model.skill.md` | stride, threat | Threat modeling |
| Privacy Audit | `security/privacy-audit.skill.md` | pii, gdpr | Privacy impact |
| Compliance | `security/compliance-review.skill.md` | soc2, pci | Compliance check |
| Legal Review | `security/legal-review.skill.md` | check licenses, review for legal compliance, is this library safe to use, gdpr compliance check, license audit | Legal check |
| Access Control| `security/access-control.skill.md` | rbac, access control, abac | Identity/Access |
| Backup | `security/backup-recovery.skill.md` | backup, restore test, rpo rto, disaster recovery, point in time recovery | DR planning |
| Hazard Analysis| `security/hazard-analysis.skill.md` | fmea, stpa | Safety analysis |
| Reliability Eng| `security/reliability-engineering.skill.md` | redundancy, reliability engineering, failover | Critical systems |
| Network Sec | `security/network-security.skill.md` | network security, firewall rules, vpc, subnet isolation, security group | Network hardening |
| Log Analysis | `security/log-analysis.skill.md` | log analysis, read logs, trace id, logql, error spike | Security monitoring |
| Traceability | `security/traceability-audit.skill.md` | traceability, requirement coverage, requirement to test, trace matrix, req coverage | Requirements trace |
| Dep Security | `security/dependency-security.skill.md` | dependency security, vulnerable dependency, sbom, supply chain, lockfile | Supply chain sec |
| AI Ethics | `security/ai-ethics-compliance.skill.md` | ai ethics, eu ai act, bias test, fairness check, dark pattern | AI safety check |
| AI Guardrails | `security/ai-safety-guardrails.skill.md` | ai guardrails, llm guardrails, pii scrubbing, output rails, human in the loop approval | AI defense |
| Secrets | `security/secrets-management.skill.md` | secrets management, api key, rotate secret, leaked secret, vault | Secrets handling |
| Safety Scan | `security/safety-scan.skill.md` | safety scan | Pre-commit safety |
| API Security | `security/api-security.skill.md` | secure api, audit api security, implement jwt auth, api security, bola | API vulnerabilities |
| Crypto Standards | `security/cryptography-standards.skill.md` | encrypt data, hash passwords, set tls policy, cryptography, key management | Crypto algorithms |
| Privacy Protection | `security/privacy-data-protection.skill.md` | privacy by design, data minimisation, pseudonymisation, dsar, right to erasure | Data privacy |
| Secure Arch | `security/secure-architecture.skill.md` | design secure system, enforce zero trust, audit architecture security, defence in depth, trust zones | Defense-in-depth |
| Prompt Injection Defense | `security/prompt-injection-defense.skill.md` | prompt injection, indirect injection, lethal trifecta, jailbreak | Defense-in-depth vs injection |
| AI Red-Teaming | `security/ai-red-teaming.skill.md` | red team, adversarial test, attack success rate, jailbreak test | Offensive AI testing (OWASP LLM) |
| Agent Sandboxing | `security/agent-sandboxing.skill.md` | sandbox, isolation, egress control, least privilege | Intrinsic agent isolation policy |
| Security Baseline | `security/security-baseline.skill.md` | security baseline, security tier, security by phase, security evidence | What security each phase needs, by risk tier |
| Security Requirements | `security/security-requirements.skill.md` | security requirements, abuse cases, privacy requirements | Security and privacy requirements at S01 |
| Agent Tool Review | `security/agent-tool-review.skill.md` | agent tool permissions, excessive agency, mcp tool review | Least privilege for an agent in the product |

### 5. Data & Analytics (`data/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Data Eng | `data/data-engineering.skill.md` | etl, spark | Data pipelines |
| Data Gov | `data/data-governance.skill.md` | data governance, lineage, classification | Data governance |
| DB Migration | `data/db-migration.skill.md` | migration, schema, database | Schema changes |
| SQL Opt | `data/sql-optimization.skill.md` | sql optimization, slow query, explain analyze | Query tuning |
| Semantic Web | `data/semantic-web.skill.md` | ontology, rdf | Meta-knowledge graphs |

### 6. Product & Strategy (`product/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Business Case | `product/business-case.skill.md` | roi, cost | Project justification |
| Design Thinking| `product/design-thinking.skill.md` | ideate, design thinking, empathize | User-centric design |
| Systems Think | `product/systems-thinking.skill.md` | loop, causal | System dynamics |
| Req Elicit | `product/req-elicitation.skill.md` | gather reqs | Interviewing |
| Req Review | `product/req-review.skill.md` | review reqs | Quality gate |
| Spec Writer | `product/spec-writer.skill.md` | write spec | RFC/PRD writing |
| Spec Analyze | `product/spec-analyze.skill.md` | drift, check | Spec verification |
| Decompose | `product/decompose.skill.md` | decompose, break down tasks | Task decomposition (15-min) |
| ADR Writer | `product/adr-writer.skill.md` | adr, decision | Architect decisions |
| Market Analysis| `product/market-analysis.skill.md` | market analysis, competitor comparison, swot analysis, differentiate from competitors, size the market, is there a market for this | API/Market research |
| Stakeholder | `product/stakeholder-management.skill.md` | stakeholder management, power interest grid, raci matrix, who is accountable, plan status updates, stakeholder conflict | Stakeholder maps |
| User Mapping | `product/user-story-mapping.skill.md` | user story mapping, story map, scope the mvp, slice into releases, walking skeleton, map the user journey | User story maps |
| Accessibility | `product/accessibility.skill.md` | a11y, wcag | Accessibility audit |
| Green Software | `product/green-software.skill.md` | green software, reduce carbon footprint, energy efficient design, carbon aware scheduling, low carbon region, eco mode | medium | Sustainable Software |
| Sustainability | `product/sustainability-checks.skill.md` | esg, sustain | ESG & Sustainability checks |
| Visual Specs | `product/visual-specs.skill.md` | visual spec, diagram spec | Visual inputs → spec package |
| Ideation Facilitation | `product/ideation-facilitation.skill.md` | brainstorm, how-might-we, scamper, crazy-8s | Divergent/convergent ideation |
| User Research Synthesis | `product/user-research-synthesis.skill.md` | affinity map, journey, synthesize user research | Synthesize research into personas |
| Opportunity Assessment | `product/opportunity-assessment.skill.md` | wardley, north-star, rice, opportunity sizing | Opportunity brief + RICE |
| Change Management | `product/change-management.skill.md` | adkar, adoption, rollout comms | ADKAR change plan |
| Estimation & Sizing | `product/estimation-sizing.skill.md` | estimation, reference-class, story points | Probabilistic sizing |
| Product Analytics | `product/product-analytics.skill.md` | funnel, dora, space, retention | Analytics + delivery metrics |
| Financial Governance | `product/financial-governance.skill.md` | budget, unit economics, cost allocation | Budget + unit economics |
| Professional Practice | `product/professional-practice.skill.md` | ethics code, professional conduct, teamwork, stakeholder comms | SE ethics + professionalism (SWEBOK) |

### 7. Coordination & Agents (`coordination/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Orch | `coordination/multi-agent-orch.skill.md` | swarm, orchestrate, delegation | Agent coordination |
| Interop | `coordination/agent-interop.skill.md` | handshake | Agent connection |
| Protocol | `coordination/agent-protocol.skill.md` | a2a | Message schema |
| Consensus | `coordination/swarm-consensus.skill.md` | swarm consensus, vote on a decision, agents disagree, break a tie, majority vote, k-threshold vote | Distributed consensus |
| Meta Opt | `coordination/meta-optimize.skill.md` | improve skill | Self-improvement |
| Persona Selector | `coordination/persona-selector.skill.md` | best persona, delegate, route task | Dynamic persona selection + delegation + voting (cost-gated) |
| Self Optimize | `coordination/self-optimize.skill.md` | optimize for project, autonomy level | Tune selection to project for quality+cost; autonomy levels |
| Meta Prompt | `coordination/meta-prompting.skill.md` | meta prompting, write a prompt for a subagent, improve this prompt, prompt gives inconsistent results, chain of thought prompt, tree of thoughts prompt | Prompt engineering |
| Patterns | `coordination/agentic-patterns.skill.md` | react, plan | Agent patterns |
| Workflow Patterns | `coordination/agent-workflow-patterns.skill.md` | prompt chaining, routing, orchestrator-workers, evaluator-optimizer | Workflow taxonomy (workflow vs agent) |
| Linter | `coordination/agentic-linter.skill.md` | boundary | Interaction validity |

### 8. Core System (`core/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| GABBE Start | `core/gabbe-start.skill.md` | gabbe start, start here, what is gabbe, which skill | Entry point: operating rules, choice of way of working, lifecycle map, state files |
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
| Emerging | `core/emerging-tech.skill.md` | 6g, iot, matter | Tech radar |
| Analytics | `core/agent-analytics.skill.md` | token usage | Agent metrics |
| Connectors | `core/knowledge-connect.skill.md` | rag, doc | RAG ingestion |
| Retrospective | `core/retrospective.skill.md` | retro, blameless, lessons learned | Blameless retrospective |
| Empirical Methods | `core/empirical-methods.skill.md` | experiment design, measurement, statistics, root cause | Empirical/measurement methods (SWEBOK) |

### 9. Neuro-Architecture (`brain/`)
*See separate index in `brain/README.md`*
| Skill | File | Context | Purpose |
|---|---|---|---|
| Active Inference | `brain/active-inference.skill.md` | high | Predictive error minimization loop |
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
| Sequential Thinking | `brain/sequential-thinking.skill.md` | think, reason | Step-by-step reasoning |
| Working Memory | `brain/working-memory.skill.md` | high | Session state management |
| Cognitive Testing | `brain/cognitive-testing.skill.md` | cognitive test, invariant, convergence, shadow test | Test cognitive loops by invariants |

### 10. AI & Swarms (`ai/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| A2UI Protocols | `ai/a2ui-protocols.skill.md` | design agent ui protocol, implement a2ui, build genui, stream ui from agent | Agent-to-UI |
| Actor Frameworks | `ai/actor-agent-frameworks.skill.md` | setup langgraph, implement actor framework, configure agent framework, agent graph checkpoints | Actor frameworks |
| Agent Comm | `ai/agent-communication.skill.md` | setup swarm communication, implement a2a protocol, connect agents using mcp, design gossip protocol | Agent-to-Agent |
| Agent UI | `ai/agent-ui.skill.md` | build agent ui, create tracing dashboard, implement agent front-end, show agent tool calls | Specialized UI |
| Beyond LLMs | `ai/beyond-llms.skill.md` | implement active inference, add neuro-symbolic logic, optimize using genetic algorithms, symbolic rules over llm | Non-LLM techniques |
| Multi-Agent Sys | `ai/multi-agent-systems.skill.md` | design mas, setup multi-agent, orchestrate agents, supervisor and sub-agents | Orchestrate MAS |
| Auto Swarm Pat. | `ai/autonomous-swarm-patterns.skill.md` | implement swarm, deploy autonomous agents, setup swarm consensus, ant colony pattern | Self-organizing swarms |
| LLM-as-Judge | `ai/llm-as-judge.skill.md` | score open-ended output, llm as judge, evaluation rubric, pairwise comparison eval | Score outputs with an LLM judge |
| RAG Evaluation | `ai/rag-evaluation.skill.md` | evaluate rag pipeline, measure faithfulness, context precision recall, detect rag hallucination | Reference-free RAG metrics |
| Context Engineering | `ai/context-engineering.skill.md` | context engineering, context window budget, context rot, prompt caching | Write/Select/Compress/Isolate context |
| Reasoning Patterns | `ai/reasoning-patterns.skill.md` | chain of thought, self-consistency, tree of thoughts, least to most | Reasoning-technique selection by problem shape |

### 11. Activation Modes (`brain/`)
| Skill | File | Triggers | Context | Purpose |
|---|---|---|---|---|
| **Brain Mode** | `brain/brain-mode.skill.md` | brain mode, activate brain | high | **Plan-and-review layer**: cheapest strategy that passes, decision log (Active Inference wording is framing) |
| Loki Mode | `brain/loki-mode.skill.md` | loki mode, activate loki, run the lifecycle | high | 14-phase lifecycle orchestrator S00–S13 with six human gates |

### 12. Industry Specifications (`industry/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Healthcare FHIR | `industry/healthcare-fhir.skill.md` | fhir, hl7 | Clinical integration |
| Industrial IoT | `industry/industrial-iot.skill.md` | iot, opc | Edge telemetry |
| Telecom Networks | `industry/telecom-networks.skill.md` | tmf, camara | Telecom networking |
| Global Standards | `industry/global-standards.skill.md` | un, itu | UN/ITU/OSI standards |
| Engineering Standards | `industry/engineering-standards.skill.md` | ieee, acm | IEEE/ACM/ISO compliance |
