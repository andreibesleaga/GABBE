# How GABBE Self-Evolves: The Gene Pool and the Reward Loop

GABBE includes a small, real, self-improving loop for its own prompts. This guide explains
exactly what that loop is, what part of it is working code, and what part of it is conceptual
framing — because the difference matters and overclaiming it would be dishonest.

## The short, honest version

GABBE evolves its prompts with an **epsilon-greedy bandit over prompt variants, rewarded by a
success rate**. That is the whole mechanism. The code that does this lives in `gabbe/brain.py`.
Around that mechanism sits a richer vocabulary — "Active Inference", "minimize free energy",
"Meta-Cognitive Brain" — which is **framing, not math**. There is no free-energy functional
being minimized anywhere in the code. When you read "Active Inference" in the brain prompts,
read it as an intent ("think before acting, prefer actions that reduce surprise about project
state"), not as an implemented variational-inference algorithm. Being clear about this is the
point of the guide.

## The gene pool (real code)

Each evolvable prompt is a **gene**. A gene is a row in the `genes` table with at least:

- `skill_name` — which prompt this gene is a variant of (e.g. `brain-activate`)
- `prompt_content` — the actual prompt text
- `generation` — how many mutation rounds produced it (0 is the seed)
- `success_rate` — its accumulated fitness, a float that only ever goes up, capped at 1.0

A "gene pool" is therefore just all the rows for a given `skill_name`: several competing
prompt variants of the same skill, each with its own fitness so far.

## Selection: epsilon-greedy (real code)

When the brain needs a prompt, `_get_best_gene()` picks one with a classic epsilon-greedy
policy:

- **80% of the time (exploit):** take the gene with the highest `success_rate`, breaking ties
  by newest `generation`.
- **20% of the time (explore):** ignore fitness entirely and take the newest generation, so a
  freshly mutated variant gets a chance to prove itself even though its `success_rate` is still 0.

That 20% exploration rate is a literal `if random.random() < 0.2` in the code. This is a
multi-armed bandit, not a search over a fitness landscape with crossover — there is no
crossover and no population culling. It is deliberately simple.

## Reward: monotonic success rate (real code)

The loop closes in `activate_brain()`. The flow is:

1. Read project state from the database (counts of TODO / IN_PROGRESS / DONE tasks). This is
   the "Observation" step.
2. Fetch the best gene for the `brain-activate` skill and use its `prompt_content` as the system
   prompt. If no gene exists, fall back to a hard-coded default prompt.
3. Call the LLM through the gateway to get a suggested next action.
4. **If the call produced a result, reward the gene** that produced it: `_update_gene_success_rate()`
   does `success_rate = MIN(1.0, success_rate + 0.1)`.

So "reward" here means: a gene that yields a non-empty LLM response gets +0.1 fitness, up to a
ceiling of 1.0. It is **monotonic** — fitness never decreases. Be honest about what this implies:
the reward signal is "the call returned something", not "the suggested action was actually good".
There is no human-judged or outcome-judged reward feeding back in yet. A gene that reliably
produces *plausible* output will climb to 1.0 regardless of whether its suggestions were wise.
This is a genuine limitation, not a hidden feature.

## Mutation: Evolutionary Prompt Optimization (real code)

New genes are born in `evolve_prompts(skill_name)`, labeled in the code as **EPO (Evolutionary
Prompt Optimization)**:

1. Fetch the current best gene for the skill (or seed a generic default if the pool is empty).
2. Ask an LLM, acting as an "Expert Prompt Engineer", to rewrite that prompt to be more
   effective, precise, and robust.
3. Insert the rewrite as a new gene at `generation + 1`, with `success_rate` starting at 0.0.

So mutation is **LLM-driven rewriting**, not random token perturbation or genetic crossover.
A new generation starts unproven (fitness 0) and only earns fitness through the explore path of
selection plus the reward loop above. Over repeated `gabbe brain activate` runs, the genes that
keep producing results accumulate fitness and get exploited more often.

## Putting the loop together

```
evolve_prompts()      → adds a new, unproven prompt variant (generation+1, fitness 0)
        │
        ▼
activate_brain()      → epsilon-greedy picks a gene (80% best, 20% newest)
        │               → runs it through the LLM via the gateway
        ▼
_update_gene_success_rate()  → +0.1 fitness if the call returned something (capped at 1.0)
        │
        ▼
(next activate_brain) → the now-fitter gene is more likely to be exploited
```

Run `evolve_prompts` occasionally to inject variation; run `activate_brain` repeatedly to let
selection and reward sort the variants. That is the entire self-evolution mechanism.

## The "brain inference via skills" framing, stated honestly

GABBE's headline framing is that its intelligence "lives in the skill markdown" and that the
brain performs "Active Inference". Here is the honest accounting:

- **What is real:** the epsilon-greedy gene selection, the LLM-driven mutation, and the
  monotonic success-rate reward are all working Python in `gabbe/brain.py`, backed by a SQLite
  `genes` table. The markdown skills are real and are what an agent actually loads and follows.
- **What is conceptual:** "Active Inference" and "minimize free energy/surprise" are *names for
  an intent* placed in the default brain system prompt. No variational free energy, generative
  model, or belief-updating math is computed. Treat these terms as a design philosophy ("predict
  the likely outcome of the current trajectory, then pick an action that reduces uncertainty
  about project state"), not as an implemented algorithm.

If you describe GABBE to others, the truthful claim is: *"a self-improving prompt loop using an
epsilon-greedy bandit with a success-rate reward, plus LLM-driven prompt mutation."* The truthful
claim is **not** "it performs active inference" or "it minimizes free energy mathematically".

## How the meta-optimize and self-improvement skills fit

Two skills give an agent a CLI-free way to drive the same loop by following markdown instead of
running Python:

- `meta-optimize.skill` (in `coordination/`) is the agent-prompt analogue of `evolve_prompts`:
  it asks the agent to critique and rewrite a prompt/skill, producing the next-generation variant
  by reasoning rather than by calling the `gabbe` CLI.
- `self-improvement.skill` (in `brain/`) frames the broader improvement intent — observe outcomes,
  propose a better prompt or process, and feed the result back — so the same evolutionary idea
  works in a pure-markdown runtime with no database.

Both are the conceptual, runtime-agnostic mirror of the concrete code in `brain.py`. The code
path is what gives you persistence and measurable fitness; the skill path is what lets the same
evolution happen inside any coding agent that can read markdown. Neither path adds free-energy
math — they both implement "try a variant, keep what works".

## What you can rely on

- The gene pool, epsilon-greedy selection, and monotonic reward exist and work.
- The reward currently means "the LLM call returned output", not "the output was good" — improving
  this (outcome- or judge-based reward) is open work, and you should not assume otherwise.
- "Active Inference" / "free energy" are framing words; there is no such computation in the code.
- The mutation step depends on an LLM call; with no API access, no new genes are produced.
