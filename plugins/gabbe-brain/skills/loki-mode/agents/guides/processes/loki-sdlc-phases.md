# Loki Mode — Detailed SDLC Phase Specifications (S00–S13)

> Referenced by `agents/skills/brain/loki-mode.skill.md`. This holds the full
> per-phase detail (personas, tasks, outputs, gates, checkpoints) so the skill
> stays under the activation-size budget. Loaded on demand during orchestration.
>
> The lifecycle has 14 phases, S00–S13. **S00 is the Day-0 strategy & discovery
> phase** that runs BEFORE S01, S01–S10 are Day 1 (build and ship), and **S11–S13
> are the Day-2 phases** (operate, evolve, sunset) that run AFTER S10 once the
> system is live.

## Lifecycle at a glance (canonical)

This table is the one source of truth for the phases, their lead personas, entry,
exit and gate. Every other file points here and does not keep its own copy.
Phase ids always have two digits (`S00`, `S13`). There are no half-numbered
phases: the old sub-gates after S02, S04, S06 and S07 (cost, parallelism,
performance, sustainability) are exit criteria of those phases.

| ID | Name | Day | Lead persona (support) | Main skills | Entry | Exit criteria | Gate | Artefacts |
|---|---|---|---|---|---|---|---|---|
| S00 | Strategy & Discovery | 0 | prod-research (prod-pm) | ideation-facilitation, user-research-synthesis, opportunity-assessment, market-analysis | Request received; `PROJECT_STATE` absent or `NOT_STARTED` | Problem statement, opportunity sized, North-Star and HEART metrics, RICE, GO/NO-GO recommendation | HUMAN: go / no-go | `docs/discovery/PROBLEM_STATEMENT.md`, `OPPORTUNITY_ASSESSMENT.md`, `MARKET_SCAN.md` |
| S01 | Requirements | 1 | prod-pm (prod-safety-engineer if safety-critical) | spec-writer, req-elicitation, req-review, ai-ethics-compliance, hazard-analysis, security-baseline, security-requirements | S00 GO, or a recorded "skip discovery" | PRD in EARS, every requirement testable, ambiguities closed, bias check done. Security tier confirmed by the human and recorded in project/SECURITY_BASELINE.md; security and privacy requirements written (security-requirements). | HUMAN | `docs/requirements/PRD.md`, `docs/requirements/EARS_REQUIREMENTS.md` |
| S02 | Architecture | 1 | prod-architect (ops-security) | arch-design, adr-writer, threat-model, error-handling-strategy, financial-governance | S01 approved | C4 model, ADRs, threat model, projected cost within the approved envelope. Assurance level chosen per component and recorded in `project/ASSURANCE_PLAN.md` (`assurance-ladder.skill`); the human approves any level above 1. Threat model and trust boundaries done for tier 2 and 3; every S02 row of project/SECURITY_BASELINE.md has an evidence path. | HUMAN | `PLAN.md`, `docs/architecture/C4_ARCHITECTURE.md`, `docs/architecture/decisions/ADR-NNN.md`, `docs/security/THREAT_MODEL.md` |
| S03 | Technical Spec | 1 | prod-tech-lead (prod-architect) | spec-analyze, api-design, event-governance | S02 approved | Spec covers every PRD criterion; API and schema contracts defined. Properties and invariants listed; where the assurance plan says level 2 or 3, the design model is checked. | prod-tech-lead (the human may review later) | `SPEC.md`, `docs/api/openapi.yaml`, `docs/db/schema-changes.md` |
| S04 | Task Decomposition | 1 | prod-tech-lead, orch-planner | decompose, estimation-sizing | S03 done | Atomic tasks, DAG acyclic, `[PARALLEL]` groups conflict-free | orch-judge | `project/TASKS.md` |
| S05 | Implementation | 1 | orch-planner with the eng-* personas | tdd-cycle, secure-coding, refactor, git-workflow, self-heal | S01–S04 checkpoints exist | All tasks DONE, each through the RARV verify step. Contracts, property tests and fuzz targets written at the chosen assurance level; frozen tests and specification files not edited by the implementer. | verify green | code, tests |
| S06 | Testing & Quality | 1 | eng-qa, orch-judge | integrity-check, final-review, eval-driven-development | S05 done | Quality gates G1–G9 pass, final-review = SHIP, no performance regression against the baseline. At the chosen assurance level: mutation-score floor met on changed code and the anti-cheating checks passed (evidence added to G1–G9; no gate replaced). Gate G5 evidence, secret scan and static analysis output saved under docs/security/evidence/; S06 rows of the baseline set. | orch-judge (veto) | `docs/quality/S06-quality-report.md` |
| S07 | Security Review | 1 | ops-security (eng-qa) | security-audit, security-baseline, threat-model, privacy-audit, ai-safety-guardrails, compliance-review | S06 pass | Checklist complete, no open HIGH finding, MEDIUM mitigated or accepted, sustainability report reviewed. For a level 3 proof: leak checklist and trusted base reviewed. Every control row of project/SECURITY_BASELINE.md has an existing evidence file (a row without one is a FAIL); open risks accepted only by the human. | HUMAN: security sign-off | `docs/security/SECURITY_REVIEW.md`, filled `templates/security/SECURITY_CHECKLIST.md` |
| S08 | Human Review | 1 | prod-tech-lead, orch-judge, prod-ethicist | final-review, professional-practice | S07 signed off | Review summary; double verification (orch-judge, prod-tech-lead, prod-ethicist); final-review = SHIP | HUMAN | review summary in the checkpoint |
| S09 | Staging | 1 | ops-devops (eng-qa) | deployment, backup-recovery, queue-management, performance-audit | S08 approved | Smoke tests green, restore from backup verified, monitoring verified | smoke tests green | staging record in `AUDIT_LOG.md` |
| S10 | Production | 1 | ops-devops, ops-sre | deployment, release-management | S09 green | The human says "deploy now" in that request, before the deploy; then health checks pass and the human confirms the observation window (15 minutes unless the plan sets another) has ended; rollback plan exercised or documented | HUMAN: "deploy now", then the automated health check | deployment record in `AUDIT_LOG.md` |
| S11 | Operate & Maintain | 2 | ops-sre (ops-monitor, ops-incident, ops-cost) | observability-stack-setup, runbook-authoring, dependency-lifecycle, incident-response | S10 live | SLOs met, no open critical CVE, spend within budget | recurring review | `docs/ops/RUNBOOKS/`, `docs/ops/SLO_REPORT.md`, `docs/ops/DEPENDENCY_STATUS.md` |
| S12 | Evolve & Improve | 2 | prod-product-ops (prod-pm) | retrospective, product-analytics, feature-flag-management | S11 cycle done | Retrospective actions logged, experiments decided, DORA and SPACE reviewed | recurring review | `docs/evolve/RETROSPECTIVE.md`, `docs/evolve/IMPROVEMENT_BACKLOG.md` |
| S13 | Decommission & Sunset | 2 | prod-pm (ops-sre, biz-legal) | decommission-sunset | The human decides to retire the system | Retention and migration done, users told, contracts wound down | exit criteria met (the human's decision is the entry) | `docs/sunset/*` |

**Human gates.** There are six, all hard stops: S00, S01, S02, S07, S08 and S10.
The agent does not advance past one until the human has answered. The record of a
human gate is one `AUDIT_LOG.md` row `HUMAN_APPROVED` with the phase, the date and
the human's words; a phase is not advanced without it. S03, S04, S05, S06, S09,
S11 and S12 are not human gates. S13 is entered only on the human's decision to
retire the system; that decision is its entry condition, not a seventh gate.

**Quality gates.** G1–G9 run at S06 and are defined in
`agents/personas/orch-judge.md`. Other files say "the quality gates G1–G9" and do
not keep their own list or count.

**Status words** for a phase: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`, `DONE`.
**Snapshot name:** `agents/memory/episodic/SESSION_SNAPSHOT/S<NN>_<name>.md`.

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

### PHASE S02 — Architecture

```
Personas: prod-architect (lead), ops-security (threat review)
Tasks:    prod-architect:
            - Write PLAN.md using C4 model
            - Define Error Handling Strategy (RFC 9457 Problem Details) using error-handling-strategy.skill
            - Create docs/architecture/C4_ARCHITECTURE.md
            - Write ADRs for all major decisions → docs/architecture/decisions/
            - Cost check: run financial-governance.skill to validate the architecture
              against budget and unit economics before the spec is written
          ops-security:
            - Review architecture for security concerns (adversarial)
            - Run threat-model.skill on critical components
            - Write THREAT_MODEL.md → docs/security/

Output:   PLAN.md, C4_ARCHITECTURE.md, ADR-001+, THREAT_MODEL.md

Exit:     C4 model, ADRs, threat model, and projected cost within the approved
          envelope (or a human-approved exception)

Gate:     HUMAN APPROVAL REQUIRED
          Present: architecture summary + threat assessment + cost check + (Safety Case if Critical)
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

Gate:    prod-tech-lead approves (with prod-architect review). This is not a human
         gate: the human may review the spec later, and the agent does not wait for it.

Checkpoint: sdlc-checkpoint.skill S03
```

### PHASE S04 — Task Decomposition

```
Persona: prod-tech-lead (with orch-planner)
Tasks:   - Read SPEC.md + PLAN.md
         - Decompose into atomic tasks (one concern, at most three files, one verifying
           test, about 15 minutes for an expert)
         - Fill templates/core/TASKS_TEMPLATE.md
         - Assign each task to the appropriate eng-* persona
         - Identify dependencies (DAG) AND Independent tasks; fill
           templates/core/DEPENDENCY_GRAPH_TEMPLATE.md
         - **Parallelism**: Mark independent tasks with `[PARALLEL]` tag

         - **Adaptive Check**:
           - *If Plan Complexity > High*: Inject `S02_DEEP_RESEARCH` (Consult KIs / Web)
           - *If Security Critical*: Inject `safety-scan` pre-check

Output:  project/TASKS.md with T-NNN IDs, status: TODO, tags: [PARALLEL] if applicable

Exit:    Tasks are atomic, the DAG is acyclic, and the `[PARALLEL]` groups are
         truly independent (no hidden edges, no cycles).

Gate:    orch-judge reviews task decomposition (not a human gate):
         - Are all tasks atomic (see the definition above)?
         - Does task coverage match SPEC acceptance criteria?
         - Are parallel groups correctly identified and conflict-free?

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
  - Check coverage against the rule in orch-judge.md (G3)
  - Run integration test suite
  - Identify any missing test scenarios from EARS acceptance criteria
  - Fill any gaps via tdd-cycle.skill
  - Score probabilistic quality via eval-driven-development.skill; interpret benchmark/
    A-B results with empirical-methods.skill (effect size, significance — not just averages)

orch-judge Tasks:
  - Run the quality gates G1–G9 exactly as defined in `agents/personas/orch-judge.md`
    (G1 lint, G2 types, G3 coverage, G4 integration, G5 dependency security,
    G6 complexity, G7 architecture fitness, G8 end-to-end, G9 EARS coverage).
    Do not keep a second list here. G7 and G8 may be recorded N/A with a reason.
  - If any gate fails: assign a remediation task to an eng-* persona → loop
  - Run the benchmark suite and compare it with the recorded baseline: no critical
    latency or throughput regression, or a human-accepted, documented exception.

Exit:    G1–G9 pass (or N/A with a reason), final-review = SHIP, no performance
         regression against the baseline.

Gate:    orch-judge (veto). Not a human gate.

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
  - Sustainability: produce a green-software report (energy and carbon per request,
    idle waste, efficiency hotspots) with green-software.skill

Acceptance:
  - SECURITY_CHECKLIST.md: all items ✓
  - No HIGH severity open findings
  - All MEDIUM findings have documented mitigations or accepted risks
  - Sustainability report reviewed; no unmitigated efficiency red flags

Gate:    HUMAN SIGN-OFF REQUIRED — hard stop
         Present the checklist, the findings and the sustainability report to the
         human. S08 may not start until the human has signed off (HUMAN_APPROVED row).

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

### PHASE S09 — Staging

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

### PHASE S10 — Production

```
Persona: ops-devops (lead), ops-sre (reliability check)

Human gate (before anything is deployed):
  - Ask the human for "deploy now". The approval must be in this request, after S09
    is green. Record it as a HUMAN_APPROVED row in AUDIT_LOG.md. No approval, no deploy.

Pre-deployment:
  - ops-sre: verify rollback plan is documented
  - ops-sre: verify monitoring/alerting will cover new features
  - ops-sre: confirm SLO thresholds are set

Deployment:
  - deployment.skill → production
  - Feature flags (if applicable): enable for canary %
  - Monitor for the observation window set in the S10 row

Post-deployment:
  - ops-monitor: verify dashboards show normal metrics
  - Write deployment record to AUDIT_LOG.md

Gate:    HUMAN "deploy now" BEFORE the production deploy (hard stop), then the
         automated health check: health checks pass and the human
         confirms the observation window (S10 row) has ended

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

Entry:   The human decides to retire the system. That decision is the entry
         condition for S13; it is not a seventh human gate.

Gate:    Deprecation policy approved + data retained/migrated/archived per policy
         + users notified + license/contract wind-down confirmed.

Checkpoint: sdlc-checkpoint.skill S13
  - THIS IS THE FINAL LIFECYCLE CHECKPOINT
  - Write: agents/memory/episodic/SESSION_SNAPSHOT/S13_sunset.md
  - Update: agents/memory/PROJECT_STATE.md → phase: S13, status: DONE (system retired)
  - Log:    agents/memory/AUDIT_LOG.md → DECOMMISSION complete
```
