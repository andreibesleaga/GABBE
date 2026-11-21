---
name: agent-workflow-patterns
description: Build LLM systems from composable workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and decide workflow vs. autonomous agent.
triggers: [prompt chaining, routing workflow, parallelization sectioning, orchestrator workers, evaluator optimizer, workflow vs agent, build effective agents, fan-out fan-in]
tags: [coordination, agents, workflow]
core: false
context_cost: medium
---
# Agent Workflow Patterns Skill

## Goal
Compose reliable LLM systems from a small set of predictable, well-understood workflow patterns, and
know when a fixed workflow suffices versus when a dynamic, autonomous agent is actually warranted. A
*workflow* is a path you wrote — the control flow is fixed and the LLM fills in steps; an *agent*
decides its own steps and tool calls at runtime. Workflows are cheaper, more testable, and more
auditable; agents are more flexible but harder to constrain and debug. The objective is to reach for
the simplest composition that meets the quality bar, add structure only when it earns its keep, and
escalate to a full agent only when no fixed workflow can express the task.

## Steps

1. **Decide workflow vs. agent first**
   - If you can enumerate the steps in advance, build a **workflow** — it will be cheaper, more
     reliable, and easier to test.
   - Choose an **agent** (dynamic control flow, open-ended tool use) only when the path genuinely
     cannot be predicted: the number/order of steps depends on intermediate results, or the task is
     open-ended (multi-file code changes, exploratory research).
   - Before either, check whether a single well-prompted call with good examples already clears the
     bar. Do not add orchestration that buys nothing.

2. **Prompt chaining — fixed sequence of calls**
   - Decompose the task into an ordered series of LLM calls where each consumes the previous output
     (e.g. outline → draft → polish; extract → transform → format).
   - Insert programmatic **gates** between steps (schema checks, validators) that can stop or reroute
     the chain before a bad intermediate propagates.
   - Use when accuracy improves by giving each call one simpler job; accept the added latency.

3. **Routing — classify then dispatch**
   - Classify the input, then send it to a specialized prompt, tool, or model tuned for that category
     (e.g. refund vs. technical-support queries; easy vs. hard reasoning).
   - This is the natural place for cost routing — send easy cases to a cheap model and hard ones to a
     strong one. Defer the cheap-vs-capable decision to `cost-benefit-router.skill` and persona
     dispatch to `persona-selector.skill` rather than hard-coding it here.
   - Use when distinct input classes are handled better in isolation than by one do-everything prompt.

4. **Parallelization — sectioning and voting**
   - **Sectioning**: split into independent subtasks run concurrently, then combine (e.g. analyze N
     documents, or run a guardrail check alongside the main task).
   - **Voting**: run the *same* task multiple times in parallel and aggregate — majority, any-flag, or
     average. Use any-flag for safety screening (one reviewer raising a flag is enough); use majority
     for accuracy. For the aggregation/quorum mechanics defer to `swarm-consensus.skill`.
   - Use when subtasks are genuinely independent or when multiple looks raise confidence; budget the
     N× token cost.

5. **Orchestrator-workers — dynamic decomposition**
   - A central LLM decomposes the task *at runtime*, delegates sub-tasks to worker LLMs, and
     synthesizes results. Unlike sectioning, the sub-tasks are not known in advance.
   - Use when you cannot predict the decomposition. For role design, topology selection, handoff
     contracts, and failure-mode mitigations defer to `multi-agent-orch.skill`; this skill owns the
     decision to *use* the pattern, that skill owns *how* to wire it.

6. **Evaluator-optimizer — generate, critique, refine**
   - One call generates; a second evaluates against an explicit rubric and returns actionable feedback;
     loop until the bar is met.
   - Use only when you have clear evaluation criteria and iterative refinement measurably helps
     (translation, complex search, structured writing).
   - The evaluator MUST be externally anchored — pair it with a deterministic check (test/lint/schema)
     and a rubric-based judge per `llm-as-judge.skill`; never let the loop grade only its own opinion
     (see `agentic-patterns.skill`, grounded self-critique).

7. **Bound and compose**
   - Compose patterns freely (route → chain → vote) but keep every loop bounded: max iterations, a
     token/wall-clock budget, and a quality-threshold exit so it stops at good-enough.
   - Start with the smallest composition, measure against an eval, and add a pattern only when the eval
     shows the gap.

## Constraints
- NEVER reach for an autonomous agent when the steps are knowable in advance — use a workflow.
- NEVER add a pattern that does not measurably improve the eval; complexity is a cost, not a feature.
- Do NOT re-implement topology selection, consensus quorum, cost routing, or judging here — reference
  `multi-agent-orch.skill`, `swarm-consensus.skill`, `cost-benefit-router.skill`, and
  `llm-as-judge.skill` and own only the workflow-composition decision.
- Every evaluator-optimizer loop MUST have an external anchor and a hard termination cap.
- Parallel voting must account for its N× token cost explicitly, not assume it is free.

## Output Format
A workflow design containing:
- **Workflow-vs-agent verdict**: which, and the evidence (are the steps knowable?).
- **Pattern composition**: the chosen patterns and how they nest (e.g. route → chain[3] → vote[5]).
- **Per-step contract**: input/output shape and the programmatic gate between each step.
- **Routing table** (if routing): input class → target prompt/tool/model.
- **Aggregation rule** (if voting): majority / any-flag / average, and quorum.
- **Termination**: max iterations, token/time budget, and quality-threshold exit per loop.
- **Eval hook**: the metric used to justify each added pattern.

## Limits and safety
- Check a routing classifier's output against a fixed list of routes. A privileged route needs its own authorization check, whatever the classifier said.
- Give every loop and fan-out a maximum number of iterations, a token or time budget and a worker cap; stop and report when one is reached.
- Give each worker only its own slice of the data; remove secrets from payloads between steps.
- Carry the user's intent and active constraints through every hop and repeat them before any step that changes something.
