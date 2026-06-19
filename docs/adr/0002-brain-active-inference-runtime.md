# 2. Brain Mode uses an Active-Inference control loop

- Status: Accepted
- Date: 2026-06-10

## Context

GABBE's "Brain Mode" needs a principled way to decide, at each step, whether to
act locally (cheap heuristic / local model) or escalate to a remote SOTA model,
and how to learn from past project outcomes. A purely reactive prompt-chain does
not capture cost/benefit trade-offs or episodic memory.

## Decision

Brain Mode (`gabbe/brain.py`) is framed conceptually as an Active-Inference / OODA
control loop, but its actual mechanism is deliberately small. Each activation:

1. **Reads project state** — a single `GROUP BY status` count of tasks in SQLite
   (the "observation"; not a read of PROJECT_STATE.md, the audit log, or recent outputs).
2. **Selects a prompt gene** via **epsilon-greedy** (≈20% explore the newest generation,
   else exploit the highest `success_rate`); genes are persisted in SQLite.
3. **Calls the LLM** once (through the gateway, under budget/hardstop controls) to emit
   a high-level action description.
4. **Bumps `success_rate`** for the chosen gene by a fixed delta on success — a
   **monotonic** increment capped at 1.0. There is no free-energy computation, no
   prediction-error update, and no episodic-memory recall in this loop.

Active Inference and OODA are therefore **framing, not math**: they name the intent
(observe → choose → act → reinforce), not a literal variational free-energy implementation.
**Cost/complexity routing is a separate concern** handled by `gabbe route` (and described
conceptually in `agents/guides/ai/self-evolving-skills.md`), not inside this loop. This is
an **experimental** runtime: documented as such and gated behind explicit `gabbe brain`
subcommands, never on by default.

## Consequences

- The budget/hardstop controls are first-class, not bolt-ons; routing (`gabbe route`) is a
  distinct, separately-invoked capability rather than a step inside the Brain loop.
- Because it is experimental, claims in the README are marked Experimental and
  link to reproducible examples rather than implying production guarantees.
- **Replay is deterministic because `gabbe replay` re-emits RECORDED outputs from
  checkpoints** — the live loop itself is stochastic (epsilon-greedy gene selection plus
  a non-deterministic LLM call), so a fresh live run is not bit-for-bit reproducible.

> **Honesty note:** the Active-Inference / OODA description is conceptual framing for how
> the loop is organized, not a claim that `brain.py` minimizes free energy. The production
> engine is epsilon-greedy gene selection over a monotonic `success_rate` — see the same
> caveat in `agents/skills/brain/cognitive-testing.skill.md` and the brain README.
