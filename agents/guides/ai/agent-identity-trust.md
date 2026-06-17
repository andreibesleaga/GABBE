# Agent Identity, Authentication & Trust

## 1. Why Agent Identity Matters

When software only suggested actions to a human, the human's identity carried the accountability. Autonomous agents break that assumption: an agent that calls tools, moves money, edits records, or talks to other agents takes actions on its own that must be attributable, authorized, and constrained. If an agent shares a human's credentials or runs as an unscoped service account, you lose three things at once — you cannot tell *which* agent acted, you cannot limit *what* it was allowed to do, and you cannot revoke *just* that agent without breaking everything sharing the credential.

Agent identity exists to restore those properties: every agent gets its own attributable identity, granted least privilege, with actions logged against that identity. This guide complements the policy and least-privilege model used elsewhere in the kit and the defensive skills `prompt-injection-defense.skill` and `output-validation.skill`; identity is the layer that decides *who the agent is and what it may do*, while those skills decide *whether a given action is safe to perform*.

Honest note: this area is moving fast in 2026. The principles below are stable, but specific protocols, profiles, and product names are evolving — treat any concrete mechanism here as a current snapshot, not a settled standard, and re-check the live specs before depending on a detail.

## 2. The Core Principles

- **Attributable**: every action traces to one agent identity, not a shared human or service account.
- **Least privilege**: an agent holds only the scopes it needs for its current task, and no more.
- **Delegated, not assumed**: when an agent acts for a user, that authority is an explicit, scoped, revocable delegation — never an inherited copy of the user's full rights.
- **Short-lived**: capability is granted through short-lived, scoped tokens, so a stolen credential expires quickly and a compromised agent can be cut off fast.
- **Human-gated at the top**: high-impact, irreversible, or trifecta-complete actions require a human approval regardless of how well-authenticated the agent is.

## 3. OAuth-Style Authorization for Agents

The mainstream direction is to reuse the OAuth/OpenID authorization patterns the web already trusts, adapted so the *agent* is a first-class principal.

- **MCP resource-server authorization model**: in the Model Context Protocol, a tool/data server is treated as an OAuth-protected resource server. The agent (acting as the client) presents an access token; the server validates it against an authorization server and enforces the token's scopes. This separates *who issued trust* (the authorization server) from *who enforces it* (the resource server), so a tool never has to trust the agent's self-description — only a verifiable token.
- **Agent-to-agent (A2A) authentication**: when agents call other agents, each side authenticates the other as a distinct principal. Trust is mutual and scoped: the calling agent proves its identity and presents the scopes relevant to the request, and the receiving agent authorizes per-request rather than trusting the channel.
- **Scope discipline**: scopes should map to concrete capabilities ("read calendar", "send draft for approval") rather than coarse roles ("admin"), so the principle of least privilege is expressible in the token itself.

## 4. Know Your Agent (KYA) and Verifiable Identity

Borrowing from "Know Your Customer" in finance, "Know Your Agent" (KYA) is the idea that a system should be able to establish *what an agent is, who operates it, and what it is permitted to do* before trusting it.

- **Agent passports**: a portable identity document for an agent — who built and operates it, what model/version it runs, and what it is authorized to do — that a relying party can verify before granting access.
- **Verifiable credentials (VCs)**: cryptographically signed claims about an agent (its operator, its certifications, its allowed scopes) that the agent presents and a verifier checks without phoning home to the issuer.
- **Decentralized identifiers (DIDs)**: identifiers an agent (or its operator) controls independently of any single provider, used as the subject of those credentials so identity is not locked to one platform.

Together these let a receiving system make a trust decision based on *verifiable* claims rather than on the agent's unverified self-assertion — which an injected or impersonating agent could fabricate.

## 5. Signed Mandates and Delegation

The hardest case is an agent acting *on a user's behalf*. The user must be able to delegate narrow authority without handing over their identity.

- **Signed mandate**: a scoped, signed authorization that says "this agent may do *these specific things*, within *these limits*, until *this time*, on behalf of *this user*." It is cryptographically signed by the delegating party so the downstream resource can verify both the grant and its bounds.
- **Constraint binding**: mandates should bind concrete constraints — spending caps, allowed counterparties, allowed action types, expiry — so a compromised agent cannot exceed the delegation even if it tries.
- **Chained delegation**: when an agent sub-delegates to another agent, the chain must be verifiable and monotonic — a sub-agent can never hold more authority than the agent that delegated to it.

## 6. Tokens, Audit, and Human Gates

- **Short-lived scoped tokens**: prefer minutes-to-hours expiry with the narrowest scope per task. Refresh through the authorization server rather than minting long-lived bearer tokens that, if stolen, grant durable access.
- **Audit and attribution**: log every privileged action against the acting agent identity, the mandate it acted under, the scopes exercised, and the human who delegated. This is the record that makes an autonomous action explainable and an incident investigable.
- **Human-approval gates for high-impact actions**: irreversible, externally visible, high-value, or trifecta-complete actions require a human in the loop even when the agent is perfectly authenticated. Strong identity reduces *who* can act; it does not by itself make a consequential action safe — that judgment stays with a human. Pair these gates with `prompt-injection-defense.skill` so a manipulated-but-authenticated agent still cannot push a harmful action through unreviewed.

## 7. Failure Modes to Design Against

- **Confused-deputy**: an agent with legitimate authority is tricked (often via indirect injection) into exercising it for an attacker's goal. Mitigation: per-request authorization, narrow mandates, and human gates on high-impact actions — never trust intent inferred from untrusted content.
- **Credential sharing / over-broad service accounts**: collapses attribution and least privilege. Mitigation: one identity per agent, scoped tokens, no shared admin credentials.
- **Token replay and over-long expiry**: a leaked long-lived token grants durable access. Mitigation: short expiry, audience/scope binding, and revocation lists.
- **Spoofed or impersonating agents**: an attacker presents a fake agent identity to a peer. Mitigation: verifiable credentials / signed identities and mutual A2A authentication rather than trusting self-described identity.
- **Mandate scope creep**: an agent acts beyond the user's intended delegation. Mitigation: explicit constraint binding (caps, counterparties, expiry) enforced at the resource server, not just in the agent.

## 8. Adoption Checklist

- Each agent has its own attributable identity; no shared human or admin credentials.
- Tool/data access uses an OAuth-style resource-server model with scoped tokens, not embedded static secrets.
- Tokens are short-lived and scoped to the current task; refresh and revocation paths exist.
- User-delegated actions run under explicit, signed, constraint-bound mandates that downstream resources verify.
- Cross-agent calls use mutual authentication with each agent as a distinct principal.
- Where used, agent identity claims are verifiable (passports / VCs / DIDs), not self-asserted.
- Every privileged action is logged against the agent identity and the mandate it acted under.
- High-impact, irreversible, or trifecta-complete actions are gated behind a human approval regardless of authentication strength.
- Specifics are re-checked against current 2026 specs before being depended upon.
