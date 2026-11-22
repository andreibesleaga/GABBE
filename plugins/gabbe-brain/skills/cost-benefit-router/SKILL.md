---
name: cost-benefit-router
description: "Chooses a local or remote model and a model tier for a task from complexity, privacy and context size. Use when asked to route a task, choose a model or cut cost, or when the task may involve sensitive data."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/cost-benefit-router.skill.md"
  tags: "brain"
  core: "false"
  context_cost: "low"
---
# Cost-Benefit Router

## Goal
> **Purpose**: Decide the most efficient execution path for a given task.
> **Philosophy**: "Don't use a cannon to kill a mosquito."

## Logic Flow

### Steps
## 1. Complexity Scoring (0–10 conceptual band)
This 0–10 banding is an illustrative conceptual scale; the actual `gabbe route` CLI scores
**0–100** against a single threshold and returns one `LOCAL`/`REMOTE` verdict. Analyze the prompt/task:
- **0-3 (Low)**: Typos, simple regex, one-line fixes, known boilerplate.
  - *Recommendation*: **LOCAL** (a small local model, or grep and sed).
- **4-7 (Medium)**: React components, API integration, unit tests, refactoring.
  - *Recommendation*: **HYBRID** (Draft Local -> Polish Remote) or mid-tier Cloud.
- **8-10 (High)**: System architecture, security review, complex debugging, creative writing.
  - *Recommendation*: the strongest tier you have (ask the human before using the top tier).

### 2. Context Analysis
- **Privacy Critical?** (PII, Credentials, Proprietary Core) -> **FORCE LOCAL**.
- **Context Size?** (>32k tokens) -> **REMOTE** (or Local with RAG).

### 3. Routing Table

| Score | Privacy | Context | Decision | Rationale |
|---|---|---|---|---|
| Low | Any | Low | **LOCAL** | Speed, Free, Good enough. |
| Med | Low | Med | **REMOTE (small tier)** | Fast, cheap cloud models. |
| Med | High | Any | **LOCAL (large)** | The largest local model available. |
| High | Low | High | **REMOTE (top tier)** | Needs the most capable model; ask the human first. |
| High | High | Any | **LOCAL (Max)** | Best available local quantization. |

## Usage

**Input**:
```json
{
  "task": "Fix a typo in README_FULL.md",
  "files": ["README_FULL.md"],
  "user_preference": "auto"
}
```

**Output**:
```json
{
  "route": "LOCAL",
  "model": "smallest local model",
  "reason": "Low complexity task, no reasoning required."
}
```

## Self-Adaptive Routing

> **Conceptual framing vs the actual CLI.** The implemented `gabbe route` command returns a
> **one-shot binary decision** (`LOCAL` / `REMOTE`) by scoring complexity on a **0–100** scale
> against a threshold, with a **PII/DLP override that forces `LOCAL`**. The richer behaviors
> described below — the multi-tier ladder, the **self-correction / escalation loop**, the
> per-task **heuristic updates**, and **autonomy-gating** (`ask`/`auto`/`hybrid`) — are
> *conceptual framing for how an agent should route work*, not features the one-shot CLI
> performs. Treat them as guidance for the orchestrator's own loop, and don't claim the router
> "guarantees" the optimal/cheapest path. See `guides/ai/self-evolving-skills.md`.

In GABBE the router is designed to behave self-adaptively end to end: it scores task **complexity**,
layers in **privacy** (a PII/DLP hit forces `LOCAL`, overriding any complexity score), and weighs
**context size** to pick the cheapest path that can still do the job. Conceptually it is gated by
autonomy level (`GABBE_AUTONOMY` = `ask` | `auto` | `hybrid`): `ask` confirms each route,
`auto` routes silently, `hybrid` auto-routes the safe cases and asks on the rest. The framing also
includes **self-correction** — when a `LOCAL` attempt fails, the orchestrator escalates up the tier
ladder to a remote model (re-checking privacy first) and updates its heuristics for next time —
though the bare `gabbe route` CLI returns only the single LOCAL/REMOTE verdict (the loop lives in
the calling agent).

## Self-Correction
If a routed task FAILS (e.g., Local model produces garbage):
1.  Log failure.
2.  **Escalate**: Retry with the next tier up (local, small remote, top tier), re-checking privacy first and asking the human before the top tier.
3.  Update heuristics.

## Constraints
- Privacy overrides complexity: sensitive data stays local.
- The cheapest tier that passes the task's checks wins; ask the human before the top tier.
- The 0-10 scale here is a conceptual guide; the CLI's `gabbe route` returns only LOCAL or REMOTE.

## Output Format
The JSON verdict shown under Usage: `route`, `model` (a tier, not a product name) and `reason`.

## Limits and safety
- Credentials, personal data and proprietary core code force LOCAL whatever the complexity score; repeat this check before every escalation to a remote model.
- Security, cryptography and access-control work goes to the strongest tier you have, not by line count; ask the human before the top tier.
- Do not edit the routing rules to loosen a privacy check without the human's yes.
- Choose by measured cost, latency and availability, not by brand preference.
