# Model Customization Decisions: Prompt Engineering vs RAG vs Fine-Tuning

## 1. What This Guide Decides

This is the **build-time** decision: given a task, how do you make a model good enough at it? The three primary levers — prompt engineering, retrieval-augmented generation (RAG), and fine-tuning — solve different problems, and reaching for the wrong one wastes time and money. This guide complements `cost-benefit-router.skill`, which handles the *runtime* local/remote routing decision; here we choose *how the model is customized in the first place*, before any request is routed.

Honest note up front: do not fine-tune prematurely. Most teams that think they need a fine-tune actually need a better prompt or better retrieval. Measure on your own evals (`eval-driven-development.skill`) before and after any change — a customization that does not move your eval numbers is cost without benefit.

## 2. The Decision Ladder

Climb the ladder in order. Stop at the first rung that meets your eval bar; only climb when you have measured that the current rung is insufficient.

1. **Start with prompt engineering.** Cheapest, fastest to iterate, no training pipeline. Clarify the instruction, add few-shot examples, structure the output, and decompose the task. A large fraction of "the model can't do this" problems dissolve here.
2. **Add RAG when the problem is *knowledge*.** If the model fails because it lacks fresh, proprietary, or long-tail facts — not because it lacks skill — give it the right context at inference time via retrieval. RAG keeps knowledge external, updatable without retraining, and citable. Use it for anything that changes (docs, policies, catalogs, tickets) or that the base model never saw.
3. **Fine-tune when the problem is *behavior, format, or latency*.** If the model knows the facts and has the context but still won't reliably produce the *style*, *structure*, *tone*, or *decision pattern* you need — or you need to bake a capability into a smaller, cheaper, faster model — fine-tune. Fine-tuning teaches *how* to respond, not *what* facts to know.

**Combine them.** These are not mutually exclusive. A common strong pattern is a fine-tuned model (for format/behavior and tool-calling reliability) that is fed retrieved context (RAG, for fresh knowledge) under a carefully engineered prompt. Prompt + RAG + fine-tune is the upper end, not three competing options.

## 3. When Each Is the Right Tool

| Symptom | Likely fix | Why |
|---|---|---|
| Output is close but wrong shape/tone | Prompt engineering | Instruction/format problem, not capability |
| Model lacks current or private facts | RAG | Knowledge is external and changes |
| Answers must be grounded and citable | RAG | Retrieval gives source attribution |
| Model knows facts but won't follow the pattern reliably | Fine-tune | Behavior must be learned, not instructed |
| Need a smaller/cheaper/faster model to match a big one on a narrow task | Fine-tune (often via distillation) | Specialize capability into a small model |
| Domain jargon or output schema the base model fumbles | Fine-tune | Format/behavior specialization |
| Task is broad and open-ended | Larger base model + prompt + RAG | Specialization would over-narrow |

## 4. Model Routing and Cascades

You rarely need one model for everything. Route by difficulty:

- **Cascade (cheap-first, escalate-on-low-confidence)**: try a cheap, fast model first; if its confidence or a verifier check is low, escalate the request to a stronger, more expensive model. Most traffic is easy and never escalates, so the average cost approaches the cheap model while quality on hard cases approaches the strong model.
- **Confidence signals**: use self-reported confidence, a verifier/judge pass, output-validation failure, or retrieval-grounding checks as the escalation trigger. Calibrate the threshold on your evals — too eager an escalation erodes the savings.
- **Relationship to runtime routing**: the cascade is the build-time *design*; the live cheap-vs-capable and local-vs-remote dispatch is owned by `cost-benefit-router.skill`. Design the cascade here, let the router execute it at runtime.

## 5. Small Language Models (SLMs) for Agentic Subtasks

In an agentic system, most steps are narrow: parse this, call that tool, classify this, extract those fields. Narrow steps rarely need a frontier model.

- **Why SLMs**: a small, specialized model is often roughly 10–30x cheaper per call and lower latency than a frontier model, and for a narrow, well-defined role (especially structured tool-calling and classification) it can match the big model's task quality after light fine-tuning.
- **Heterogeneous systems**: prefer a mix — SLMs for the high-volume narrow roles, a frontier model reserved for genuinely hard planning/reasoning steps. This is usually the dominant cost lever in an agent, because the narrow steps are the high-volume ones.
- **Fit check**: an SLM is a good fit when the role has a tight input/output contract and a clear eval; it is a poor fit for open-ended reasoning, long-horizon planning, or tasks where the failure mode is subtle.

## 6. Distillation and Quantization

- **Distillation**: train a small "student" model to imitate a large "teacher" (or the teacher's outputs) on your task distribution. This is the standard route to an SLM that punches above its size on a narrow task — you transfer the teacher's behavior into a cheaper-to-run model.
- **Quantization**: reduce the numerical precision of a model's weights (and sometimes activations) to shrink memory and speed up inference, typically with a small, measurable quality cost. Use it to fit a model on smaller/cheaper hardware or on-device.
- **Always re-measure**: both techniques trade some quality for cost/latency. The trade is only acceptable if it holds on *your* evals, not on a generic benchmark.

## 7. On-Device / Local Tradeoffs

Running a model locally or on-device buys privacy (data never leaves the device), offline capability, and zero per-call API cost — at the price of a capability ceiling (you can only run models that fit the hardware), upgrade friction, and the engineering cost of local serving. Local is attractive for privacy-sensitive, high-volume, or offline-required workloads, and is usually paired with quantized SLMs. The live local-vs-remote dispatch decision belongs to `cost-benefit-router.skill`; this guide's job is to decide *whether you have built a local-capable model worth dispatching to*.

## 8. Cost / Latency / Quality Tradeoff

| Approach | Setup cost | Per-call cost | Latency | Quality ceiling | Knowledge freshness |
|---|---|---|---|---|---|
| Prompt engineering | Very low | Base model rate | Base | Bounded by base model | Static (model's cutoff) |
| RAG | Low–medium | Base + retrieval | Base + retrieval | High on grounded facts | Live / updatable |
| Fine-tuning | High (training) | Often lower (smaller model) | Often lower | High on the trained behavior | Static unless paired with RAG |
| SLM (often distilled) | Medium | Very low (~10–30x cheaper) | Low | High on narrow role only | Static unless paired with RAG |
| Quantized / on-device | Medium | Near zero | Low–medium | Hardware-bounded | Static unless paired with RAG |
| Cascade (cheap→strong) | Medium | Near cheap-model average | Variable | Near strong-model on hard cases | Depends on members |

Note: the per-call and latency figures are directional — measure the actual numbers on your workload and hardware before committing.

## 9. Decision Checklist

- Have you exhausted prompt engineering before reaching for anything heavier? Most "model can't" problems are prompt problems.
- Is the failure a *knowledge* gap (→ RAG) or a *behavior/format/latency* gap (→ fine-tune)? Name it before choosing.
- Can a small or distilled model cover this narrow role at a fraction of the cost? Default agentic subtasks to SLMs.
- Have you designed a cheap-first cascade so frontier-model calls are the exception, not the rule?
- Did you re-run your evals (`eval-driven-development.skill`) before and after every customization, and confirm the change actually moved the numbers?
- For local/on-device, did you confirm the quantized model still clears your eval bar?
- Have you avoided fine-tuning until prompt + RAG were measurably insufficient?
