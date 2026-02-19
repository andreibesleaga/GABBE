# Skills Registry — 00-index.md

> Complete catalog of all available skills.
> Skills = agent capability packages. Invoke by mentioning trigger keywords.
> Context cost: low (< 2k tokens) | medium (2-8k) | high (> 8k)

---

## Installation

### Method 1: This Kit (built-in — no install needed)
All 115+ skills in this directory are ready to use immediately.
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
#   .claude/skills/ -> .agents/skills/*/*.skill.md  (done by setup-context.sh)

# Global scope (all projects on this machine):
ln -sf /path/to/.agents/skills/*/*.skill.md ~/.claude/skills/
# For Gemini/Antigravity:
ln -sf /path/to/.agents/skills/*/*.skill.md ~/.agent/skills/
```

---

> **Total Skills**: 123
> *Registry auto-updated by init.py logic*

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
| Enterprise Int | `ops/enterprise-integration.skill.md` | erp, sap, integration | high | Enterprise Patterns |

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

### 5. Data & Analytics (`data/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Data Eng | `data/data-engineering.skill.md` | etl, spark | Data pipelines |
| Data Gov | `data/data-governance.skill.md` | lineage, catalog | Data governance |
| DB Migration | `data/db-migration.skill.md` | migration, sql | Schema changes |
| SQL Opt | `data/sql-optimization.skill.md` | slow query | Query tuning |

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
| ADR Writer | `product/adr-writer.skill.md` | adr, decision | Architect decisions |
| Market Analysis| `product/market-analysis.skill.md` | competitors | API/Market research |
| Stakeholder | `product/stakeholder-management.skill.md` | raci, comms | Stakeholder maps |
| User Mapping | `product/user-story-mapping.skill.md` | user journey | User story maps |
| Accessibility | `product/accessibility.skill.md` | a11y, wcag | Accessibility audit |
| Green Software | `product/green-software.skill.md` | green, carbon | medium | Sustainable Software |

### 7. Coordination & Agents (`coordination/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
| Orch | `coordination/multi-agent-orch.skill.md` | swarm, delegate | Agent coordination |
| Interop | `coordination/agent-interop.skill.md` | handshake | Agent connection |
| Protocol | `coordination/agent-protocol.skill.md` | a2a | Message schema |
| Consensus | `coordination/swarm-consensus.skill.md` | vote | Distributed consensus |
| Meta Opt | `coordination/meta-optimize.skill.md` | improve skill | Self-improvement |
| Meta Prompt | `coordination/meta-prompting.skill.md` | system prompt | Prompt engineering |
| Patterns | `coordination/agentic-patterns.skill.md` | react, plan | Agent patterns |
| Linter | `coordination/agentic-linter.skill.md` | boundary | Interaction validity |

### 8. Core System (`core/`)
| Skill | File | Triggers | Purpose |
|---|---|---|---|
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
| Working Memory | `brain/working-memory.skill.md` | high | Session state management |

### 10. Activation Modes (`loki/`)
| Skill | File | Triggers | Context | Purpose |
|---|---|---|---|---|
| **Brain Mode** | `loki/brain-mode.skill.md` | brain activate, supermode | high | **Meta-Cognitive Orchestrator** (Active Inference + Routing) |
| Loki Mode | `loki/loki-mode.skill.md` | loki, swarm | high | Standard 10-phase SDLC Orchestrator |
