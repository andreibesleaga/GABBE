# Loki Swarm — Persona Taxonomy
<!-- Full registry of all agent personas in the swarm system -->
<!-- Each persona = a specialized agent role with defined scope, outputs, and constraints -->
<!-- Invoked by: orch-planner (task assignment) or loki-mode.skill (orchestration) -->

---

## The 4 Swarms

```
┌─────────────────────────────────────────────────────────────────┐
│  PRODUCT/BUSINESS SWARM (Deciders)                              │
│  Translates human intent → verifiable artifacts                 │
│  prod-pm · prod-architect · prod-tech-lead · prod-design        │
│  biz-legal · biz-compliance                                     │
└─────────────────────────────────────────────────────────────────┘
         │ spec.md, plan.md, ADRs, project/tasks.md
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION SWARM (Managers)                                 │
│  Coordinates workflow, verifies quality, routes failures        │
│  orch-planner · orch-judge · orch-coordinator · orch-researcher │
└─────────────────────────────────────────────────────────────────┘
         │ task assignments, quality gates, research findings
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  ENGINEERING SWARM (Builders)                                   │
│  Implements code — deep technical, narrow context               │
│  eng-frontend · eng-backend · eng-database · eng-api            │
│  eng-mobile · eng-qa · eng-perf · eng-infra                     │
└─────────────────────────────────────────────────────────────────┘
         │ code, tests, migrations, CI config
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  OPERATIONS SWARM (Enablers)                                    │
│  Path to production: deploy, secure, monitor, comply            │
│  ops-devops · ops-security · ops-sre · ops-monitor              │
│  ops-incident · ops-release · ops-cost · ops-compliance         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Engineering Swarm — Builders

| Persona | File | Role | Primary Output |
|---|---|---|---|
| `eng-frontend` | [eng-frontend.md](eng-frontend.md) | UI/UX implementation, components, browser TDD | Component files, CSS, Playwright tests |
| `eng-backend` | [eng-backend.md](eng-backend.md) | APIs, use cases, domain logic | Controllers, use cases, domain entities |
| `eng-database` | [eng-database.md](eng-database.md) | Schema design, migrations, query optimization | Migration files, seed data, indexes |
| `eng-api` | [eng-api.md](eng-api.md) | API contracts, OpenAPI specs, GraphQL schemas | openapi.yaml, resolvers, contract tests |
| `eng-mobile` | [eng-mobile.md](eng-mobile.md) | Mobile app (iOS/Android/React Native) | Mobile screens, navigation, device tests |
| `eng-qa` | [eng-qa.md](eng-qa.md) | Test suites, acceptance criteria validation | Test files, coverage reports |
| `eng-perf` | [eng-perf.md](eng-perf.md) | Performance optimization, profiling | Benchmark reports, optimized code |
| `eng-infra` | [eng-infra.md](eng-infra.md) | Docker, CI/CD config, environment setup | Dockerfiles, GitHub Actions workflows |
| `eng-tooling` | [eng-tooling.md](eng-tooling.md) | Tool builder, script automation, MCPs | Custom scripts, MCP servers |
| `eng-data` | [eng-data.md](eng-data.md) | Pipelines, ETL, Spark, dbt | Data pipelines, dbt models |
| `eng-ml` | [eng-ml.md](eng-ml.md) | Model training, MLOps, inference | Model APIs, training pipelines |
| `eng-messaging` | [eng-messaging.md](eng-messaging.md) | Queues, Event Schemas, Async | Event Specifications, DLQ Configs |

---

## Operations Swarm — Enablers

| Persona | File | Role | Primary Output |
|---|---|---|---|
| `ops-devops` | [ops-devops.md](ops-devops.md) | Pipeline management, deployments, environments | CI/CD configs, deployment scripts |
| `ops-security` | [ops-security.md](ops-security.md) | Adversarial security — finds exploits in code | Security audit report, CVE findings |
| `ops-sre` | [ops-sre.md](ops-sre.md) | Reliability, SLOs, incident response | SLO definitions, runbooks, alerting rules |
| `ops-monitor` | [ops-monitor.md](ops-monitor.md) | Observability, dashboards, alerting | Dashboard configs, alert rules |
| `ops-incident` | [ops-incident.md](ops-incident.md) | Incident investigation and postmortems | Incident reports, action items |
| `ops-release` | [ops-release.md](ops-release.md) | Release management, changelogs, versioning | CHANGELOG.md, release tags |
| `ops-cost` | [ops-cost.md](ops-cost.md) | Cloud cost optimization | Cost analysis report, recommendations |
| `ops-compliance` | [ops-compliance.md](ops-compliance.md) | Regulatory compliance, audit evidence | Compliance report, evidence package |

---

## Product/Business Swarm — Deciders

| Persona | File | Role | Primary Output |
|---|---|---|---|
| `prod-pm` | [prod-pm.md](prod-pm.md) | Product requirements (EARS), PRD writer | PRD.md, EARS_REQUIREMENTS.md |
| `prod-architect` | [prod-architect.md](prod-architect.md) | Architecture decisions, C4 model, ADRs | PLAN.md, C4_ARCHITECTURE.md, ADR-*.md |
| `prod-tech-lead` | [prod-tech-lead.md](prod-tech-lead.md) | Business Strategy, Requirements, Stakeholder Management | PRDs, User Stories, Roadmaps |
| `prod-design` | [prod-design.md](prod-design.md) | UX Design, User Flows, Wireframes | Design Specs, Mockups, Prototypes |
| `ui-design` | [ui-design.md](ui-design.md) | Visual Design, CSS, Design Tokens | High-Fidelity mocks, Token System |
| `prod-ethicist` | [prod-ethicist.md](prod-ethicist.md) | AI Ethics & Sustainability Officer | Ethical Impact Assessments, Governance |
| `prod-safety-engineer` | [prod-safety-engineer.md](prod-safety-engineer.md) | Safety Officer (Hazel) - Hazard Analysis & Compliance | Hazard Analysis Reports, Safety Compliance Docs |
| `prod-research` | [prod-research.md](prod-research.md) | User Research, Market Analysis, Competitive Intel | Research Reports, User Personas |
| `biz-compliance` | [biz-compliance.md](biz-compliance.md) | Business compliance, policies, audit | Business compliance report |
| `biz-legal` | [biz-legal.md](biz-legal.md) | Legal review, licenses, contracts | Legal approval, license report |

---

## Orchestration Swarm — Managers

| Persona | File | Role | Primary Output |
|---|---|---|---|
| `orch-planner` | [orch-planner.md](orch-planner.md) | Task scheduling, dependency resolution, assignments | Task assignments (from project/tasks.md) |
| `orch-judge` | [orch-judge.md](orch-judge.md) | 7-gate quality checks, EARS compliance | Quality gate verdicts |
| `orch-coordinator` | [orch-coordinator.md](orch-coordinator.md) | State tracking, failure routing, escalations | Escalation reports, status updates |
| `orch-researcher` | [orch-researcher.md](orch-researcher.md) | Authoritative research, knowledge gaps | Research findings in semantic/ |

---

## Swarm Interaction Rules

```
1. Product/Business → Orchestration: deliver spec artifacts
   (orch-planner receives project/tasks.md from prod-tech-lead)

2. Orchestration → Engineering: task assignments
   (orch-planner assigns T-NNN to eng-* with context)

3. Engineering → Orchestration: completion or failure
   (eng-* reports DONE/BLOCKED to orch-planner)

4. Orchestration → Operations: quality-gated handoff
   (orch-judge approves S06, ops-security receives for S07)

5. Operations → Orchestration: deployment status
   (ops-devops reports to orch-coordinator after each deploy)

6. Any swarm → orch-researcher: knowledge gap
   (any agent invokes orch-researcher for API/library research)

7. orch-coordinator → human: escalation
   (only orch-coordinator raises human escalations — not individual eng-*)
```

---

## Persona Constraints

All personas share these universal constraints:
- Always read AGENTS.md and CONSTITUTION.md before acting
- Always check CONTINUITY.md for past failures before starting
- Never skip the RARV Cycle (loki/RARV_CYCLE.md)
- Never exceed own scope (e.g., eng-backend never touches UI)
- Never commit secrets or PII to any file
- Never modify AUDIT_LOG.md existing entries
- Always invoke knowledge-gap.skill before using unknown APIs
- Always write audit log entry for every significant action
