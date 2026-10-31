# GABBE — ops (Claude Code plugin)

GABBE ops skills (30): operations: deployment, environments, observability, incidents, performance, cost and release management.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-ops@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Version 1.1.3. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `caching-strategy` — Implement Redis/Memcached patterns and invalidation strategies.
- `capacity-planning` — Forecasting resource usage, load testing interpretation, and scaling limits.
- `cloud-deploy` — Deploy applications to modern cloud platforms (Vercel, Railway, AWS).
- `configuration-management` — Establish a unified software configuration management discipline covering branching, baselines, change control, reproducible builds, versioning, SBOM, and config audit.
- `cost-optimization` — Cloud cost analysis and optimization (FinOps)
- `decommission-sunset` — Plan the safe sunset of a service or product — deprecation policy and timeline, data retention/migration/export, user comms, contract wind-down, traffic drain, teardown, and post-sunset verification.
- `dependency-lifecycle` — Define a dependency lifecycle policy — patch/minor/major upgrade cadence, SBOM refresh, CVE triage, EOL tracking, automated PRs, lockfile hygiene, and supply-chain pinning.
- `deployment` — CI/CD pipeline verification, Docker container security, environment management, and deployment workflow
- `dev-environments` — Set up, configure, and maintain local/remote development environments
- `dev-workflow` — Standardized Github operations, Diátaxis documentation framework, and visual assets
- `docker-dev` — Assistance with Local Development using Docker (Compose, DevContainers).
- `enterprise-integration` — Design integrations with ERP/CRM systems and modernize legacy applications.
- `feature-flag-management` — Manage the full feature-flag lifecycle — create, roll out, measure, and clean up — across release, ops/kill-switch, experiment, and permission flag types with progressive delivery.
- `incident-response` — Manage production incidents, SEV levels, and post-mortems
- `infra-devops` — Design and implement cloud infrastructure (Terraform/K8s) and CI/CD pipelines.
- `k8s-dev` — Assistance with Remote Kubernetes Development (Telepresence, Okteto, DevSpace).
- `memory-optimization` — Summarizing context, pruning history, and managing token budget efficiency.
- `observability-stack-setup` — Bootstrap end-to-end observability with OpenTelemetry traces, metrics, and logs, including GenAI LLM span conventions, dashboards, alerts, and SLO/SLI definition.
- `performance-audit` — Profiling, benchmarking, Web Vitals audit, N+1 detection, and performance optimization
- `performance-optimization` — Optimize systems for speed and scale (Caching, Sharding, Async).
- `production-health` — Manage system stability, avoid agentic loops, optimize costs, and enforce sleep cycles.
- `production-verifier` — Post-deployment smoke tests, synthetic user checks, and "Canary" validation in Prod.
- `queue-management` — Standards for DLQs (Dead Letter Queues), Idempotency, and Retry policies.
- `release-management` — Manage versioning, changelogs, and release processes
- `release-validation` — The final "Green Light". Checks all test suites (Unit, Int, E2E) and third-party reports.
- `reliability-sre` — Apply SRE principles (SLO, Error Budget, Chaos Engineering).
- `runbook-authoring` — Author operational runbooks so every alert maps to a tested, copy-pasteable, idempotent recovery procedure with diagnosis, remediation, escalation, rollback, and verification.
- `system-benchmark` — Measure system throughput, stability, scalability, and resilience.
- `tech-debt` — Identify, document, score, and prioritize technical debt into an actionable backlog
- `troubleshooting-guide` — Diagnose complex system failures through systematic troubleshooting

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
