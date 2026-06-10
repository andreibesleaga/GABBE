# Human–Agent Collaboration Principles

> The most important interface GABBE has is the one between the **human** (the
> developer / engineer / architect) and the **agent** (Claude Code, Cursor,
> Antigravity, OpenCode, a raw LLM…). This guide makes that interface a
> first-class design concern, not an afterthought.

## Why this matters
Autonomy is only trustworthy when the human keeps an **accurate mental model** of
what the agent is doing. No amount of capability is safe if the human cannot tell
what the agent is trying to do, how it is doing it, or how to intervene. A good
collaboration interface is the quality bar for "fully working in the best ways."

## The three questions the human must always be able to answer
Drawn from ordinary mental-model and system-legibility principles, a well-behaved
agent keeps three questions answerable at every step:

| Facet | Question | GABBE's obligation | Satisfied in GABBE by |
|---|---|---|---|
| **Purpose** | "What is this for?" | Bound the agent's job — its domain, goals, and explicit **non-goals**. A "do anything" agent creates friction and false expectations. | CONSTITUTION scope + project-specific articles; the S01 Requirements gate / spec (`spec-driven`). |
| **Transparency** | "How is it working?" | Make reasoning, tool selection, and self-correction legible — never operate invisibly. | **Observability** (decision/span trace, token + cost attribution, `audit-trail`/`agent-analytics`, `AUDIT_LOG.md`). |
| **Control** | "How do I steer it?" | Provide affordances to **intervene** — pause, inject constraints, correct a plan, approve/reject high-stakes actions. | Human-in-the-Loop gates (AGENTS.md §9), the `GABBE_AUTONOMY` posture, `clarify.skill`. |

## The collaboration stance: manager, not operator
The healthiest division of labour is for the human to act as a **manager** and the
agent as a **delegate**:

> *delegate the objective → observe progress → intervene on exceptions.*

This implies an **asynchronous, observable surface** — a synchronous
request/response UI for a ten-minute agent task forces the wrong mental model.
GABBE's observable surface (memory logs + the audit/decision trace + the task/gate
board in `project/TASKS.md`) is what makes delegation trustworthy. The three parties
of the collaboration are:

- **Human = manager / delegator** (developer, engineer, architect) — sets the
  objective, reviews at gates, handles exceptions.
- **Agent = delegate** — executes the AGENTS.md operating loop / RARV cycle.
- **The observable shared surface = the connective tissue** — memory, audit
  trace, and the task/gate board that keep the human's mental model accurate.

## How GABBE operationalizes it
- **Purpose** → keep scope and non-goals explicit (CONSTITUTION + spec); the
  architect persona bounds what the agent is and is *not* to do.
- **Transparency** → observability is non-negotiable (every run traced; see the
  Observability mandate in AGENTS.md §5 and CONSTITUTION Article VI).
- **Control** → HITL gates + autonomy levels (L0–L3, `self-optimize.skill`) scale
  intervention frequency to the autonomy the human has granted.

## Final-review checklist (apply at integrity-check / S08)
A change is only "done" when all three facets hold:
- [ ] **Purpose** — scope/non-goals are explicit; the work maps to a spec/requirement.
- [ ] **Transparency** — the run is traced and legible (decisions, tools, cost) — no black box.
- [ ] **Control** — the right HITL gates fired for the autonomy level; high-stakes/irreversible actions were human-approved.
