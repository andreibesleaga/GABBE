# GABBE — ops (Claude Code plugin)

GABBE ops skills (26): operations: deployment, environments, observability, incidents, performance, cost and release management.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe-ops@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills@1.9.0 add andreibesleaga/GABBE -a claude-code
```

Version 1.2.0. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `caching-strategy` — Choose a cache pattern (cache-aside, read-through, write-through, write-behind) with TTLs, invalidation, key naming and fallbacks for Redis or Memcached. Use when you add a cache, see stale data, or a hot key overloads the store.
- `capacity-planning` — Estimate how many instances, how much memory, IO and connections a service needs, from a baseline, a growth factor, a load test and headroom. Use when you plan for a traffic increase, size a cluster or set autoscaling limits.
- `cloud-deploy` — Configure and deploy an app to Vercel, Railway or AWS (SST) with config files in the repo, parity of environments and no hand-set options. Use when you pick a hosting platform or write vercel.json, railway.toml or sst.config.ts.
- `configuration-management` — Write a software configuration management plan - branching model, baselines, change control, reproducible builds, versioning, SBOM and configuration audit. Use when a project has no clear release identity, builds differ between machines, or you must choose trunk or git-flow.
- `cost-optimization` — Find cloud spend that can be cut (idle compute, unused storage, network, over-sized databases) and report each item with savings and risk. Use when the cloud bill grows, a FinOps review is due, or you look for unused resources.
- `decommission-sunset` — Plan the retirement of a service or product - deprecation timeline, data retention and export, user notices, contracts, traffic drain, teardown and checks afterwards. Use when the human decides to retire or shut down a system.
- `dependency-lifecycle` — Set the policy for keeping dependencies current - patch, minor and major cadence, SBOM refresh, CVE triage, EOL tracking, automated update PRs, lockfiles and pinning. Use when you define or review how a project handles updates and advisories.
- `dev-environments` — Set up a team-wide development environment with DevContainers, DevSpace or Docker Compose, with seed data and sample configuration. Use when onboarding is slow, "works on my machine" bugs appear, or a project needs a shared dev setup.
- `dev-workflow` — Handle git and GitHub tasks with the gh CLI and organise documentation with the Diataxis quadrants (tutorial, how-to, reference, explanation). Use when you restructure docs, prepare commits or a PR, or need to pick a doc type.
- `docker-dev` — Set up local development with Docker - Compose with watch mode, DevContainers, multi-stage Dockerfiles, non-root users, volumes. Use when you containerise an app for local work or fix slow or broken Docker dev setups.
- `enterprise-integration` — Design integrations between a modern app and ERP, CRM or legacy systems - messaging patterns, anti-corruption layer, strangler fig, CDC, facade APIs. Use when you connect to SAP, Salesforce or a legacy system, or add a message bus.
- `feature-flag-management` — Plan a feature flag from dark launch to removal - flag type, safe default, progressive rollout, kill switch, metrics, cleanup owner and date. Use when you add a flag, plan a canary or percentage rollout, or clean up stale flags.
- `infra-devops` — Write infrastructure as code (Terraform, OpenTofu), Kubernetes manifests and CI/CD pipelines with least privilege, private networks and remote state. Use when you create or change cloud infrastructure, Helm charts or pipeline files.
- `k8s-dev` — Set up development against a remote Kubernetes cluster with Telepresence, Okteto or DevSpace - intercepts, file sync, per-developer namespaces, RBAC. Use when the app is too big for a laptop or needs cloud-only services such as RDS or SQS.
- `memory-optimization` — Keep an agent's context small and cheap - rolling summaries, entity extraction, pruning of files and logs, a forget step after each task, top-k retrieval. Use when the context overflows, token costs climb or a long session loses focus.
- `observability-stack-setup` — Plan OpenTelemetry traces, metrics and logs, GenAI span attributes, SLIs and SLOs, dashboards and alerts that each link to a runbook. Use when you add tracing, define SLOs, or cannot see why a service or LLM call is slow or costly.
- `performance-audit` — Find bottlenecks by measurement - load tests, CPU and memory profiles, Web Vitals, N+1 queries, slow SQL, bundle size, then check each fix with a before and after benchmark. Use when an endpoint or page is slow and you must prove why.
- `performance-optimization` — Choose and apply speed and scale fixes after profiling - caching, read replicas, sharding, indexes, queues, event-driven design. Use when measured latency or load needs a design change, not just a code tweak.
- `production-health` — Check the operational health of an agentic system in production - loop and recursion stops, circuit breakers, sleep and scale-down, cost caps, model routing. Use when an agent loops, spend jumps, or you need a health check of a running agent.
- `production-verifier` — Verify a live deploy with read-only smoke checks, a 10% canary on error rate, p95 and business metrics, and a scripted browser journey. Use right after a production deploy, or to decide on a rollback.
- `queue-management` — Set rules for message queues - dead-letter queues, idempotent consumers, retries, at-least-once delivery, ordering and poison pills. Use when you add a consumer, messages are lost or processed twice, or a DLQ fills up.
- `reliability-sre` — Apply SRE practice - SLIs and SLOs, error budgets and freeze policy, golden signals, symptom alerts, blameless post-mortems and chaos tests. Use when you set reliability targets, an error budget runs out, or on-call needs a recovery guide.
- `runbook-authoring` — Write an operational runbook for one alert - symptom, impact, read-only diagnosis, idempotent remediation, verification, rollback, escalation. Use when an alert has no runbook or an incident needs a repeatable recovery procedure.
- `system-benchmark` — Design and run load, stress, soak and resilience tests on a staging system, then report throughput, p95 and p99 latency, error rate and the first bottleneck. Use when you must measure capacity or check a system against its performance requirements.
- `tech-debt` — Find technical debt (markers, complexity, duplication, coverage gaps, structural smells, stale dependencies), score it by impact and effort, and write a P1 to P4 backlog. Use when quality decays, before a refactor plan, or to size repayment work.
- `troubleshooting-guide` — Diagnose a system failure step by step - gather facts, list and rule out hypotheses, run the smallest safe check, then write a remediation task list. Use when something is broken and the cause is unknown, or after an incident is contained.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
