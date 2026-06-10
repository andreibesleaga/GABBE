# 2. Brain Mode uses an Active-Inference control loop

- Status: Accepted
- Date: 2026-06-10

## Context

GABBE's "Brain Mode" needs a principled way to decide, at each step, whether to
act locally (cheap heuristic / local model) or escalate to a remote SOTA model,
and how to learn from past project outcomes. A purely reactive prompt-chain does
not capture cost/benefit trade-offs or episodic memory.

## Decision

Brain Mode (`gabbe/brain.py`) implements an Active-Inference / OODA control loop:
Observe (read PROJECT_STATE, audit log, recent outputs) → Orient → Decide (route
local vs remote via a cost-benefit router) → Act, with evolutionary prompt
optimization ("genes" persisted in SQLite) and episodic memory recall. This is an
**experimental** runtime: it is documented as such and gated behind explicit
`gabbe brain` subcommands, never on by default.

## Consequences

- The cost router and budget/hardstop controls are first-class, not bolt-ons.
- Because it is experimental, claims in the README are marked Experimental and
  link to reproducible examples rather than implying production guarantees.
- The loop is deterministic enough to be replayed (`gabbe replay`) for audit.
