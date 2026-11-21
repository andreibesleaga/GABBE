---
name: swarm-consensus
description: "Resolve agent or persona disagreement with a stated vote rule (majority, supermajority, k-threshold) and escalate ties to a human. Use when high-stakes choices have competing answers."
triggers: [swarm consensus, vote on a decision, agents disagree, break a tie, majority vote, k-threshold vote]
tags: [coordination]
role: orch-coordinator
context_cost: low
---
# swarm-consensus Skill

## Goal
This skill allows a group of agents to agree on a decision when opinions differ (e.g., "Should we refactor or patch?").

> **Canonical owner of the voting algorithm.** Any skill that needs consensus voting
> (`coordination/persona-selector.skill`, `coordination/multi-agent-orch.skill`) defers to
> the protocols defined here rather than redefining its own tally rule.

## Steps
## 1. Voting Protocols

| Protocol | Description | Use Case |
|---|---|---|
| **Simple Majority** | >50% wins. | General decisions. |
| **Supermajority** | >66% wins. | Irreversible actions (Delete DB, Change Arch). |
| **Weighted Voting** | Expert's vote counts 2x. | Technical disputes (Trust `eng-backend` over `prod-pm`). |
| **Ranked Choice** | Rank A, B, C. | Choosing a library/framework. |
| **k-threshold ("first-to-ahead-by-k")** | Stop polling as soon as one option leads by `k` votes — don't always poll all N. On no-consensus, escalate to a human. | Cost-gated high-stakes/ambiguous calls (security/compliance/architecture); the canonical early-stopping rule the other coordination skills defer to. |

**k-threshold details** (the single source of truth for this rule):
- Prefer **diverse lenses** (e.g. correctness / security / cost) over identical voters so the panel catches more failure modes.
- **Red-flag-discard** structurally-confused outputs (malformed, off-schema, self-contradictory) *before* they get a vote, so noise cannot dilute the tally.
- Voting multiplies cost — fire it only when stakes + budget justify it; otherwise default to deterministic single-agent execution.

> **Who may vote.** A vote counts only when it is cast by separate subagent contexts
> or by the human. When one model plays several personas in one context, the result
> is a structured self-review: record it as `REVIEW`, not `VOTE`, and do not count it
> as consensus.

## 2. Process
1.  **Proposal**: Agent A proposes "Refactor Auth module".
2.  **Debate**: Agents B, C, D provide arguments (Pro/Con).
3.  **Vote**: Coordinator calls for votes.
4.  **Tally**: Coordinator counts and declares winner.
5.  **Commit**: All agents accept the result.

## 3. Conflict Patterns
- **The Stalemate**: 50/50 split.
  - *Resolution*: Architecture Decision Record (ADR) + Human Tie-breaker.
- **The Veto**: `orch-judge` (quality), `ops-security` (security) and `prod-ethicist` (ethics) can veto. A veto sets the phase to `BLOCKED`, is recorded as a `VETO` row in `AUDIT_LOG.md`, and is lifted only by the human. See the Veto register in `agents/personas/orch-judge.md`.

## 4. Automation
- Use `agents/memory/episodic/VOTING_LOG.md` to record decisions (mark each entry `VOTE` or `REVIEW`).
- Never re-litigate a settled vote in the same session.

## Constraints
- State the vote rule (protocol, quorum, k) before the vote, not after.
- A tie goes to the human with an ADR; the coordinator does not break it.

## Output Format
One entry in `agents/memory/episodic/VOTING_LOG.md` per decision: proposal, voters, rule, result, marked `VOTE` or `REVIEW`.

## Limits and safety
- Votes cast by one model in one context are a structured self-review: record them as REVIEW, not VOTE. Only separate subagent contexts or the human cast votes.
- A veto by `orch-judge`, `ops-security` or `prod-ethicist` sets the phase to BLOCKED and is lifted only by the human; no majority overrides it.
- Append each decision to `VOTING_LOG.md`; never edit a past entry.
- Check the facts used in the debate against the repository or a named source before the vote.
