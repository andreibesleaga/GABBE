---
name: update-scan
description: Scans the kit, skill registries and the ecosystem for newer skills, tools, MCP servers or models and recommends or adopts them within cost and permission limits. Use at preflight, or when the human asks what is new or better.
triggers: [update scan, check for updates, new tools, better model, newer skill, whats new, self-evolve, upgrade, scan registry, better mcp]
tags: [core]
context_cost: medium
---
# Update-Scan Skill

## Goal
Keep the system current and self-evolving: detect what is new or better — in the local kit, in connected skill registries, and in the wider ecosystem (tools, MCP servers, models) — then **recommend or auto-adopt the best option per scenario**, always within the cost and permission bounds set by `GABBE_AUTONOMY`. This is the discovery engine behind the kit's self-evolution. It never adopts blindly: every candidate is validated and gated before it changes behavior.

Run it at preflight (Step 5 of `preflight.skill`) and on demand.

## Sources to scan
1. **Local kit** — new/changed `*.skill.md`, guides, templates, personas since the last preflight snapshot (count + names).
2. **Skill registries** — configured universal SKILL.md registries (Agent Garden / google-skills, skills.sh, Agensi, agent-skills-hub, awesome-agent-skills …). Import path + validation is owned by `skills-registry.skill`.
3. **Ecosystem** — newer best-practice tools, MCP servers, and models, discovered via `core/research.skill` (respect the Research Policy source tiers). Note SOTA/expensive options explicitly.

## Steps
1. Scan the three sources.
2. For each candidate run the decision loop below.
3. Report in the Output Format and log every decision.

## Decision loop (per candidate)
```
discover → evaluate → gate → adopt-or-recommend → log
```
1. **Evaluate** the candidate on: relevance to current/likely tasks, quality/provenance, `context_cost`, and expected cost/benefit vs the incumbent.
2. **Gate** on `GABBE_AUTONOMY` + budget:
   - `ask` → present a recommendation, do nothing until the user chooses.
   - `hybrid` (default) → **auto-adopt only when** the change is cheap, reversible, and clearly better; otherwise recommend + ask.
   - `auto` → adopt the best per scenario for cheap/reversible changes; still **ask** for anything expensive, SOTA, irreversible, or that pulls in externally-sourced code.
3. **Validate before adopt** (mandatory for anything external): `validate_skills` (frontmatter parses), slug/path-traversal checks, link + use-case validators, and a secret/egress + executable-content scan (see `skills-registry.skill`). Reject on any failure.
4. **Adopt or recommend**, then **log** the decision (candidate, evaluation, gate outcome, action) to `agents/memory/AUDIT_LOG.md`.

## Self-evolution paradigm (bounded)
The kit's evolution is **A2-style** — learn from *good* outcomes, not bad ones:
- Feed only **successful** trajectories into any evolved prompt/gene/skill refinement. **Exclude failed or known-bad trajectories** from the pool so the system cannot amplify its own mistakes (misaligned-replay guard).
- Treat reward as multi-objective: task completion AND cost-efficiency AND user acceptance — never optimize one into the ground.
- Prefer **canary/shadow** adoption with easy rollback for any evolved component; version it so a regression is reproducible and revertible (ties to `brain/learning-adaptation.skill`).
- Evolution itself is cost-gated: do not spend budget evolving when a cheaper static choice already meets the bar.

## Protected files (self-healing guardrail)
When self-healing or auto-adopting, **never edit** build files, IaC, CI/CD config, or dependency manifests (`package.json`, `pyproject.toml`, lockfiles, Dockerfiles, workflow YAML) **unless** the failure is specifically classified as dependency/build-related and the change is within the self-heal allowlist (AGENTS.md §8). Otherwise escalate. This keeps an auto-fix loop from silently rewriting the project's foundations.

## Self-Evolution Workflow (Git Branching)
Whenever the agent attempts to update its own core logic or configurations (`agents/`, `gabbe/`), the following strict workflow MUST be followed:
1. **Branching**: Never mutate files directly on the main branch. Work on a branch named `evolve/{feature-name}`; propose the `git switch -c` command to the human and run it only when asked.
2. **Analysis**: Scan the proposed changes for regression risks.
3. **Drafting**: Write the proposed changes on the isolated branch.
4. **Validation**: Run the test suite (`pytest` or equivalent) to ensure no core system failures.
5. **Review**: Submit the branch for human review (e.g., Pull Request) or wait for manual approval before merging.
> [!WARNING]
> Bypassing these steps risks unrecoverable corruption of the agent's capabilities.

## Output Format
```markdown
## UPDATE_SCAN

### Local kit
- New/changed: [names or "none"]

### Registries
- Candidates: [name → source → relevance/provenance] or "none configured"

### Ecosystem (tools / MCP / models)
- [candidate] — better than [incumbent] because [reason] — cost: [low/high/SOTA]

### Decisions (gated by autonomy=[ask|hybrid|auto], budget=[…])
- ADOPTED: [x] (cheap+reversible+validated)
- RECOMMEND (awaiting approval): [y] (expensive/SOTA/irreversible/external)
- REJECTED: [z] (failed validation: [reason])

> Logged to AUDIT_LOG.md
```

## Constraints
- Never adopt an externally-sourced skill/tool that fails validation — no exceptions.
- Never auto-adopt expensive / SOTA / irreversible changes; those always require human approval (AGENTS.md §9), even under `auto`.
- Never touch protected files outside the dependency-specific allowlist.
- Always log adoptions and recommendations to AUDIT_LOG.md so evolution is auditable and reversible.

## Limits and safety
- Every external candidate carries its source; one of unknown origin is quarantined and never adopted automatically.
- Validation (`validate_skills`, slug check, secret and egress scan) runs on every import; a request to skip it is declined.
- Do not touch build files, IaC, CI config or dependency manifests outside the dependency allowlist (AGENTS.md section 8).
- Take budget figures from the platform or the human, not from your own estimate; an expensive adoption always needs the human's yes.
- Learn only from successful runs; do not relax that rule without a human design decision.
