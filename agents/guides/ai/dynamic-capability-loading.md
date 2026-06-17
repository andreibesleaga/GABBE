# Dynamic Capability Loading: The Load-or-Ask Flow

GABBE is built so an agent does not need every capability pre-loaded. When a task needs something
the agent does not currently have — a skill, a piece of knowledge, an awareness of some new tool —
GABBE follows a defined **load-or-ask** flow: try to discover and load the missing capability from
known sources; if it genuinely cannot be resolved, fall back to asking the user. This guide
describes that decision flow end to end.

The governing principle is simple: **prefer loading over guessing, and prefer asking over
hallucinating.** An agent should never invent a capability it does not have. It either finds the
real one, or it asks.

## The trigger: a capability gap

A capability gap is detected when the current task requires something the agent cannot satisfy
with what is already in context — for example, the task needs a skill that is not in
`agents/skills/00-index.md`, or it depends on knowledge the agent does not hold, or it touches a
technology the agent is unsure is current. Preflight surfaces many of these gaps at session start;
others appear mid-task. Either way, the same resolution flow applies.

## The four discovery sources

GABBE resolves a gap by consulting four sources, roughly in order of locality (cheapest and most
trusted first):

1. **`skills-registry.skill` — import an existing skill.** The first question is always "does this
   capability already exist somewhere we can import?" The skills registry is the catalog of
   available skills and the mechanism for pulling one in. If the missing capability is a known
   skill (locally or in a registry GABBE can import from), this resolves the gap directly, with no
   new research needed. Always check here before reaching for the network.

2. **`update-scan.skill` — gated discovery of what is new.** If the capability is not already
   known, GABBE may need to discover whether it exists in the wider world. `update-scan.skill`
   performs this discovery as a **gated** action: it is allowed to look outward (for new tools,
   versions, or techniques) but only under the autonomy posture in effect — under `ask` it
   proposes the scan and waits; under `hybrid`/`auto` it may proceed within budget. The gating
   matters: discovery can cost tokens and pull in unvetted information, so it is deliberately not
   automatic and unbounded.

3. **`emerging-tech` — the tech radar.** When the gap is "is there a newer or better way to do
   this that I'm not aware of?", the `emerging-tech` skill acts as a tech radar: a curated view of
   adopt / trial / assess / hold technologies. It answers currency questions ("is this library
   still the right choice?", "has the recommended approach moved on?") so the agent can choose a
   current capability rather than a stale one.

4. **`knowledge-connect.skill` — RAG over connected knowledge.** When the gap is informational
   rather than tool-shaped — the agent needs *facts*, not a skill — `knowledge-connect.skill`
   retrieves from connected knowledge sources (retrieval-augmented generation). This grounds the
   agent in real, cited material instead of relying on parametric memory, which is exactly how a
   knowledge gap should be closed honestly.

These are complementary, not redundant: registry import answers "do we already have the skill?",
update-scan answers "does it exist out there?", emerging-tech answers "is what we'd use current?",
and knowledge-connect answers "what are the actual facts?".

## Preflight ranks the optimal set

Discovery typically surfaces *more* candidate capabilities than the task needs. Loading all of
them would bloat the context window and slow everything down. So selection is a ranking problem,
and `preflight.skill` performs it with an explicit objective:

```
rank candidates by:  task_relevance  ×  ( 1 / context_cost )
```

Each skill declares a `context_cost` (low / medium / high) in its frontmatter. Preflight prefers
high-relevance, low-cost capabilities and only pulls expensive (`high`) ones when the task truly
needs them. The result is the **smallest set of capabilities that covers the task** — load what
moves the needle, leave the rest indexed but unloaded. Index summaries are loaded cheaply; full
skill bodies are pulled only for the winners of this ranking.

## The fallback: ask the user

Discovery does not always succeed. The capability may not exist in any registry, the knowledge may
not be in any connected source, or the requirement itself may be ambiguous enough that no amount of
loading resolves it. When the gap is **unresolved after discovery**, GABBE does not guess and does
not fabricate a capability. It falls back to `clarify.skill`, which asks the user a focused,
batched set of questions — routed through whatever coding agent the user is driving (Claude Code,
Cursor, Copilot Chat, and so on). Asking is a first-class, expected outcome of this flow, not a
failure mode.

## The end-to-end decision flow

```
Task needs a capability the agent doesn't have
        │
        ▼
Is it an already-known skill?  ── yes ──▶  skills-registry.skill: import it
        │ no
        ▼
Discover whether it exists / is current:
   • update-scan.skill   (gated discovery — respects autonomy posture & budget)
   • emerging-tech       (tech radar — is the candidate current?)
   • knowledge-connect.skill (RAG — retrieve the actual facts, cited)
        │
        ▼
Found one or more candidates? ── no ──▶  clarify.skill: ASK the user (via the coding agent)
        │ yes
        ▼
preflight.skill ranks by  relevance × (1 / context_cost)
        │
        ▼
Load ONLY the winning minimal set (full bodies); proceed with the task
        │
        ▼
Still blocked / ambiguous mid-task? ──▶  clarify.skill: ASK the user
```

## Honest limits

- **Discovery is gated, not omniscient.** `update-scan.skill` only finds what its sources expose,
  and it runs under autonomy/budget gates — it will not silently scan the whole internet.
- **RAG is only as good as what is connected.** `knowledge-connect.skill` can only retrieve from
  sources that are actually wired up; an empty or stale knowledge base returns little, and the
  honest response there is to ask rather than to confabulate.
- **The ranking weights are heuristic.** `relevance × (1/context_cost)` is a sensible default, but
  relevance is an estimate; preflight can pick a suboptimal set, which is one reason clarify exists.
- **Importing a skill is not the same as vetting it.** A newly imported skill should still be
  reviewed before it is trusted for high-stakes work; discovery resolves availability, not safety.
- **Asking is the correct terminal state.** When nothing resolves the gap, falling back to
  `clarify.skill` is the designed-for outcome — silence or invention would be the bug.
