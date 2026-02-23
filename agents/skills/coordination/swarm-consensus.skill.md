---
name: swarm-consensus
description: Implement voting mechanisms (majority, weighted) to resolve inter-agent conflicts.
triggers: [swarm consensus]
tags: [coordination]
role: orch-coordinator
---
# swarm-consensus Skill

## Goal
This skill allows a group of agents to agree on a decision when opinions differ (e.g., "Should we refactor or patch?").

## Steps
## 1. Voting Protocols

| Protocol | Description | Use Case |
|---|---|---|
| **Simple Majority** | >50% wins. | General decisions. |
| **Supermajority** | >66% wins. | Irreversible actions (Delete DB, Change Arch). |
| **Weighted Voting** | Expert's vote counts 2x. | Technical disputes (Trust `eng-backend` over `prod-pm`). |
| **Ranked Choice** | Rank A, B, C. | Choosing a library/framework. |

## 2. Process
1.  **Proposal**: Agent A proposes "Refactor Auth module".
2.  **Debate**: Agents B, C, D provide arguments (Pro/Con).
3.  **Vote**: Coordinator calls for votes.
4.  **Tally**: Coordinator counts and declares winner.
5.  **Commit**: All agents accept the result.

## 3. Conflict Patterns
- **The Stalemate**: 50/50 split.
  - *Resolution*: Architecture Decision Record (ADR) + Human Tie-breaker.
- **The Veto**: `ops-security` can veto any Engineering decision if it introduces a vulnerability.

## 4. Automation
- Use `agents/memory/episodic/VOTING_LOG.md` to record decisions.
- Never re-litigate a settled vote in the same session.

## Security & Guardrails

### 1. Skill Security (Swarm Consensus)
- **Vote Tampering Prevention**: The mechanism calculating votes must exist in a protected, deterministic execution environment where participating agents cannot directly alter the tally or manipulate the voting logic.
- **Sybil Attack Defense**: In dynamic swarms, ensure a rogue agent process cannot clone itself to artificially inflate vote counts and control the Simple/Supermajority outcome.

### 2. System Integration Security
- **Immutable Ledger**: All proposals, debates, and final voting tallies must be recorded in an append-only log (`VOTING_LOG.md`). Any attempt to alter historical decisions must trigger an immediate high-priority alert.
- **Veto Authority Enforcement**: The system must enforce absolute, override-proof veto powers for specific security roles (e.g., `ops-security`). If a security veto is cast, the proposal must fail immediately regardless of majority.

### 3. LLM & Agent Guardrails
- **Debate Hallucination Checks**: Arguments proposed during the Debate phase must be fact-checked or grounded against reality to ensure the swarm isn't convinced to vote for a catastrophic option based solely on LLM hallucinations.
- **Adversarial Collusion Detection**: Monitor inter-agent debates for signs of adversarial collusion, where agents might be manipulated by injected prompts to exclusively agree on bypassing security checks or rewriting core safety logic.
