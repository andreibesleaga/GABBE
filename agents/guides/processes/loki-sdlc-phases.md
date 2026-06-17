# Loki Mode — Detailed SDLC Phase Specifications (S00–S13)

> Referenced by `agents/skills/brain/loki-mode.skill.md`. This holds the full
> per-phase detail (personas, tasks, outputs, gates, checkpoints) so the skill
> stays under the activation-size budget. Loaded on demand during orchestration.
>
> The core build loop is S01–S10. **S00 is the Day-0 strategy & discovery phase**
> that runs BEFORE S01, and **S11–S13 are the Day-2 phases** (operate, evolve,
> sunset) that run AFTER S10 once the system is live.

## Orchestration Loop — SDLC Phases (S00–S13)

### PHASE S00 — Strategy & Discovery (Day-0)

```
Personas: prod-research (lead), prod-pm
Tasks:    prod-research:
            - Run ideation-facilitation.skill (structured ideation, problem framing)
            - Run user-research-synthesis.skill (synthesize interviews/signals → insights)
            - Market & competitive scan; map the value chain with a Wardley map
            - Draft the problem statement (the job-to-be-done, who hurts, why now)
          prod-pm:
            - Run opportunity-assessment.skill (size the opportunity, risks, bets)
            - Define the North-Star metric + supporting HEART metrics
            - Prioritize candidate bets with RICE (Reach·Impact·Confidence ÷ Effort)
            - Frame go/no-go recommendation with explicit success criteria

Output:  docs/discovery/PROBLEM_STATEMENT.md
         docs/discovery/OPPORTUNITY_ASSESSMENT.md (RICE table, North-Star/HEART)
         docs/discovery/MARKET_SCAN.md (competitive scan + Wardley map)

Gate:    HUMAN GO/NO-GO REQUIRED — hard stop
         Present discovery summary (problem, opportunity, metrics, RICE) to user.
         Human decides go/no-go BEFORE S01 may start.
         NO-GO → archive discovery, stop. GO → proceed to S01.

Checkpoint: sdlc-checkpoint.skill S00
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S00_discovery.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S00, status: DONE
  - Log:    agents/memory/AUDIT_LOG.md → PHASE_TRANSITION: S00 complete (GO/NO-GO recorded)
```

### PHASE S01 — Requirements

```
Persona: prod-pm
Task:    Write PRD.md using EARS syntax
         Ask user clarifying questions (ambiguity layer)
         Fill templates/product/PRD_TEMPLATE.md
         Run ai-ethics-compliance.skill (Mandatory Bias Check)
         IF CRITICAL (Health/Aviation):
           - Engage prod-safety-engineer
           - Run hazard-analysis.skill (FMEA/STPA)
Output:  docs/requirements/PRD.md
         docs/requirements/EARS_REQUIREMENTS.md

Gate:    HUMAN APPROVAL REQUIRED
         Present PRD to user → wait for explicit approval
         User may request changes → loop until approved

Checkpoint: sdlc-checkpoint.skill S01
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S01_requirements.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S01, status: DONE
  - Log:    agents/memory/AUDIT_LOG.md → PHASE_TRANSITION: S01 complete
```

### PHASE S02 — Architecture Design

```
Personas: prod-architect (lead), ops-security (threat review)
Tasks:    prod-architect:
            - Write PLAN.md using C4 model
            - Define Error Handling Strategy (RFC 7807) using error-handling-strategy.skill
            - Create docs/architecture/C4_ARCHITECTURE.md
            - Write ADRs for all major decisions → docs/architecture/decisions/
          ops-security:
            - Review architecture for security concerns (adversarial)
            - Run threat-model.skill on critical components
            - Write THREAT_MODEL.md → docs/security/

Output:   PLAN.md, C4_ARCHITECTURE.md, ADR-001+, THREAT_MODEL.md

Gate:     HUMAN APPROVAL REQUIRED
          Present: architecture summary + threat assessment + (Safety Case if Critical)
          Wait for approval. Loop if changes requested.

Checkpoint: sdlc-checkpoint.skill S02
```

### PHASE S03 — Technical Specification

```
Persona: prod-tech-lead (with prod-architect review)
Tasks:   - Fill templates/product/SPEC_TEMPLATE.md
         - Define all API contracts (OpenAPI YAML)
         - Define Event Topology (AsyncAPI) & Schemas (event-governance.skill)
         - Define database schema changes
         - Define Data Governance (Classification) & Access Control (RBAC)
         - Define RPO/RTO targets
         - Define testing strategy
Output:  SPEC.md, docs/api/openapi.yaml, docs/db/schema-changes.md

Gate:    HUMAN APPROVAL — lighter / may be async (the tech spec IS human-approved, but it
         is not a hard *blocking* stop like the S01, S02, S07, S08 gates)

Checkpoint: sdlc-checkpoint.skill S03
```

### PHASE S04 — Task Decomposition

```
Persona: prod-tech-lead (with orch-planner)
Tasks:   - Read SPEC.md + PLAN.md
         - Decompose into atomic tasks (15-minute rule enforced)
         - Fill templates/core/TASKS_TEMPLATE.md
         - Assign each task to the appropriate eng-* persona
         - Identify dependencies (DAG) AND Independent tasks
         - **Parallelism**: Mark independent tasks with `[PARALLEL]` tag

         - **Adaptive Check**:
           - *If Plan Complexity > High*: Inject `S02_DEEP_RESEARCH` (Consult KIs / Web)
           - *If Security Critical*: Inject `safety-scan` pre-check

Output:  project/TASKS.md with T-NNN IDs, status: TODO, tags: [PARALLEL] if applicable

Gate:    orch-judge reviews task decomposition:
         - Are all tasks < 15 minutes?
         - Does task coverage match SPEC acceptance criteria?
         - Are parallel groups correctly identified?

Checkpoint: sdlc-checkpoint.skill S04
```

### PHASE S05 — Implementation

```
Persona: orch-planner (coordinator), eng-* (executors)
SCM discipline: apply configuration-management.skill (branching model, baselines,
  reproducible builds) alongside git-workflow.skill throughout this phase.

Implementation Loop (repeats until all tasks DONE):
  1. orch-planner analyzes `project/TASKS.md`:
     - Identifies next batch of independent TODO tasks (Parallel Group)
     - Or next sequential task if dependencies exist

  2. **Context Retrieval (RAG)**:
     - Invoke `knowledge-connect.skill` query: "How to implement [task keywords]?"
     - Retrieve top 3 relevant snippets from `VECTOR_DB_CONFIG` source
     - **On Failure**: Log warning "RAG Unavailable", attempt fallback to `filesystem` search, or proceed with available context only.
     - Inject into task context

  3. **Delegation (A2A Check)**:
     - Is this task for an external agent? (e.g., "Ask Security Swarm")
     - YES -> Invoke `agent-interop.skill` -> Delegate -> Wait -> generic result
     - NO  -> Assign to internal `eng-*` persona

  4. **Execution (Parallel/Batch)**:
     - For each task in current batch (concurrently if model supports):

       assigned eng-* persona executes RARV Cycle:
       REASON:  Load task context + AGENTS.md + CONTINUITY.md + RAG Context
                Write mini-plan before touching files

       ACT:     Write failing test (TDD Red — MANDATORY)
                Verify test fails before implementing
                Run `safety-scan.skill` (Guardrail)
                Implement minimal code (Apply secure-coding.skill triggers)
                Update project/TASKS.md: status → IN_PROGRESS

       REFLECT: Library-First? Layer boundaries? Security inputs? PII in logs?

       VERIFY:  Run: [test command]      → must be GREEN
                Run: [typecheck]         → zero errors
                Run: [lint]              → zero errors
                Run: agentic-linter      → no violations

  5. **Batch Result Processing**:
     - If VERIFY passes:
       - Update project/TASKS.md: status → DONE
       - Write audit-trail.skill entry: TASK_DONE

     - If VERIFY fails:
       - **Quick Check**: Invoke `ci-autofix` (Autonomous Remediation)
         - If FIXED -> Proceed to DONE logic
       - **Dynamic Optimization**: Invoke `self-heal.skill` (max 5 attempts)
         - *Input*: Error log + Task Context + RAG Context
         - *Output*: Fix applied OR Escalation
       - **Meta-Optimization**: If `self-heal` FAILS repeatedly (>3x):
         - Invoke `meta-optimize.skill` (Rewrite the failing skill/prompt)
         - Log: "Self-Evolution Triggered for [Skill Name]"
       - If escalated:
         - orch-coordinator logs HUMAN_ESCALATION
         - task status → BLOCKED

  6. Repeat until all tasks DONE

Checkpoint: sdlc-checkpoint.skill S05
  (Save after every batch to prevent state loss)
```

### PHASE S06 — Testing & Quality

```
Persona: eng-qa (lead), orch-judge (validator)

eng-qa Tasks:
  - Run full test suite → verify all green
  - Check coverage ≥ 99% per module
  - Run integration test suite
  - Identify any missing test scenarios from EARS acceptance criteria
  - Fill any gaps via tdd-cycle.skill
  - Score probabilistic quality via eval-driven-development.skill; interpret benchmark/
    A-B results with empirical-methods.skill (effect size, significance — not just averages)

orch-judge Tasks:
  - Quality Gate Check (orch-judge's 7-gate system, extended here with E2E + EARS):
    Gate 1: Lint/Syntax  → ESLint/PHP-CS-Fixer → zero errors
    Gate 2: Type Safety  → tsc/PHPStan         → zero errors
    Gate 3: Coverage     → Vitest/Pest          → ≥ 99%
    Gate 4: Integration  → Docker Compose       → all green
    Gate 5: Security     → dependency-security.skill → no critical vulnerabilities
    Gate 6: Complexity   → Cyclomatic < 10 for all functions
    Gate 7: Architecture → architecture-governance.skill → no layer violations (Fitness Functions)
    Gate 8: E2E          → e2e-test-suite (Playwright/Cypress) → all critical flows PASS
    Gate 9: EARS         → All acceptance criteria have passing tests

  (Numbering note: Gates 1–6 + EARS are orch-judge's canonical 7-gate set — EARS is
   orch-judge's Gate 7, shown here as Gate 9; Loki adds Architecture + E2E as the two
   extra checks. Same checks, Loki-local numbering. orch-judge.md remains the 7-gate authority.)
  If any gate fails: assign remediation task to eng-* persona → loop

Gate:    All 9 gates PASS

Checkpoint: sdlc-checkpoint.skill S06
```

### PHASE S07 — Security Review

```
Personas: ops-security (adversarial), eng-qa (verification)

ops-security Tasks:
  - security-audit.skill → OWASP Top 10 full scan
  - threat-model.skill → verify mitigations implemented
  - privacy-audit.skill → PII scan (if applicable)
  - ai-safety-guardrails.skill → Verify protection against prompt injection
  - compliance-review.skill → if regulated (SOC2/PCI/HIPAA)
  - Fill: templates/security/SECURITY_CHECKLIST.md
  - Document all findings in: docs/security/SECURITY_REVIEW.md

Acceptance:
  - SECURITY_CHECKLIST.md: all items ✓
  - No HIGH severity open findings
  - All MEDIUM findings have documented mitigations or accepted risks

Gate:    SECURITY_CHECKLIST passed + no critical CVEs

Checkpoint: sdlc-checkpoint.skill S07
```

### PHASE S08 — Human Review

```
Personas: prod-tech-lead (review prep), orch-judge (EARS compliance), prod-ethicist (safety)
Professional conduct: prod-ethicist applies professional-practice.skill (ACM/IEEE-CS
  Code of Ethics) for the human/ethics dimension of the review.

Prep:
  - prod-tech-lead generates review summary:
    - What was built (linked to SPEC acceptance criteria)
    - All ADRs made during implementation
    - All security findings and resolutions
    - Test coverage report
    - Any known limitations or deferred tech debt
  - orch-judge: final EARS compliance check
    - All requirements addressed? (DONE)
    - Any "Nice to Have" deferred with documented reason?

  - **Double Verification Protocol**:
    1. orch-judge verifies logic & specs (Automated)
    2. prod-tech-lead verifies code quality & patterns (Human-Proxy)
    3. prod-ethicist verifies final safety check (Safety)
  - Run **core/final-review.skill** (independent expert pass: correctness, security,
    observability, spec/golden-thread, cost, simplicity) — must be SHIP before the human gate.

Gate:    DOUBLE VERIFICATION + HUMAN APPROVAL REQUIRED
         This is a mandatory stop — no autonomous continuation.
         Human may request changes → loop back to S05 for specific tasks.

Checkpoint: sdlc-checkpoint.skill S08
```

### PHASE S09 — Staging Deployment

```
Persona: ops-devops (lead), eng-qa (smoke tests)

ops-devops Tasks:
  - deployment.skill → staging environment
  - Verify CI/CD pipeline passes
  - Run smoke tests against staging

eng-qa Tasks:
  - Verify critical user flows work in staging
  - Verify Restore from Backup (backup-recovery.skill) — Mandatory
  - Verify DLQ Consumption & Replay (queue-management.skill)
  - Check monitoring/alerting is configured
  - Run performance-audit.skill against staging

Gate:    All smoke tests GREEN + monitoring verified
         (If Critical: Failover Test PASS via reliability-engineering.skill)

Checkpoint: sdlc-checkpoint.skill S09
```

### PHASE S10 — Production Deployment

```
Persona: ops-devops (lead), ops-sre (reliability check)

Pre-deployment:
  - ops-sre: verify rollback plan is documented
  - ops-sre: verify monitoring/alerting will cover new features
  - ops-sre: confirm SLO thresholds are set

Deployment:
  - deployment.skill → production
  - Feature flags (if applicable): enable for canary %
  - Monitor for 15 minutes after deployment

Post-deployment:
  - ops-monitor: verify dashboards show normal metrics
  - Write deployment record to AUDIT_LOG.md

Gate:    Production healthy for 15+ minutes

Checkpoint: sdlc-checkpoint.skill S10
  - Update PROJECT_STATE.md: phase: S10, status: DONE (build loop complete; Day-2 begins)
  - Write completion summary to AUDIT_LOG.md
  - Archive SESSION_SNAPSHOT: S10_production.md
```

### PHASE S11 — Operate & Maintain (Day-2)

```
Personas: ops-sre (lead), ops-monitor, ops-incident, ops-cost
Tasks:    ops-sre:
            - Run observability-stack-setup.skill (metrics/logs/traces, dashboards, SLOs)
            - Run runbook-authoring.skill → fill templates/ops/RUNBOOK_TEMPLATE.md per service
            - Define on-call rotation; verify error budget policy against SLOs
            - Run dependency-lifecycle.skill (patch cadence, dependency upgrades, CVE triage)
            - Use feature-flag-management.skill to govern live flags (rollout/rollback)
          ops-monitor:
            - Watch dashboards/alerts; confirm SLO adherence; flag burn-rate breaches
          ops-incident:
            - Run incident response per runbook; capture timeline for blameless review (→ S12)
          ops-cost:
            - Monitor cloud/API spend vs budget; flag cost regressions and savings

Output:  docs/ops/RUNBOOKS/ (one per service)
         docs/ops/SLO_REPORT.md (SLO adherence + error-budget burn)
         docs/ops/DEPENDENCY_STATUS.md (patch/upgrade log, open CVEs)

Gate:    SLOs met + error budget healthy + no open critical CVEs + spend within budget
         (Recurring/steady-state phase — re-enters on every operational cycle.)

Checkpoint: sdlc-checkpoint.skill S11
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S11_operate.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S11, status: IN_PROGRESS (Day-2)
  - Log:    agents/memory/AUDIT_LOG.md → operational cycle recorded
```

### PHASE S12 — Evolve & Continuously Improve

```
Personas: prod-product-ops (lead), prod-pm
Tasks:    prod-product-ops:
            - Run retrospective.skill (blameless) → fill templates/core/PROJECT_RETROSPECTIVE_TEMPLATE.md
            - Review DORA + SPACE metrics; identify delivery/health bottlenecks
            - Plan tech-debt paydown; feed prioritized items back into S04 decomposition
            - Govern feature-flag lifecycle with feature-flag-management.skill (retire stale flags)
          prod-pm:
            - Run product-analytics.skill (funnels, retention, North-Star movement)
            - Design A/B experiments → fill templates/product/EXPERIMENT_PLAN_TEMPLATE.md
            - Translate insights into prioritized iterations (loop back to S00/S01 as needed)

Output:  docs/evolve/RETROSPECTIVE.md (blameless, action items)
         docs/evolve/EXPERIMENTS/ (A/B plans + readouts)
         docs/evolve/IMPROVEMENT_BACKLOG.md (tech-debt + analytics-driven bets)

Gate:    Retrospective actions logged + experiments have a decision (ship/iterate/kill)
         + DORA/SPACE reviewed. Improvements re-enter the loop (→ S00/S01/S04).

Checkpoint: sdlc-checkpoint.skill S12
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S12_evolve.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S12, status: IN_PROGRESS (Day-2)
  - Log:    agents/memory/AUDIT_LOG.md → improvement cycle recorded
```

### PHASE S13 — Decommission & Sunset

```
Personas: prod-pm (lead), ops-sre, biz-legal
Tasks:    prod-pm:
            - Run decommission-sunset.skill → fill templates/ops/DECOMMISSION_PLAN_TEMPLATE.md
            - Define deprecation policy + timeline; plan user comms / migration paths
          ops-sre:
            - Execute data retention/migration plan; archive data + final backups
            - Tear down infra safely (DNS, secrets, monitors); confirm no live dependents
          biz-legal:
            - Wind down licenses/contracts/vendor commitments; confirm compliance/retention

Output:  docs/sunset/DECOMMISSION_PLAN.md
         docs/sunset/DATA_RETENTION_AND_MIGRATION.md
         docs/sunset/USER_COMMS.md (deprecation notices, migration guidance)

Gate:    Deprecation policy approved + data retained/migrated/archived per policy
         + users notified + license/contract wind-down confirmed.

Checkpoint: sdlc-checkpoint.skill S13
  - THIS IS THE FINAL LIFECYCLE CHECKPOINT
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S13_sunset.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S13, status: DONE (system retired)
  - Log:    agents/memory/AUDIT_LOG.md → DECOMMISSION complete
```

## New mid-phase quality gates

These are lightweight gates inserted *between* existing phases. They do not renumber any
phase; they are checkpoints the orchestrator runs before advancing the adjacent phase.

- **S02.5 — Cost & Feasibility gate** (between S02 and S03): run financial-governance.skill
  to validate the proposed architecture against budget/unit-economics before committing to a
  spec. Gate: projected cost within approved envelope, or human-approved exception.
- **S04.5 — Parallelism / Dependency-feasibility gate** (between S04 and S05): build the task
  dependency graph by filling templates/core/DEPENDENCY_GRAPH_TEMPLATE.md; verify the
  `[PARALLEL]` groups are truly independent (no hidden edges, no cycles). Gate: DAG is acyclic
  and parallel batches are conflict-free before implementation starts.
- **S06.5 — Performance-regression gate** (after S06): run the benchmark suite and compare
  against the recorded baseline. Gate: no critical latency/throughput regression vs baseline,
  or a human-accepted, documented exception.
- **S07.5 — Sustainability gate** (after S07): produce a green-software report (energy/carbon
  per request, idle waste, efficiency hotspots). Gate: sustainability report reviewed; no
  unmitigated efficiency red flags.

---
