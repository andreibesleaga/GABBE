# What Is Genuinely Novel in GABBE — and What Is Conceptual

This guide is a deliberately honest inventory. GABBE makes several distinctive design bets, and
some of them are backed by working code while others are aspirational framing on top of a simpler
reality. The goal here is to let a reader tell the two apart, because the value of an honest
inventory is exactly that it does not overclaim. For each idea you will find: the claim, what is
real and working, and what is conceptual or aspirational. There are no "best-in-class" or
"mathematically guaranteed" claims here, by design.

## 1. Brain inference via skills

**The claim.** GABBE's "intelligence" is not locked inside a binary; it lives in structured
markdown skills, and a meta-cognitive "brain" reasons over project state using Active Inference to
choose the next strategic action.

**What is real and working.** The brain loop in `gabbe/brain.py` genuinely reads project state
from a database, selects a prompt via an epsilon-greedy bandit over stored "genes", calls an LLM
to propose the next action, and rewards the chosen gene with a monotonic success-rate bump. The
skills themselves are real markdown that any coding agent can load and follow with zero CLI
dependencies — that runtime-agnostic part is genuine and is GABBE's most distinctive trait.

**What is conceptual / aspirational.** "Active Inference" and "minimize free energy/surprise" are
*framing words in a system prompt*, not implemented math. No free-energy functional, generative
model, or belief update is computed anywhere. The honest description is "an epsilon-greedy bandit
over prompt variants with a success-rate reward". Also, the current reward signal means "the LLM
returned output", not "the output was good" — so the loop optimizes for plausible responses, not
yet for verified-good decisions. (See `self-evolving-skills.md` for the full breakdown.)

## 2. Self-evolving genes

**The claim.** GABBE improves its own prompts over time through evolutionary optimization.

**What is real and working.** `evolve_prompts()` in `gabbe/brain.py` does perform Evolutionary
Prompt Optimization: it takes the current best prompt for a skill, asks an LLM to rewrite it more
effectively, and stores the rewrite as a new generation in a SQLite `genes` table. Selection
(epsilon-greedy, 80% exploit / 20% explore) and reward (+0.1 per successful use, capped at 1.0)
are working code. Over repeated runs, fitter prompts get used more.

**What is conceptual / aspirational.** This is a single-parent, LLM-rewrite mutation with a bandit
selector — there is **no crossover, no population culling, and no random genetic operators**, so
calling it "genetic/evolutionary" is a useful metaphor more than a literal genetic algorithm.
Fitness is monotonic and based on "did the call return something", so a prompt can reach maximum
fitness without ever having given good advice. Improving the reward to be outcome- or judge-based
is open work, not a shipped capability.

## 3. The runtime-agnostic markdown kit

**The claim.** The entire GABBE methodology — skills, personas, guides, templates — is portable
markdown that works inside any coding agent (Claude Code, Cursor, Copilot Chat, Windsurf, and so
on) with no runtime lock-in.

**What is real and working.** This is one of GABBE's strongest and most genuinely-true claims. The
skills, personas, and guides are plain structured markdown. An agent can follow them by reading
them; the optional `gabbe` Python CLI adds persistence, metrics, and enforcement but is not
required to use the methodology. The index files and frontmatter conventions make the kit
discoverable and selectable. Portability is real.

**What is conceptual / aspirational.** "Works in any agent" depends on the host agent actually
reading and honoring the markdown; weaker agents may ignore structure, skip gates, or not load the
right skills. The platform controls (budgets, hard stops, gates) are **markdown-enforced only**
unless the `gabbe` CLI is in the loop — i.e. in a pure-markdown runtime they are conventions an
agent is asked to follow, not guarantees the environment imposes. Treat cross-agent behavior as
"portable in principle, variable in practice".

## 4. The four-layer memory

**The claim.** GABBE gives agents durable, structured memory across sessions, organized in layers
(e.g. project state, continuity of past failures, episodic session snapshots, and an audit log).

**What is real and working.** The memory files exist and are used: `PROJECT_STATE.md` tracks the
current SDLC phase and last checkpoint, `CONTINUITY.md` records past failures to avoid repeating,
episodic `SESSION_SNAPSHOT` entries capture per-session state, and `AUDIT_LOG.md` is the minimum
authoritative trace. Preflight loads compact headers from these on activation, and checkpoints
write to them. This gives real cross-session continuity grounded in files on disk.

**What is conceptual / aspirational.** The "memory priming with decay" and "biologically-inspired
forgetting" described in the skills are a sensible retrieval *policy* expressed in markdown, not a
learned or statistically-decayed memory model — the agent is *asked* to weight by recency and
relevance, and honors that to the degree the host agent follows instructions. The richness of the
memory also depends on the agent diligently writing checkpoints; nothing forces it in a
pure-markdown runtime. So the structure is real; the discipline that fills it is convention.

## 5. The Loki swarm SDLC

**The claim.** "Loki mode" orchestrates a swarm of specialized personas through a phased software
lifecycle (S01–S10, plus Day-2 phases S11/S12), with gates and human checkpoints between phases.

**What is real and working.** The phase specifications (S01 Requirements through S10 Production
Deployment), the persona roster, the per-phase checkpoints that write to memory, and the
human-approval gates are all defined in the kit and are followed by an agent that loads them. The
phase validator even recognizes the extended Day-2 phases (S11/S12) as legitimate. The persona
specialization (each persona's Role / Does NOT / Context Scope / Outputs / RARV cycle) is concrete
and usable.

**What is conceptual / aspirational.** "Swarm" describes orchestrated *single-agent role-switching
and delegation guided by markdown*, not necessarily many autonomous agents running concurrently —
how much true parallelism happens depends entirely on the host runtime. The gates are as binding
as the host agent's willingness to honor them; without the `gabbe` CLI enforcing hard stops, a
phase gate is a strong instruction, not a hard barrier. The lifecycle is a genuinely well-specified
process; whether it executes as a literal multi-agent swarm depends on the environment it runs in.

## How to talk about GABBE honestly

- Lead with the runtime-agnostic markdown kit and the structured memory and SDLC — these are the
  most real, most differentiated, and most defensible claims.
- Describe the brain and genes as "a self-improving prompt loop using an epsilon-greedy bandit
  with a success-rate reward and LLM-driven mutation" — accurate and still interesting.
- Never say "active inference / free energy" as if it were computed; it is framing.
- Never say "guaranteed", "mathematically proven", or "best-in-class". GABBE's strength is a
  coherent, portable methodology with a small real learning loop — that is worth describing
  accurately rather than inflating.
