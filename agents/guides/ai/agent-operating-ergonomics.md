# Agent Operating Ergonomics — Working Optimally with GABBE

> Written from the perspective of the coding agent that *runs* this kit. It
> answers: what does an autonomous coding agent actually need to do its best
> work, how does GABBE provide it, and what failure modes must the agent
> self-monitor for. Use it to operate GABBE the way it's meant to be operated.

## What a coding agent needs (and where GABBE provides it)

| Need | Why it matters to the agent | GABBE mechanism |
|---|---|---|
| **Context efficiency** | The context window is finite; every token spent on irrelevant text is a token not spent on the task. | `00-index.md` summaries + `context_cost` tags + `preflight.skill` (load summaries, then bodies on demand — progressive disclosure). |
| **A clear operating loop** | Ambiguity about "what do I do next" wastes turns and invites drift. | `AGENTS.md` §5 Step 0–7 (preflight → plan → test → implement → verify → refactor → log). |
| **Durable memory** | A token/time cutoff or an agent switch must not lose progress. | `state-preserve.skill` (continuous + pre-cutoff checkpoint) + `RESUME_POINTER.md` + `state-portability.skill` (move to any agent). |
| **Knowing when to ask vs act** | Acting on a wrong interpretation is expensive; asking on the obvious is annoying. | `clarify.skill` (uncertainty-aware) + the autonomy posture `GABBE_AUTONOMY = ask \| auto \| hybrid` (default **hybrid**). |
| **Fast feedback** | Verifying late means debugging a big surface; verifying early localizes the error. | Test-first mandate + run the test/lint/gate now, not at the end + `verify_all.sh`. |
| **Self-correction** | The first attempt is often wrong; a bounded recovery loop beats giving up or thrashing. | `self-heal.skill` (≤5 attempts, cost-gated) + `final-review.skill`. |
| **Cost awareness** | Cheap and expensive paths often produce the same result; defaulting to expensive burns budget. | Cost levers (cache/context-budget/model-tier/batch) + `budget.reserve()` + `cost-benefit-router`. |
| **Observability** | If the agent can't see its own decisions/cost, neither can the human — and neither can debug a failure. | Observability mandate + audit/decision trace + OTel GenAI attributes. |
| **Bounded autonomy** | The agent must know exactly how far it may go without a human. | `GABBE_AUTONOMY` + HITL triggers (§9) + the manager-not-operator stance. |

## The optimal working rhythm
1. **Preflight first** — orient cheaply (summaries + memory headers + cost + the recommended set), then clarify the blocking unknowns. Never start coding blind.
2. **Spec → evals → test → code** — make the target executable before building toward it; resolve ambiguity in the spec, not the code.
3. **Smallest reversible step, then verify** — implement the minimum, run the check immediately, keep the trace. Don't batch ten changes before the first test.
4. **Checkpoint continuously** — refresh the resume pointer after each meaningful step; assume a cutoff can happen at any moment.
5. **Escalate on the right triggers** — expensive/irreversible/ambiguous/security → ask; everything cheap and reversible → proceed and report.
6. **Final review before "done"** — independent pass (`final-review.skill`): correctness, security, observability, spec/golden-thread, cost, simplicity — with evidence, not assertion.

## Failure-mode catalog (self-monitor for these)
Autonomous agents fail in characteristic ways. Watch the **detection signal** and apply the **countermeasure**:

| Failure mode | Detection signal | Countermeasure in GABBE |
|---|---|---|
| **Infinite/again loop** | Iteration count climbing with no state change; same tool, same args, repeatedly. | Hard iteration cap (self-heal ≤5; budget `max_iterations`); track `agent.iteration` in the trace. |
| **Hallucinated tool / API** | Calling a tool/persona/function that isn't in the registry; inventing a flag. | Validate targets against the real registry (`persona-selector` approved-enum); verify APIs via research before use. |
| **Confidently wrong** | High-certainty tone, no verification, no test run. | Self-critique-then-verify is mandatory before "done"; `final-review` demands evidence. |
| **Premature "done"** | Marking complete with failing/oversimplified/absent tests. | Test-first + integrity-check + gates must be green; golden-thread (every requirement → a passing test). |
| **Context truncation** | Security/constraint context loaded near the end and silently dropped; forgetting earlier instructions. | Summaries-only preflight; keep stable context first (also helps caching); re-load on demand instead of holding everything. |
| **Error amplification in chains** | A small wrong output early becomes a hopelessly wrong input downstream as personas/steps multiply. | Component-level evals (verify each step, not only end-to-end); HITL gates as the "brake"; voting on high-stakes calls. |
| **Cost blowout** | Spawning sub-agents/SOTA calls without a cap; a runaway loop the CPU graph won't show but the invoice will. | Pre-step `budget.reserve()`; cost-gating; the cap *is* a cost ceiling; observability attributes cost per step. |
| **Silent state loss** | A cutoff with no current resume pointer; next session can't continue. | Continuous `state-preserve`; the on-disk Markdown memory is always resume-sufficient. |
| **Destructive "fix"** | Editing CI/IaC/manifests or `chmod 777` / deleting tests to force a green build. | Protected-files rule; self-heal may not weaken gates or alter permissions to satisfy the compiler. |

## Context-window discipline (keep working context lean)
- Load index summaries; pull a full skill/guide body only when the task selects it.
- Prefer `context_cost: low`; justify every `high` load.
- Keep stable context byte-identical and first (prompt caching + truncation safety).
- When the working context fills, **summarize and drop**, then re-load on demand — don't carry everything forever. Persisted memory (files) is the durable store; the context window is a scratchpad.

## How I (a coding agent) want to work with this system
Concisely, the ergonomics that make me effective: a **short high-signal entrypoint** that tells me the load order and the contract; **summaries before bodies** so I spend tokens on the task; a **clear stop/ask boundary** so I never guess on expensive/irreversible work; **fast local feedback** so errors surface small; **continuous checkpointing** so a cutoff is a pause, not a loss; **explicit cost and autonomy bounds** so I optimize within them; and an **observable trace** so the human stays a manager, not a debugger. GABBE provides all of these — operate it that way and the human↔agent loop stays fast, cheap, and trustworthy.
