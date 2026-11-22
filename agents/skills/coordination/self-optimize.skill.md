---
name: self-optimize
description: Tune skill/guide/persona/model selection to the project for quality+cost; gabbe.config.json + autonomy levels + alignment.
triggers: [self optimize, optimize for project, tune selection, best for this project, project config, autonomy level, optimize quality cost, adapt to project]
tags: [coordination]
context_cost: medium
---
# Self-Optimize Skill

## Goal
Continuously tune *how* the system works to the **current project and task** — which skills/guides/templates/personas/model-tiers to use, how much to clarify, how much to spend — optimizing for best engineering principles, quality, and cost simultaneously. It reads the per-project policy (`project/gabbe.config.json`), applies the configured autonomy level, honors a 3-layer alignment hierarchy, and records every material decision so the optimization is auditable and reversible. This complements `coordination/meta-optimize.skill` (which improves the skills themselves); self-optimize improves the *selection and posture* for the project at hand.

## Project policy: `project/gabbe.config.json`
A runtime-agnostic file any agent reads (the optional `gabbe` CLI reads it too). All keys optional; sensible defaults apply. See `docs/SCHEMA.md`.
```json
{
  "autonomy": "hybrid",
  "budgets": { "max_cost_usd": 5.0, "max_tokens_per_run": 100000 },
  "model_tiers": { "cheap": "<model id>", "default": "<model id>", "sota": "<model id>" },
  "enabled_mcps": ["context7", "filesystem"],
  "registries": ["https://skills.sh", "google/skills"],
  "protected_files": ["pyproject.toml", "package.json", "*.lock", "Dockerfile", ".github/**"]
}
```

Name no product as a routing rule: use the cheapest model tier that passes the task, and ask the human before the top tier. The `model_tiers` values are the project's own model ids.

## Autonomy levels (explicit)
The `GABBE_AUTONOMY` knob maps to concrete levels so behavior is predictable:

| Level | Posture | Behavior |
|---|---|---|
| **L0** | `ask` (suggest-only) | Propose actions; do nothing without explicit approval. |
| **L1** | `ask` | Ask before each non-trivial action, then act on approval. |
| **L2** | `hybrid` (default) | Act autonomously when cheap + reversible + unambiguous; ask for expensive/SOTA/irreversible/ambiguous. |
| **L3** | `auto` (act-and-report) | Act on cheap/reversible work silently and report; STILL pause for expensive/SOTA/irreversible/external-code actions. |

No level ever permits irreversible, SOTA-cost, or externally-sourced-code actions without human approval.

## Alignment hierarchy (macro → meso → micro)
Honor three layers; on conflict, **most-restrictive-wins**:
- **Macro (societal/legal):** laws and regulations (GDPR/HIPAA/EU AI Act), CONSTITUTION universal articles.
- **Meso (org):** team/org policy, `project/gabbe.config.json`, project-specific CONSTITUTION articles.
- **Micro (task):** the user's immediate request + this task's constraints.
A micro request may not override a macro/meso rule; escalate the conflict instead of resolving it silently.

## Steps
The optimization loop, run once per task:
1. **Read context:** task intent + `project/gabbe.config.json` + budget posture + the 00-index summaries (from `preflight.skill`).
2. **Select for quality×cost:** choose the skills/guides/personas/model-tier that meet the quality bar at the lowest cost (rank by relevance × 1/`context_cost`; tier models via `brain/cost-benefit-router.skill` and `coordination/persona-selector.skill`).
3. **Apply principles:** enforce the project's engineering principles (Constitution articles, SDLC gates) — never trade quality/security gates for cost.
4. **Conscience pass:** before any irreversible action, run a verification/self-critique pass (and human gate per the autonomy level).
5. **Record:** log the selection + rationale to `AUDIT_LOG.md`; version the active policy/ruleset so a later decision is reproducible.

## Constraints
- Optimize quality AND cost together — never sacrifice a quality/security gate, the lifecycle (S00–S13), or HITL escalation to save tokens (Article X).
- Most-restrictive-wins across macro/meso/micro; never let a task request override law/org/Constitution.
- Respect the configured autonomy level exactly; expensive/SOTA/irreversible/external-code actions always require approval.
- Record material selection decisions so optimization stays auditable + reversible.

## Output Format
```markdown
## SELF-OPTIMIZE — [task]
- Autonomy level: [L0–L3 / ask|hybrid|auto]
- Selected: skills=[…] guides=[…] persona=[…] model-tier=[cheap|default|sota]
- Alignment check: [macro/meso/micro — any conflict → escalate]
- Cost vs quality rationale: [one line]
- Logged to AUDIT_LOG.md
```

## Limits and safety
- Validate `project/gabbe.config.json`. On a malformed or unknown value fall back to the default (hybrid) and report it; never raise autonomy above what the human set.
- Optimization changes which skills and model tier are chosen, never the standards: no lower coverage threshold, skipped scan or removed gate.
- A task prompt cannot raise its own autonomy level; report such a request as a conflict.
- Take budget figures from the real config or usage records, not from the model's estimate. Record each selection in `AUDIT_LOG.md`.
