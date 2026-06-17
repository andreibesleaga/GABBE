# Agentic Design Patterns — Comprehensive Catalog

A scannable taxonomy of the design patterns and advanced techniques used to build autonomous
LLM-based agents. Each entry gives a one- or two-line description, **when to use** it, and the
GABBE skill (referenced by name in backticks) that implements or operationalizes it. Patterns are
grouped by the problem they solve; most real systems **compose** several of them.

This guide is a map, not an implementation. When an entry names a GABBE skill, that skill is the
load-bearing artifact — read it before building. Where no dedicated skill exists, the catalog itself
is the reference.

---

## How to read this catalog

Three meta-principles cut across every category below:

- **Start simple; add structure only when it pays for itself.** The cheapest correct system that
  meets the bar wins. A single well-prompted call beats a chain; a fixed chain beats an autonomous
  agent; reach for multi-agent only when one agent provably cannot hold the task. Every added
  pattern buys a property (accuracy, parallelism, auditability) and costs another (latency, tokens,
  surface area) — spend deliberately.
- **Workflows vs. agents.** A *workflow* is a predictable, pre-composed path through known steps
  (you wrote the control flow). An *agent* dynamically decides its own steps and tool calls at
  runtime. Workflows are easier to test, cheaper, and more auditable; agents are more flexible and
  handle open-ended tasks. Prefer the workflow when the steps are knowable in advance.
- **Reflection needs an external anchor.** Any self-critique loop that scores only its own opinion
  reinforces errors rather than fixing them. Pair every reflective pattern below with a deterministic
  check, a symbolic constraint, or an independent judge. See `agentic-patterns.skill` (grounded
  self-critique) and `llm-as-judge.skill`.

---

## (a) Reasoning patterns

Techniques that shape *how a single model thinks* before or while it answers. They trade extra
tokens/latency for accuracy on hard problems. Implemented and contrasted in `reasoning-patterns.skill`
and `sequential-thinking.skill`.

- **Chain-of-Thought (CoT)** — make the model lay out intermediate reasoning steps before the final
  answer. *Use when:* multi-step arithmetic, logic, or analysis where a one-shot answer is unreliable.
  *Skip when:* trivial lookups (it just adds latency). → `reasoning-patterns.skill`,
  `sequential-thinking.skill`.
- **Self-Consistency** — sample several independent CoT traces and take the majority answer instead
  of trusting one. *Use when:* a single trace is noisy and a verifiable/aggregable answer exists.
  *Cost:* N× tokens. → `reasoning-patterns.skill`; for the voting mechanics see
  `swarm-consensus.skill`.
- **Tree-of-Thoughts (ToT)** — explore reasoning as a branching tree, score partial branches with a
  value heuristic, and prune dead ends. *Use when:* problems with search/backtracking structure
  (puzzles, planning, proofs). *Cost:* high — many calls. → `reasoning-patterns.skill`.
- **Graph-of-Thoughts** — generalize ToT to a DAG so partial results can *merge*, not only branch.
  *Use when:* sub-results recombine (e.g. aggregating sub-summaries). → `reasoning-patterns.skill`.
- **ReAct (Reason + Act)** — interleave reasoning with tool calls: Thought → Action → Observation →
  repeat, so reasoning is grounded in real observations. *Use when:* the model needs external
  information or to act in an environment (search, DB, APIs). The default loop for tool-using agents.
  → `agentic-patterns.skill`.
- **Reflexion** — after a failed attempt, write a verbal self-critique into memory and retry with that
  lesson in context; the critique persists across attempts. *Use when:* tasks allow multiple attempts
  with a usable success/failure signal. *Anchor required* (see meta-principles). → `agentic-patterns.skill`
  (reflection), `episodic-consolidation.skill` (persisting the lesson).
- **Least-to-Most** — first decompose the problem into an ordered list of easier sub-problems, then
  solve them in sequence, each using earlier answers. *Use when:* the hard problem is really a chain of
  dependent easy ones; improves generalization to harder instances. → `reasoning-patterns.skill`.
- **Step-Back Prompting** — before answering, ask the model to derive the higher-level principle,
  abstraction, or general question, then reason from it. *Use when:* the model rushes to a specific
  wrong answer and a governing concept would steady it. → `reasoning-patterns.skill`.
- **Dual-Process (System 1 / System 2)** — wrap fast generative output (System 1) in a slower
  evaluative layer (System 2) that checks before committing. *Use when:* fast answers are usually
  right but occasional confident errors are costly. → `reasoning-patterns.skill`,
  `consciousness-loop.skill`.
- **Test-time compute scaling** — spend more inference compute (longer reasoning, more samples,
  verifier-guided search) on harder instances only. *Use when:* difficulty varies and you can detect
  it; route easy cases to cheap paths. → `reasoning-patterns.skill`, `cost-benefit-router.skill`.
- **Outcome vs. Process reward (ORM vs. PRM)** — grade only the final answer (ORM) versus grading each
  reasoning step (PRM). PRM catches "right answer, wrong reasoning" and prunes bad traces early.
  *Use when:* you can score steps; it is the antidote to lucky-but-unsound traces. → `agentic-patterns.skill`
  (per-step scoring), `cognitive-testing.skill`.

**When NOT to use heavy reasoning:** simple, well-specified, single-fact tasks; latency-critical paths;
cases where a deterministic tool already gives the answer. Heavy reasoning multiplies cost and can
*talk itself out of* a correct first answer.

---

## (b) Planning patterns

Techniques for turning a goal into an executable sequence of steps. Implemented via
`sequential-thinking.skill` and the orchestration skills.

- **Plan-and-Execute** — generate the full plan up front, then execute steps without re-planning each
  one. *Use when:* you want auditability and predictable cost, and the environment is stable enough
  that the plan won't go stale. *Trade-off:* less adaptive than re-planning every step. → `loki-mode.skill`,
  `multi-agent-orch.skill`.
- **Plan-Reflect (re-planning loop)** — execute a step, observe, and revise the remaining plan before
  continuing. *Use when:* the environment is dynamic or steps surface new information. *Trade-off:*
  more LLM calls, harder to audit. → `agentic-patterns.skill`.
- **Task decomposition** — split a large goal into independent or dependent sub-tasks with explicit
  inputs/outputs. The substrate under almost every multi-step pattern. *Use when:* any task too big
  for one focused context. → `multi-agent-orch.skill`, `context-engineering.skill`.
- **Hierarchical task networks (HTN)** — recursively decompose tasks into sub-tasks until each is
  directly executable, forming a tree of methods. *Use when:* domains with reusable decomposition
  recipes and clear sub-task boundaries. → `multi-agent-orch.skill`.
- **Plan-as-graph (DAG planning)** — represent the plan as a dependency DAG so independent branches run
  in parallel and ordering constraints are explicit. *Use when:* sub-tasks have a partial order with
  real parallelism to exploit. → `multi-agent-orch.skill`, `agent-workflow-patterns.skill`.
- **Planner / Worker / Solver factorization (ReWOO-style)** — a planner writes the whole tool-using
  plan once (with variable placeholders), workers execute tools, a solver composes the final answer —
  decoupling reasoning from observations so tool count doesn't blow up call count. *Use when:* many
  tool calls per task and you want to minimize reasoning-model invocations. → `agent-workflow-patterns.skill`.

---

## (c) Workflow patterns (the "effective agents" taxonomy)

Predictable, pre-composed control flows. These are the first thing to reach for — they are cheaper and
more reliable than autonomous agents and solve most problems. Fully operationalized in
`agent-workflow-patterns.skill`.

- **Prompt chaining** — decompose a task into a fixed sequence of LLM calls, each consuming the prior
  output, optionally with programmatic gates between steps. *Use when:* the task cleanly splits into
  ordered sub-tasks (e.g. outline → draft → polish). → `agent-workflow-patterns.skill`.
- **Routing** — classify the input, then dispatch it to a specialized prompt, tool, or model.
  *Use when:* distinct input categories are handled better separately, or to send easy cases to a
  cheap model and hard ones to a strong one. → `agent-workflow-patterns.skill`, `cost-benefit-router.skill`,
  `persona-selector.skill`.
- **Parallelization — sectioning** — split a task into independent subtasks run concurrently, then
  combine. *Use when:* parts are genuinely independent (e.g. analyze N documents). → `agent-workflow-patterns.skill`.
- **Parallelization — voting** — run the *same* task multiple times in parallel and aggregate (majority,
  any-flag, average). *Use when:* you need higher confidence or want diverse attempts (e.g. multiple
  reviewers for code, guardrail screening). → `agent-workflow-patterns.skill`, `swarm-consensus.skill`.
- **Orchestrator-workers** — a central LLM dynamically decomposes the task, delegates sub-tasks to
  worker LLMs, and synthesizes their results. Unlike sectioning, the sub-tasks are *not* known in
  advance. *Use when:* you can't predict the decomposition (e.g. multi-file code changes, open-ended
  research). → `multi-agent-orch.skill`, `agent-workflow-patterns.skill`.
- **Evaluator-optimizer** — one LLM generates, a second evaluates against a rubric and returns
  feedback, loop until the bar is met. *Use when:* you have clear evaluation criteria and iterative
  refinement measurably helps (translation, complex search, writing). *Anchor required.* → `agent-workflow-patterns.skill`,
  `llm-as-judge.skill`.

---

## (d) Multi-agent patterns

Topologies for coordinating multiple agents. The dominant trade-off and characteristic failure mode of
each is the deciding factor — see the decision matrix and failure-mode taxonomy in `multi-agent-orch.skill`.

- **Supervisor / hierarchical (hub-and-spoke)** — a supervisor decomposes, routes to workers, and
  integrates results. *Buys:* central control, auditability. *Costs:* supervisor bottleneck and
  *command distortion* down deep delegation trees. → `multi-agent-orch.skill`, `loki-mode.skill`.
- **Blackboard / peer-to-peer** — agents collaborate laterally through a shared state store with no
  central controller. *Buys:* fault tolerance, no single point of failure. *Costs:* poor observability,
  emergent loops/herding/deadlock. → `multi-agent-orch.skill`, `autonomous-swarm-patterns.skill`.
- **Debate** — multiple agents argue from different priors and a moderator/judge picks or synthesizes.
  *Use when:* contested or subjective questions where surfacing disagreement improves the answer;
  *use a different model family for the judge* to avoid correlated failure. → `swarm-consensus.skill`,
  `llm-as-judge.skill`.
- **Consensus / voting** — multiple agents answer the same question and the result is aggregated.
  *Buys:* accuracy on hard problems. *Costs:* N× tokens. Use *first-to-ahead-by-k* and discard
  structurally malformed votes. → `swarm-consensus.skill`.
- **Market / contract-net** — tasks are advertised and agents bid; the awarded agent binds to a
  computational contract (I/O schema, resource budget, eval metric) and may sub-contract. *Use when:*
  heterogeneous workers and tasks that must be matched by capability/cost, or workloads that exceed one
  context. → `multi-agent-orch.skill` (computational-contract delegation).
- **Round-robin / dispatcher** — cyclically distribute work across interchangeable stateless workers.
  *Use when:* throughput on independent units with no shared state. → `multi-agent-orch.skill`.
- **Swarm / handoff** — decentralized sequential control transfer: each specialist hands control to the
  next, no central supervisor. *Use when:* a pipeline of specialists where each fully owns its phase.
  → `autonomous-swarm-patterns.skill`, `multi-agent-systems.skill`.
- **Actor model (message-passing)** — isolated stateful actors with private state communicate only via
  async immutable messages, with "let it crash" supervision and dead-letter queues. *Use when:* you
  need fault isolation, location transparency, and resilient distributed coordination. → `actor-agent-frameworks.skill`,
  `multi-agent-systems.skill`.
- **Board / state-machine (kanban) coordination** — model the work as tasks moving through explicit
  states (todo → doing → blocked → awaiting-validation → done) on a shared board that is the single
  source of truth. *Use when:* you want observable, resumable, human-reviewable multi-agent work.
  → `multi-agent-orch.skill` (handoffs + HITL checkpoints).
- **Fan-out / fan-in** — spawn parallel workers, then aggregate their outputs in a single reducer.
  *Use when:* embarrassingly parallel sub-tasks (e.g. many searchers → one writer). → `agent-workflow-patterns.skill`,
  `multi-agent-orch.skill`.

**Coordination economics:** coordination overhead grows with agent count and there is a capability
saturation threshold beyond which adding agents *hurts*. The topology is the constraint — pick the
simplest one that fits and validate it empirically.

---

## (e) Memory & context patterns

Techniques for managing what the agent knows across time and what fits in the window now. Memory
*mechanics* live in the `brain/` skills; the *budget decisions* live in `context-engineering.skill`.

- **Write / Select / Compress / Isolate** — the four context-management strategies: persist durable
  state outside the window, retrieve just-in-time, compact long history, and split concerns across
  focused sub-agents. *Use when:* any agent whose task outgrows a single clean context. → `context-engineering.skill`.
- **Memory taxonomy (working / episodic / semantic / procedural)** — short-horizon scratch state; past
  experiences/interactions; facts and knowledge; learned how-to skills. *Use when:* designing what an
  agent should remember and where. → `working-memory.skill`, `episodic-consolidation.skill`.
- **Summarization / compaction** — compress message history into a running summary once it crosses a
  threshold, preserving decisions and constraints. *Use when:* long-running sessions approaching the
  context ceiling. *Keep a recovery path* — compaction is lossy. → `context-engineering.skill`.
- **Forgetting / decay as a first-class operation** — actively expire or down-weight stale memory rather
  than accumulating forever. *Use when:* unbounded memory growth degrades retrieval relevance. → `episodic-consolidation.skill`,
  `learning-adaptation.skill`.
- **RAG (retrieval-augmented generation)** — retrieve relevant external documents and condition the
  answer on them instead of relying on parametric memory. *Use when:* answers need current/proprietary
  facts with provenance. Evaluate it. → `knowledge-connect.skill`, `rag-evaluation.skill`.
- **Agentic RAG (Self-RAG / Corrective-RAG / Adaptive-RAG)** — let the agent decide *whether* to
  retrieve, judge retrieved quality and correct (re-query / fall back to web) when confidence is low,
  and route by question difficulty. *Use when:* retrieval quality is variable and a naive single-shot
  retrieve-then-answer is unreliable. → `knowledge-connect.skill`, `rag-evaluation.skill`.
- **GraphRAG / knowledge-graph memory** — retrieve over a structured graph (entities + relations)
  instead of flat chunks, enabling multi-hop and global questions. *Use when:* questions span many
  documents or need relational reasoning. → `knowledge-connect.skill`.
- **Skill acquisition / procedural caching (Voyager-style)** — distill successful solutions into named,
  vector-indexed, callable skills the agent reuses later. *Use when:* recurring sub-tasks worth
  amortizing into a growing skill library. → `self-evolving-skills` guide, `self-improvement.skill`.

---

## (f) Tool & environment patterns

How agents act on the world. The agent-computer interface quality matters as much as model quality.

- **Tool use / function calling** — expose typed, strictly-schema'd tools the model invokes with
  structured arguments. *Use when:* the agent must do anything beyond producing text. Design atomic,
  well-described, error-proofed tools. → `tool-construction.skill`, `agentic-patterns.skill`.
- **Parallel tool use / function-calling fan-out** — issue independent tool calls concurrently in one
  turn. *Use when:* multiple independent reads/queries with no ordering dependency. → `agent-workflow-patterns.skill`.
- **Code execution** — let the agent write and run code in a sandbox as its action space, rather than
  calling fixed tools. *Use when:* tasks needing arbitrary computation, data wrangling, or composition
  of operations. *Sandbox mandatory.* → `agent-sandboxing.skill`, `tool-construction.skill`.
- **Computer use / GUI control** — drive applications through screenshots and synthesized
  mouse/keyboard actions when no API exists; perceive → act → re-perceive. *Use when:* the only
  interface is a GUI; prefer API/tool calls whenever available (cheaper, more reliable). → `sensory-motor.skill`,
  `agent-sandboxing.skill`.
- **MCP (model context protocol)** — a standard protocol for exposing tools, resources, and prompts to
  agents over stdio/HTTP, so capabilities are pluggable and portable. *Use when:* you want
  interoperable, reusable tool servers instead of bespoke integrations. → `tool-construction.skill`,
  `agent-protocol.skill`.
- **A2A (agent-to-agent) protocol** — a standard for agents to discover each other (agent cards) and
  exchange tasks across organizational/runtime boundaries. *Use when:* federating agents built by
  different teams or in different stacks. → `agent-protocol.skill`, `agent-interop.skill`.
- **Tiered integration hierarchy** — prefer direct tool calls, then MCP gateways, then unified APIs,
  then A2A — climbing tiers only as interoperability needs grow. *Use when:* deciding how an agent
  should reach an external capability. → `tool-construction.skill`.

---

## (g) Reliability & safety patterns

Patterns that keep autonomous systems correct, bounded, and accountable. Most agentic failures are
reliability failures, not capability failures.

- **Grounded reflection (external anchor)** — never let a self-critique loop score only its own
  opinion; require a deterministic check, a symbolic constraint, or per-step scoring so the loop
  corrects errors instead of reinforcing them. *Use when:* any reflection/self-review loop. → `agentic-patterns.skill`,
  `cognitive-testing.skill`.
- **LLM-as-judge / generator-critic** — score outputs with a separate model against an explicit rubric,
  ideally from a different model family to avoid correlated blind spots. *Use when:* automated quality
  gating where deterministic checks can't fully cover the criteria. → `llm-as-judge.skill`.
- **Guardrails (input/output filtering)** — screen prompts and outputs for injection, jailbreaks,
  policy violations, secret leakage, and unsafe actions, ideally as a parallel voting check. *Use when:*
  any agent exposed to untrusted input or producing consequential output. → `ai-safety-guardrails.skill`,
  `prompt-injection-defense.skill`.
- **Human-in-the-loop (HITL)** — insert approval/revision checkpoints before consequential actions, with
  confidence-threshold gating so only uncertain or high-impact steps interrupt a human. *Use when:*
  irreversible or high-stakes actions; lower autonomy bands. → `multi-agent-orch.skill`,
  `human-agent-collaboration` guide.
- **Circuit breaker / loop bounding** — hard caps on iteration depth, token/wall-clock budget, and a
  quality-threshold exit so loops cannot spin forever or exhaust cost. *Use when:* every ReAct,
  reflection, planning, or consensus loop. → `agentic-patterns.skill`, `reliability-engineering.skill`.
- **Sandboxing / least privilege** — execute tools and code in isolated environments (filesystem,
  network, process, inference) with egress control and scoped credentials, so a vulnerable tool or
  injection has a contained blast radius. *Use when:* any agent that executes code, calls tools, or
  handles untrusted content. → `agent-sandboxing.skill`.
- **Provenance & audit trail** — tag every input with its source, treat re-read memory and upstream
  handoffs as untrusted data, and keep an append-only record of what the agent wrote/selected/did.
  *Use when:* multi-step or multi-agent systems needing forensic accountability. → `context-engineering.skill`,
  `traceability-audit.skill`.
- **Confused-deputy / poisoned-handoff defense** — prevent a privileged agent from being steered by a
  malicious user or a compromised upstream peer into actions it shouldn't take. *Use when:* any
  topology where privilege differs across agents. → `multi-agent-orch.skill`, `prompt-injection-defense.skill`.
- **Spectrum of autonomy** — treat autonomy as a tunable design variable (suggest → confirm → act),
  raising it only as trust and evals accumulate. *Use when:* deciding how much latitude to give an
  agent in production. → `self-optimize.skill`, `human-agent-collaboration` guide.

> Classical (non-agentic) software design & architecture patterns — GoF, layered/
> hexagonal/microservices/event-driven, DDD, enterprise integration — have their own
> catalog in the `software-design-patterns` guide. Agentic patterns sit on top of them.

---

## Composition cheat-sheet

| Goal | Reach for |
|---|---|
| One-shot answer is unreliable | CoT → self-consistency → ToT (in that order of cost) |
| Agent needs live data / to act | ReAct + tool use + sandbox |
| Steps are knowable in advance | a workflow (chaining / routing / parallelization) — not an agent |
| Decomposition is unpredictable | orchestrator-workers |
| Clear rubric, iteration helps | evaluator-optimizer + LLM-as-judge (external anchor) |
| Hard question, want confidence | consensus/voting or debate (different judge family) |
| Task outgrows one context | Write/Select/Compress/Isolate + sub-agents |
| Needs current/proprietary facts | (Agentic) RAG / GraphRAG + RAG evaluation |
| Irreversible / high-stakes action | HITL gate + circuit breaker + sandbox |

When in doubt, build the simplest version, measure it against an eval, and add a pattern only when the
eval shows you need it.
