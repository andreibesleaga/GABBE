# ADR-[NNN]: [Title of Architectural Decision]
<!-- Architecture Decision Record — created by adr-writer.skill -->
<!-- Store in: docs/architecture/decisions/ADR-[NNN]-[slug].md -->

**Date:** [YYYY-MM-DD]
**Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-NNN]
**Deciders:** [names or roles — e.g., "Tech Lead, Backend Team"]
**Tags:** [database | authentication | api | frontend | infrastructure | security | performance]

---

## Context

<!-- What is the problem we're solving?
     What are the forces at play? (performance, security, team skills, cost, time)
     What is the current state (status quo)?
     Why does a decision need to be made NOW? -->

[2-5 sentences describing the situation and why this decision matters.]

**Current state:** [How things work today]
**Constraint(s):** [Non-negotiable constraints: budget, timeline, team expertise, existing system]

---

## Options Considered

### Option A: [Name]
<!-- Description: what is this option? -->
[Brief description]

**Pros:**
- [benefit 1]
- [benefit 2]

**Cons:**
- [drawback 1]
- [drawback 2]

**Source:** [Official docs, benchmark, team experience]

---

### Option B: [Name]
[Brief description]

**Pros:**
- [benefit 1]
- [benefit 2]

**Cons:**
- [drawback 1]
- [drawback 2]

**Source:** [Official docs, benchmark, team experience]

---

### Option C: [Name] (if applicable)
[Brief description]

**Pros:**
- [benefit 1]

**Cons:**
- [drawback 1]

---

## Decision

**We will use [Option X].**

Because:
1. [Primary reason — ties to constraint or requirement]
2. [Secondary reason]
3. [Supporting evidence — benchmark, official recommendation, team expertise]

---

## Consequences

### Positive
- [What improves as a result of this decision]
- [What becomes easier]
- [What risk is reduced]

### Negative
- [What trade-off or cost do we accept]
- [What becomes harder or more expensive]
- [What technical debt is introduced, if any]

### Neutral
- [Things that change but aren't clearly positive or negative]
- [Things teams need to learn or adapt to]

### Risks
- [Risk 1]: [how we mitigate it]
- [Risk 2]: [how we mitigate it or accept it]

---

## Y-Statement Summary

> For [context / who this decision serves]
> who need [goal or capability],
> [the chosen solution]
> is a [category: database, framework, pattern, approach]
> that [key benefit].
> Unlike [alternative],
> our solution [key differentiator].

**Example:**
> For the authentication team who need a stateless, scalable session mechanism,
> JWT with refresh token rotation
> is a token-based authentication approach
> that eliminates server-side session storage.
> Unlike session cookies,
> our solution works across multiple API servers without a shared session store.

---

## Links

- **PRD Reference:** [link to PRD where this decision is needed]
- **Related ADRs:** [ADR-NNN — links to related decisions]
- **Official docs:** [link to official documentation that informed this decision]
- **Implementation:** [link to PR or commit where this was implemented]

---

## Review

**Approved by:** [name, date]
**Implementation complete:** [Yes/No — date]
**Revisit date:** [When should we revisit this decision? e.g., "2026 Q1 when library v3.0 releases"]
