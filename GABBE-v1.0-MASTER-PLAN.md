# GABBE v1.0 — Methodology Expansion + Advanced Testing + Release Readiness (Final Master Plan)

## Context

GABBE (`/home/andrei/work/AI/GABBE`, v0.9.6 alpha) is a **runtime-agnostic Markdown "agentic
engineering kit"** (`llms.txt`): an external AI agent (Claude/Cursor/Copilot/Gemini/Codex) reads
`agents/AGENTS.md` + `CONSTITUTION.md` and operates as a governed engineering team **without needing
the Python CLI**. It already ships ~180 skills, ~85 templates, ~73 guides, 34 personas, a 10-phase
SDLC (S01–S10), the RARV per-task loop (`agents/guides/processes/RARV_CYCLE.md`), a 4-layer memory
model (RESUME_POINTER → PROJECT_STATE → CONTINUITY → AUDIT_LOG), and an **additive-only** emit
pipeline (`agents/scripts/compile_skills.py`) gated by CI validators.

**Why this change:** the user wants the *methodology layer* to be the priority and to approach
best-in-class coverage of the **entire** lifecycle — ideation/brainstorming → specs/design thinking →
architecture → implementation → management → final product → **post-launch maintenance & evolution** —
so the framework is excellent even when used standalone (no CLI/MCP). The original uploaded plan was
testing-only and had factual errors (corrected in Track B). Exploration of the existing framework
surfaced concrete gaps this plan closes.

**Outcome:** ship **GABBE v1.0** — a richer, self-consistent, validator-passing methodology layer
covering cradle-to-grave ADLC, grounded in named industry methods; a deterministic Python
property/fuzz/chaos test suite; hardened-and-*proven* self-* capabilities (self-evolving,
self-adaptive, self-healing, dynamic capability loading with ask-the-user fallback); refreshed
compatibility with current agentic coding agents; **100% backward compatibility** with existing
software/agents/procedures; and a documented **forward-adaptability protocol** so any future AI or
engineering methodology can be absorbed without breaking changes — closed by one complete end-to-end
v1.0 acceptance verification.

**On "100% perfect":** literal perfection is not provable; we operationalize it as a **concrete,
verifiable v1.0 readiness bar** — every validator green, every gate green, every backward-compat
baseline preserved, and every claimed capability (self-evolving/-adaptive/-healing/dynamic-loading)
demonstrated by an executable scenario. A claim ships only if a check proves it.

**Backward-compatibility guarantee (non-negotiable):** every change in this plan is **additive**.
The 6 CI gates (api-surface, cli-help, config-schema, db-schema, emitter-vault, cve-delta) and the
additive-only emit pipeline are the enforcement mechanism — no public API/CLI/config/DB/emit key is
removed or retyped. Existing agents, projects initialized on prior versions, and existing procedures
keep working unchanged. The only intentionally-regenerated baseline is `cli_help/verify.txt` (new
additive `--chaos` flag).

**Forward-adaptability (auto-evolving, everything supported):** v1.0 documents and tests the
extension points that let GABBE absorb anything new without a breaking change — new agents/clients via
the emitter registry, new skills/templates/personas via the additive index + `skills-registry`, new
tools/models/MCPs via `update-scan` + `emerging-tech` (tech radar), new knowledge via `knowledge-connect`
(RAG), and self-improvement via the brain gene-evolution loop + `meta-optimize`. Anything the agent
cannot resolve autonomously falls back to `clarify` (ask the user via the coding agent).

**Confirmed decisions:** Gap-fill **+ quality upgrade**; **add Day-0 (S00) and Day-2 (S11–S13)**
lifecycle phases; **both tracks on one branch**; ground content in **named methods** (ADD 3.0, ATAM,
Spec-Driven Development, fitness functions, DORA/SPACE, Wardley, ADKAR, JTBD) with self-contained prose
(no inline citation URLs).

**Honesty guardrail:** content claims "best-in-class / high-confidence coverage," never "mathematically
guaranteed 100% correctness." PBT/metamorphic testing sample an input space — they raise confidence,
they do not prove. This is stated in the testing skills. Likewise, **evals sample and LLM-as-judge is
biased-but-useful** — report `pass^k` reliability, never claim proof; a judge is calibrated against
human labels, never treated as ground truth; and the AI-risk **standards map documents coverage, not
certification**. (Track E.)

**Branch:** `git checkout -b feat/methodology-expansion-and-advanced-testing` (no commits/pushes until
the user reviews the diff).

---

## Authoring contract (every new markdown file MUST satisfy — enforced by CI)

- **Skills:** `agents/skills/<category>/<name>.skill.md`; YAML frontmatter with **required** `name` +
  `description`, plus `triggers` (non-empty, no placeholder words like "a/this/any"), `tags`,
  `context_cost`, `core`. Register in `agents/skills/00-index.md`.
- **Templates:** `agents/templates/<category>/`; register in `agents/templates/00-index.md`.
- **Guides:** `agents/guides/<subcategory>/`.
- **Personas:** `agents/personas/<name>.md`; register in `agents/personas/00-index.md`.
- **Links:** every `[text](path)` must resolve (validate_links.py). **No MCP** referenced unless it
  exists in `agents/templates/core/MCP_CONFIG_TEMPLATE.json`.
- Match existing `.skill.md` section convention: **Goal → Steps → Constraints → Output Format →
  (optional) Security & Guardrails**.

---

# TRACK A — Methodology Layer (primary)

## A1. Lifecycle extension — Day-0 + Day-2 (cradle-to-grave ADLC)

Edit `agents/guides/processes/loki-sdlc-phases.md`, `agents/skills/brain/loki-mode.skill.md`,
`agents/templates/core/SDLC_TRACKER.md`, `agents/memory/PROJECT_STATE_TEMPLATE.md`, and
`agents/guides/processes/full-system-lifecycle.md` (extend the golden thread) to add:

- **S00 — Strategy & Discovery (Day-0):** opportunity framing, ideation, Wardley mapping, market/
  competitive scan, problem statement, North-Star/HEART metric, RICE prioritization. Leads:
  `prod-research`, `prod-pm`. **Human gate:** go/no-go before S01.
- **S11 — Operate & Maintain (Day-2):** SRE operations, on-call/incident, patching, dependency
  upgrades, SLO adherence, cost monitoring. Leads: `ops-sre`, `ops-monitor`, `ops-incident`,
  `ops-cost`.
- **S12 — Evolve & Continuously Improve:** blameless retrospective, tech-debt paydown, analytics-
  driven iteration, A/B experiments, feature-flag lifecycle, DORA/SPACE review. Leads:
  `prod-product-ops` (new), `prod-pm`, `eng-*`.
- **S13 — Decommission & Sunset:** deprecation policy, data retention/migration, archival, user
  comms, license/contract wind-down. Leads: `prod-pm`, `ops-sre`, `biz-legal`.

## A2. New quality gates inside existing phases

Document in `loki-sdlc-phases.md` and the `orch-judge` persona:
- **S02.5 Cost & Feasibility gate** — architecture cost estimate + budget approval (uses new
  `financial-governance` skill).
- **S04.5 Parallelism/Dependency feasibility** — dependency-graph + resource-conflict check (new
  `DEPENDENCY_GRAPH_TEMPLATE.md`).
- **S06.5 Performance-regression gate** — benchmark vs. baseline before S07.
- **S07.5 Sustainability gate** — invoke `green-software` report before S08.

## A3. New skills (gap-fill) — ~18 files, grounded in named methods

**Product / Day-0 & discovery** (`agents/skills/product/`):
- `ideation-facilitation.skill.md` — divergent/convergent brainstorming (How-Might-We, Crazy-8s,
  SCAMPER) + concept selection.
- `user-research-synthesis.skill.md` — affinity mapping, JTBD, persona synthesis, journey mapping.
- `opportunity-assessment.skill.md` — Wardley mapping, opportunity sizing, North-Star/HEART, RICE.
- `change-management.skill.md` — ADKAR adoption, comms cadence, training plan.
- `estimation-sizing.skill.md` — reference-class forecasting, probabilistic ranges, t-shirt/points.
- `product-analytics.skill.md` — event taxonomy, funnels, A/B experiment design, **DORA Four Keys +
  SPACE** delivery metrics.
- `financial-governance.skill.md` — budget tracking, cost allocation, ROI / unit-economics.

**Architecture** (`agents/skills/architecture/`):
- `attribute-driven-design.skill.md` — **ADD 3.0** (drivers → design iterations → tactics/patterns →
  quality-attribute scenarios). Grounds the "ADD" the user named.
- `fitness-functions.skill.md` — evolutionary-architecture fitness functions for continuous arch
  governance (ties to `architecture-governance` + `agentic-linter`).

**Coding / testing** (`agents/skills/coding/`):
- `pbt-strategy.skill.md` — Hypothesis property + `RuleBasedStateMachine` invariants.
- `metamorphic-testing.skill.md` — metamorphic relations (paraphrase/noise invariance), with the
  hand-designed-MR + live-LLM caveat.
- `chaos-fault-injection.skill.md` — fault recipes ↔ expected escalation/hardstop/rollback.
- `spec-driven-development.skill.md` — spec-first (Spec Kit-style) workflow; ties S01→S04.

**Ops / Day-2** (`agents/skills/ops/`):
- `observability-stack-setup.skill.md` — OpenTelemetry instrumentation, dashboards/alerts bootstrap.
- `feature-flag-management.skill.md` — flag lifecycle, progressive delivery, kill switches.
- `runbook-authoring.skill.md` — operational runbooks (every alert → runbook).
- `dependency-lifecycle.skill.md` — patch/upgrade cadence, SBOM refresh, EOL tracking.
- `decommission-sunset.skill.md` — deprecation & sunset method.

**Core** (`agents/skills/core/`):
- `retrospective.skill.md` — blameless retrospective; lessons-learned feed `CONTINUITY.md`.

## A4. New templates — ~10 files

`agents/templates/`: `core/ESTIMATION_TEMPLATE.md`, `architecture/FITNESS_FUNCTION_TEMPLATE.md`,
`architecture/ADD_WORKBOOK_TEMPLATE.md`, `core/PROJECT_RETROSPECTIVE_TEMPLATE.md`,
`ops/RUNBOOK_TEMPLATE.md`, `core/DEPENDENCY_GRAPH_TEMPLATE.md`, `product/EXPERIMENT_PLAN_TEMPLATE.md`,
`product/CHANGE_MANAGEMENT_PLAN_TEMPLATE.md`, `ops/DECOMMISSION_PLAN_TEMPLATE.md`,
`coding/PROPERTY_TEST_CHECKLIST.md`. Each registered in `agents/templates/00-index.md` and wired to the
phase/skill that produces it.

## A5. New personas — 2 files

`agents/personas/prod-product-ops.md` (Day-2 metrics/analytics/experimentation owner) and
`agents/personas/prod-integration.md` (third-party integration / vendor-SLA architect). Register in
`agents/personas/00-index.md`; wire into S11/S12 (product-ops) and S02/S03/S05 (integration).

## A6. Quality upgrades to existing core methodology files

- `agents/skills/coding/testing-strategy.skill.md` — add PBT / metamorphic / chaos / mutation tiers
  above the pyramid; link the four new testing skills. Add the line *tests verify determinism; **evals**
  score probabilistic quality* and point to the Track E eval skills (evals are a discipline distinct
  from tests).
- `agents/skills/architecture/arch-review.skill.md` — make **ATAM** explicit (utility tree, scenario
  prioritization, sensitivity/tradeoff points).
- `agents/personas/eng-qa.md` — reference new testing skills + the `slow`/`live_llm`/`mutation` marker
  scheme (Track B).
- `agents/guides/principles/testing-strategy.md` — modernize to match the upgraded skill.
- `agents/skills/brain/active-inference.skill.md` + `loki-mode.skill.md` — add a one-line
  "Implementation note": the production `gabbe/brain.py` uses epsilon-greedy gene selection +
  monotonic success_rate; the free-energy framing is conceptual (prevents future tests against
  non-existent math).

## A7. Index, memory & self-consistency

- Register all new skills/templates/personas in their `00-index.md` files; ensure every new skill has
  non-empty, non-placeholder triggers.
- Update `SDLC_TRACKER` + `PROJECT_STATE` templates for S00/S11/S12/S13.
- Verify every phase reference points to an existing skill/template/persona, and every new file's links
  resolve (closes the loop the validators check).

---

# TRACK B — Advanced Testing (secondary, deterministic Python)

Condensed from the corrected testing plan (full rationale in Context). All additive and gate-safe.

- **Phase 0 — Plumbing:** add `hypothesis-jsonschema>=0.23` + `mutmut>=2.4` to `pyproject.toml` `[dev]`
  (reject `schemathesis`/`pytest-asyncio`/`fastmcp` — wrong protocol / no coroutines / would break the
  api-surface gate). Add pytest markers `slow`/`live_llm`/`mutation`. Update `ci.yml` `validate` step to
  `-m "not slow and not live_llm and not mutation"`.
- **Phase 1 — Core invariants (per-commit):** `gabbe/tests/test_{budget,sync,route,replay}_properties.py`
  reusing `tmp_project`/`db_conn` — budget cap never exceeded, sync idempotency/convergence, route
  PII-LOCAL + complexity threshold, replay round-trip/idempotency.
- **Phase 2 — MCP fuzz + chaos:** `test_mcp_fuzz.py` (`hypothesis-jsonschema` against the
  jsonschema-validated `run_command` handler + malformed JSON-RPC envelope fuzzing via patched stdin);
  dedupe MCP schema into one `_RUN_COMMAND_SCHEMA` with a gentle `maxLength`/no-NUL bound (update both
  sites + `docs/MCP_CONFIGURATIONS.md`). `test_chaos_fault_injection.py` — subprocess timeout, sqlite
  `OperationalError` mid-txn, LLM failure → assert escalation/hardstop/rollback (silent escalation mode).
  **(Track E5)** bound *every* string tool input by charset+length (`pattern`+`maxLength`) and add
  `test_mcp_contract.py` (schemas valid; bounded; adversarial payloads fail-closed).
- **Phase 3 — Brain reframe:** `test_brain_properties.py` (real engine: monotonic capped success_rate,
  epsilon-greedy bounds, escalation-once) + `test_brain_toy_demos.py` (toy `active_inference_loop.py` /
  `global_workspace.py`, labeled non-integrated). **(Track E6)** add `test_brain_invariants.py`
  (mutually-exclusive-state + toy-convergence + episodic resume-pointer integrity) and
  `test_loki_shadow.py` (loop/resource guard, confidence-threshold escalation, self-heal→restore).
- **Phase 4 — `gabbe verify --chaos`:** add **new** public `run_chaos_checks()` in `gabbe/verify.py`
  (do not change `run_verification()`'s baselined signature), wire `--chaos` in `gabbe/main.py`,
  regenerate only `gabbe/tests/baselines/cli_help/verify.txt`.
- **Phase 5 — Nightly lane (opt-in):** metamorphic LLM tests marked `live_llm` (mocked by default; real
  only when `GABBE_LIVE_LLM=1`); add `nightly` CI job (`schedule` + `workflow_dispatch`) running
  `slow`/`live_llm` + non-blocking `mutmut` on `budget.py,sync.py,route.py`.

---

# TRACK C — v1.0 Release Readiness, Self-* Hardening & Compatibility

## C1. Self-* capability hardening + executable proof (the core of the v1.0 ask)

For each capability: confirm what is *real code* vs *agent-orchestrated markdown*, harden it, document
it honestly, and add an **executable proof scenario** (Python test where code exists; a scripted
walkthrough doc validated by `verify_use_cases.py` where it is markdown-orchestrated).

- **Self-evolving** — real engine `gabbe/brain.py` (`evolve_prompts`, epsilon-greedy `_get_best_gene`,
  monotonic `_update_gene_success_rate`) + `meta-optimize`/`self-improvement` skills. Proof:
  `test_brain_properties.py` (Track B Phase 3) shows generation increments + reward closes the loop.
  Doc: `agents/guides/ai/self-evolving-skills.md` (genes, fitness, "brain inference via skills" —
  GABBE's world-first framing, stated honestly).
- **Self-adaptive** — `cost-benefit-router`, `persona-selector`, autonomy levels (`GABBE_AUTONOMY`
  ask|auto|hybrid), dynamic routing (PII→LOCAL). Proof: `test_route_properties.py` (Track B) +
  preflight "recommend OPTIMAL set" path. Doc: upgrade `agents/skills/brain/cost-benefit-router.skill.md`.
- **Self-healing** — `self-heal` (5-attempt loop) + `ci-autofix` + escalation/hardstop. Proof:
  `test_chaos_fault_injection.py` (Track B Phase 2) asserts escalation after repeated failure. Doc:
  refresh `agents/guides/ai/self-healing-summary.md`.
- **Dynamic capability loading + ask-the-user fallback** — `update-scan`, `emerging-tech`,
  `skills-registry`, `knowledge-connect` (RAG), and the preflight ranking by relevance×(1/context_cost);
  when unresolved, `clarify` asks the user through the coding agent. NEW guide
  `agents/guides/ai/dynamic-capability-loading.md` describing the load-or-ask flow end-to-end; validated
  by `verify_use_cases.py` (scenario: "needed capability missing → discover or ask").

## C2. Compatibility refresh — current agentic coding agents

- Research the current major agents at implementation time and refresh/extend the emitters in
  `agents/scripts/compile_skills.py` and `agents/scripts/init.py`: Claude Code, Cursor, GitHub
  Copilot / VS Code, Gemini, Codex, plus current others (Windsurf, Zed, Antigravity, OpenCode, Amazon
  Kiro, Aider) — added **additively** (new clients only; never remove existing ones, preserving
  Gate 4 emitter-vault baselines).
- Anchor on open standards already used: `AGENTS.md` standard + the agent-skills `SKILL.md` directory
  standard. Update `docs/MCP_CONFIGURATIONS.md` and `README.md`/`llms.txt` compatibility matrix.
- **Backward-compat check:** every prior emitter output must still be produced byte-compatibly
  (Gate 4 golden emitters); new agents add new output paths only.

## C3. Forward-adaptability / extension protocol (auto-evolving, future-proof)

- NEW guide `agents/guides/processes/extension-protocol.md`: the canonical, additive way to add a new
  skill / template / persona / guide / agent-client / MCP / model without a breaking change — the
  contract that makes GABBE absorb "any future AI or engineering methodology."
- Document the **schema-version migration** path (`gabbe-schema-version`) and the additive-only policy
  in `docs/SCHEMA.md` so future format growth never breaks old consumers.
- Wire `emerging-tech` (tech radar) + `update-scan` into S11/S12 so the framework keeps adopting new
  capabilities over a project's life.

## C4. v1.0 release mechanics (all additive)

- Bump version to **1.0.0** in `pyproject.toml` and `package.json`; confirm no breaking emit/schema
  change accompanies the major bump (additive-only preserved).
- Update `CHANGELOG.md` (v1.0 entry), `README.md` (feature list + honest "world-first" framing:
  brain-inference-via-skills / self-evolving genes), `llms.txt`, and `agents/guides/ai/gabbe-innovations.md`
  (NEW: what's novel, what's real vs conceptual).
- Add `docs/V1_RELEASE_CHECKLIST.md` — the human-runnable release gate (mirrors the Acceptance Matrix
  below).

---

# TRACK D — Distribution: easy, isolated, auto-detecting and automated, fully-reversible Install / Update / Uninstall

**Current state (audited):** 3 install entry points — `install.sh`/`install.ps1` (bootstrap) →
`bin/install.js` (`npx gabbe init`) → `scripts/init.py` (wizard); `gabbe` console-script via
`pyproject.toml`. Install is **strictly isolated today** (writes only into the target dir or optional
`$HOME/agents`; no shell-rc, `$PATH`, global-npm, or system writes) and supports per-agent selection
(`--agents`) for 16 agents. **Gaps blocking v1.0:** no uninstall, no install manifest, no
agent-deselection, `.bak` files pile up, symlink-vs-copy not tracked, orphaned emitted skills on
re-runs, global install undocumented.

## D1. Install manifest (backbone of reversibility) — additive

Every installer writes `.gabbe/manifest.json` in the target recording **exactly** what it created:
each entry = `{path, kind: symlink|copy|dir|skill-emit, points_to, agent, bytes/hash, backup_of:
<.bak path|null>, installer_version, schema_version, timestamp}` plus the agent-selection snapshot and
chosen target (project|global|custom). Implemented in `bin/install.js`, `scripts/init.py`, and
`agents/scripts/compile_skills.py` (records emitted skill dirs). New file → **does not** touch
api-surface/config/db gates; it is a NEW emitted artifact so Gate 4 (additive-only) accepts it.

## D2. Multi-target install (your selectable scopes), automated discovery and auto-detection of platforms, agents, systems, directories

- **Project dir (default):** target = cwd. Unchanged behavior.
- **Global system:** `--global` → `$XDG_DATA_HOME/gabbe` (fallback `$HOME/.gabbe` or `$HOME/agents`),
  with a **refcount** of dependent projects in the global manifest so uninstall never deletes a kit
  another project still uses.
- **Custom dir:** `--dir <abs-path>`.
- All three documented in a new `docs/INSTALL.md` with copy-paste commands. **Isolation invariant
  (enforced + tested):** nothing is ever written outside the chosen target (no shell rc, no `$PATH`,
  no global npm, no system paths) unless `--global` is explicitly chosen.

## D3. Distribution channels (multiple options, from remote repo or package)

Document + verify install from: (a) `npx gabbe init` (npm), (b) `pipx install gabbe` / `pip install
gabbe` then `gabbe init` (PyPI), (c) `curl -fsSL <repo>/install.sh | sh` (bootstrap), (d) `git clone`
+ `python3 scripts/init.py`. Each lands the same kit; each reversible by D4.

## D4. Update & Uninstall — clean, scoped, idempotent, error-free

- **`uninstall`** (`npx gabbe uninstall`, `gabbe uninstall`, plus `uninstall.sh`/`uninstall.ps1`):
  reads `.gabbe/manifest.json`, removes **exactly** what was installed (symlinks, copies, emitted skill
  dirs, then now-empty dirs), **restores any `.bak` backups**, and **never** touches user/preserve
  files (`AGENTS.md` edits, `CONSTITUTION.md`, `memory/*`, `project/*`, `policies.yml`, `PROJECT*.md`).
  Flags: `--agents <list>` (scope to specific agents), `--dry-run` (print plan, change nothing),
  `--purge` (also remove `agents/` kit + `.gabbe/`). Idempotent: safe to run twice; tolerant of
  partially-removed state; exits 0 with a clear report.
- **`--remove-agents <list>`** on init/update: deselect an agent — remove only that agent's wiring via
  the manifest, leaving everything else intact.
- **`update`** (`npx gabbe update` / `gabbe update`): refresh kit files **additively** from source,
  preserve all user/preserve files, prune orphaned emitted skills (manifest diff), bump
  `gabbe-schema-version` if needed. Backward-compatible by construction.
- `.bak` hygiene: track every backup in the manifest; `uninstall` restores them; `update` reports them.

## D5. Tests (deterministic, per-commit) under `scripts/tests/`

- `test_install_manifest.py` — install into a tmp dir for a chosen agent set; assert manifest lists
  every created path with correct `kind`, and that re-install is idempotent (no duplicate/orphan).
- `test_uninstall.py` — install → uninstall → assert the tmp target is byte-identical to its
  pre-install state (preserve files untouched, `.bak` restored, no leftovers); `--dry-run` changes
  nothing; double-uninstall is safe.
- `test_install_isolation.py` — snapshot the filesystem **outside** the target before/after install;
  assert zero writes outside the target (no `$HOME`, no system paths) for project/custom scope; assert
  unselected agents get zero files.
- `test_remove_agents.py` — multi-agent install, then `--remove-agents` one; assert only that agent's
  files are gone and the rest are intact.

**Gate impact (all additive):** new CLI subcommands (`uninstall`/`update`) and flags change
`gabbe --help` / subcommand help → regenerate the affected `cli_help/*.txt` baselines (Gate 2
documented-additive carve-out). New public functions are additive for Gate 1. No removals anywhere.

---

# TRACK E — Evaluation, Standards-Grounded Guardrails, Cognitive-Mode Testing & Published-Library Verification

**Why:** the framework has deterministic tests (Track B) and OTel observability (`gabbe/audit.py`), but
no way to **score** the quality of its ~180 markdown skills (the product) or its agent trajectories, no
**standards-grounded** guardrail methodology, only thin cognitive-mode testing, no graph-level
flow/logic/state verification, and no verification of the **published** artifact's one-command install.
All additive, honest, and dependency-minimal (heavy eval libs are an optional `[evals]` extra / external
CLI only — the CVE-delta gate stays clean). Where a file already covers a concern, **upgrade** it.

## E1. Eval methodology skills (markdown, zero-dep, runtime-agnostic) — primary value

New skills (section convention: Goal → Steps → Constraints → Output Format → Security & Guardrails):
- `agents/skills/coding/eval-driven-development.skill.md` — offline eval suites; golden datasets;
  3-tier assertions (deterministic exact/regex/JSON-schema → semantic similarity → LLM-as-judge);
  eval-driven CI; statistical gating for nondeterminism (`pass@k`/`pass^k`, run-N-times thresholds —
  single-run estimates vary 2–6 pp); prompt-drift regression. Names Promptfoo/DeepEval patterns without
  depending on them.
- `agents/skills/ai/llm-as-judge.skill.md` — rubric-based scoring; known biases (position, verbosity,
  the dominant *style* bias, self-preference) + mitigations (position randomization, CoT, ensemble
  judges, calibration vs. human labels, temperature=0). Honesty: biased-but-useful, never ground truth.
- `agents/skills/ai/rag-evaluation.skill.md` — faithfulness, answer relevance, context precision/recall
  (Ragas-grounded, reference-free); ties to `core/knowledge-connect.skill.md`; MeTMaP silent-mismatch caveat.
- `agents/skills/coding/agent-trajectory-eval.skill.md` — tool-selection precision/recall/F1, parameter
  F1, trajectory in-order match (not exact-match), state-machine transition checks, success-rate +
  `pass^k`. Ground in τ-bench + SWE-bench Verified.

New templates: `agents/templates/coding/{EVAL_PLAN_TEMPLATE,GOLDEN_DATASET_TEMPLATE,EVAL_RUBRIC_TEMPLATE}.md`
(golden-dataset shape is promptfoo-compatible YAML). New guide:
`agents/guides/principles/evaluation-strategy.md` (eval pyramid: deterministic → semantic → judge →
human; eval-first alongside test-first). Wire eval checkpoints into **S05/S06** (eng-qa) + **S12**
(Day-2 continuous eval); update `eng-qa.md` + `testing-strategy.skill.md`.

## E2. Skill self-eval harness (GABBE evaluating its own skills) — minimal, home-grown, `live_llm`/nightly

- `agents/scripts/eval_skills.py` (**no new dep**) — reads golden cases, calls the model via a thin
  adapter reusing `gabbe/llm.py` + `gabbe/cache.py` when present, else degrades to assertions-only
  (no-LLM) mode; scores deterministic assertions per-commit + optional LLM-judge under `live_llm`;
  emits a JSON scorecard.
- Golden datasets beside skills: `agents/skills/<category>/evals/<skill>.eval.yaml` (promptfoo-compatible).
  Seed high-value subset: `core/clarify`, `core/research`, `product/spec-writer`, `coding/code-review`,
  `core/integrity-check`.
- Optional `gabbe eval` subcommand in `gabbe/main.py` (additive: new public `run_evals()` in a new
  module; regenerate only new `cli_help/eval.txt`). Add optional `[evals]` extra to `pyproject.toml`
  (promptfoo/Ragas/DeepEval/Langfuse documented as external tools, kept out of core + `[dev]`).

## E3. Eval-driven CI lane (nightly, non-blocking first)

Extend the Track B Phase 5 nightly job to also run `eval_skills.py --live` over the seeded golden set,
compare to a stored baseline scorecard, report drift (**non-blocking**). Per-commit CI runs only the
deterministic-assertion subset. Blocking eval gates are the documented **v1.1 path**, not a v1.0 promise.

## E4. Guardrails grounded in named standards (parallels ADD 3.0 / ATAM grounding)

- New `agents/skills/security/prompt-injection-defense.skill.md` — direct vs. indirect (tool-output/RAG)
  injection; the lethal trifecta; Meta "Rule of Two"; dual-LLM/quarantine + spotlighting + instruction
  hierarchy; "assume tool output is untrusted." Ground in OWASP **LLM01:2025**.
- New `agents/skills/coding/output-validation.skill.md` — schema-validated output (Pydantic/Zod) +
  constrained decoding + retry-on-validation-failure; PII masking before external calls and before
  logging (Presidio-grounded regex+NER hybrid; false-negative caveat). Ground in OWASP **LLM05** + **LLM02**.
- New guide `agents/guides/security/ai-risk-standards-map.md` — mapping table: GABBE skill/gate/persona
  ↔ OWASP LLM Top 10 (2025) LLM01–LLM10, NIST AI RMF (+ GenAI Profile), MITRE ATLAS, ISO/IEC 42001,
  EU AI Act. Subsumes the Post-EOF suggestion #1 (`threat-model.skill.md` + `compliance-review.skill.md`
  already exist — link, don't duplicate).
- **Upgrade** `agents/skills/security/ai-safety-guardrails.skill.md` with the input/output/dialog/
  retrieval/execution **rails taxonomy** + links to the two new skills. Wire both new skills into
  **S02** (threat model), **S05/S07** (impl/security review), and the brain/loki Security sections.

## E5. MCP contract-test hardening (strengthens Track B Phase 2)

Extend the planned `_RUN_COMMAND_SCHEMA` dedupe so **every string tool input is bounded by charset +
length** (`pattern` + `maxLength`), not just no-NUL/maxLength (ground in MCP-38 taxonomy + NSA MCP
guidance). Add `gabbe/tests/test_mcp_contract.py` — declared input/output schemas are valid JSON Schema;
all string inputs bounded; valid payloads accepted; adversarial payloads (oversized, bad charset,
missing-required, extra-field, malformed JSON-RPC envelope) rejected fail-closed. Complements (not
replaces) `test_mcp_fuzz.py`. Update `docs/MCP_CONFIGURATIONS.md` + `SECURITY.md`.

## E6. Cognitive-mode (Brain/Loki) testing — honest reframe respected

- `gabbe/tests/test_brain_invariants.py` — drives the **toy** `agents/skills/brain/scripts/
  {global_workspace,active_inference_loop}.py`: (a) mutually-exclusive states never co-exist; (b) toy
  prediction error is non-increasing/converges over N iterations (tests the toy demo, labeled
  non-integrated — production `gabbe/brain.py` is epsilon-greedy, not literal free-energy); (c)
  episodic-memory resume-pointer integrity under rapid context switching (exact last state, no
  fabricated history).
- `gabbe/tests/test_loki_shadow.py` — shadow/sandbox testing of the orchestration state machine vs. a
  mock `state.db`: loop/resource guard (identical tool call ×3 → escalation), confidence-below-threshold
  → human escalation, injected-failure → self-heal → baseline restore. Reuse
  `escalation.py`/`hardstop.py`/`replay.py` + `tmp_project`. Deterministic, per-commit.
- New `agents/skills/brain/cognitive-testing.skill.md` — test cognitive loops via invariants/
  convergence/shadow-testing, not output-equality; cross-link `pbt-strategy` + `chaos-fault-injection`.

## E7. Methodology-graph verification (flows / logic / states / architecture checked)

New `agents/scripts/validate_methodology_graph.py` (additive validator joining the `validate_*`/
`verify_*` suite) checks: **lifecycle state machine** (every S00–S13 phase has lead persona(s) + output
template(s) + gate; transitions form a valid DAG with human-approval gates present; no phase references a
missing skill/template/persona); **persona handoff graph** (inputs/outputs resolve; no orphan persona;
orch-planner → eng-* → eng-qa → orch-judge connected); **memory state model** (RESUME_POINTER →
PROJECT_STATE → CONTINUITY → AUDIT_LOG referenced coherently); **skill shape** (required sections present;
triggers non-placeholder). Add to CI `validate` + Acceptance item 1.

## E8. Published-library verification — one-command install, autodetect env/agents/OS, multi-OS

Verify the **actually published artifact** (not just a local checkout) installs everything with a single
simple command and auto-detects the environment, agents, platform, and OS.

- **Single-command install (verified):** each channel is one command — `npx gabbe init`,
  `pipx install gabbe` (or `pip install gabbe`) `&& gabbe init`, `curl -fsSL <repo>/install.sh | sh`.
  A post-publish smoke job installs from the **real registry** (npm / PyPI / raw URL), not the working
  tree, and asserts the kit lands + emits for detected agents end-to-end.
- **Autodetection (tested):** new `scripts/tests/test_autodetect.py` asserts the installer correctly
  detects (a) installed agent clients (Claude Code, Cursor, Copilot/VS Code, Gemini, Codex, Windsurf,
  Zed, Antigravity, OpenCode, Cline, Aider, …) from their config-dir fingerprints; (b) OS/platform
  (linux/macos/windows, arch); (c) package managers / runtimes available (node, python, pipx, git);
  (d) target scope (project/global/custom). Detection is reported in `gabbe doctor` output (see below)
  and recorded in `.gabbe/manifest.json`. Unknown/absent agents are skipped cleanly, never error.
- **`gabbe doctor` / `gabbe verify --install` (additive):** a single read-only command that prints a
  full environment + install report — detected OS/arch, runtimes, agents, chosen target, what is/would
  be written, manifest integrity, and a PASS/FAIL per check. New public `run_doctor()` (regenerate only
  the new `cli_help/doctor.txt`).
- **Multi-OS CI matrix:** add an `install-matrix` job to `.github/workflows/ci.yml` running on
  `{ubuntu, macos, windows}` × `{npx, pip/pipx, curl|sh (POSIX) / install.ps1 (Windows)}`, executing
  install → `gabbe doctor` → emit-for-detected-agents → `update` → `uninstall` → assert byte-identical
  restore. Guarantees the shell/PowerShell/npm/Python paths don't bit-rot (closes Post-EOF suggestion #2).
- **Post-publish (release) verification:** add a `release-verify` job to `release.yml` (or a scheduled
  job) that, after publish, installs the **published** package on the OS matrix from each channel and
  runs the same smoke checks; failure blocks marking the release "verified."
- **Tests (deterministic, per-commit where possible):** `scripts/tests/test_autodetect.py`,
  `scripts/tests/test_one_command_install.py` (each channel's single command lands the kit into a tmp
  target and autodetect populates the manifest); the live published-registry checks run in the
  install-matrix / release-verify jobs.

---

## Suggested execution order

0. **Research refresh** (start of implementation): re-run targeted web research to confirm the current
   agentic-coding-agent list (C2) and that named methods/metrics are still current — fold any deltas in.
1. Branch.
2. Track A (primary): A1 lifecycle → A2 gates → A3 skills → A4 templates → A5 personas → A6 upgrades →
   A7 indexes/self-consistency.
3. Track C: C1 self-* hardening/proof → C2 compatibility refresh → C3 extension protocol → C4 release
   mechanics (version bump + CHANGELOG/README/V1 checklist last).
4. Track D: D1 manifest → D2 targets → D3 channels → D4 update/uninstall → D5 tests.
5. Track B: Phase 0 → 5 (deterministic per-commit first; nightly lane last).
6. Track E: E7 graph-validator + E1 eval skills/templates/guide → E4 guardrails + E5 MCP contract →
   E6 cognitive tests → E2 eval harness → E8 published-library verification (multi-OS + autodetect) →
   E3 nightly eval lane (E5/E6 fold into Track B Phase 2/3; do them with Track B).
7. **Final v1.0 Acceptance Verification** (below) — must be 100% green before tagging v1.0.0.
(Tracks A/B/C/D/E are largely independent; A is primary, C4 version bump is last.)

## FINAL v1.0 ACCEPTANCE VERIFICATION (complete, end-to-end — all must pass)

This is the single release gate. Mirror it into `docs/V1_RELEASE_CHECKLIST.md`. Tag v1.0.0 only when
**every** item below is green.

**1 — Methodology layer is valid & self-consistent (the docs' test suite):**
```
python3 agents/scripts/validate_skills.py            # frontmatter parses; required keys present
python3 agents/scripts/validate_links.py             # zero broken [text](path) links, all files
python3 agents/scripts/validate_integrity.py         # required dirs/structure intact
python3 agents/scripts/verify_triggers_and_mcps.py   # triggers non-empty; referenced MCPs exist
python3 agents/scripts/verify_use_cases.py           # every documented scenario resolves to real skills
python3 agents/scripts/validate_methodology_graph.py # (E7) lifecycle DAG + persona handoffs + memory state coherent
```
Manual cross-check: every S00–S13 phase + every new gate references an existing skill/template/persona;
every new skill/template/persona appears in its `00-index.md`.

**2 — Backward compatibility preserved (the guarantee):**
```
bash scripts/gates/run_gates.sh    # ALL 6 gates green:
#   Gate 1 api-surface  (no removed/changed public signatures — only additions)
#   Gate 2 cli-help     (byte-equal; ONLY cli_help/verify.txt regenerated for additive --chaos)
#   Gate 3 config-schema + 3b db-schema (additive only)
#   Gate 4 emitter-vault (every prior client's output byte-compatible; new agents = new paths only)
#   Gate 6 cve-delta    (no new CVEs)
```

**3 — Python test suite green (deterministic per-commit):**
```
pip install -e ".[dev]"
pytest gabbe/tests/ scripts/tests/ -v -m "not slow and not live_llm and not mutation"
#   includes (Track E) test_mcp_contract.py, test_brain_invariants.py, test_loki_shadow.py,
#   test_autodetect.py, test_one_command_install.py, and the assertions-only eval_skills subset
ruff check . && black --check . && mypy gabbe
```

**4 — Self-* capabilities each demonstrated (claim → proof):**
- Self-evolving: `pytest gabbe/tests/test_brain_properties.py` (gene generation increments; reward loop closes).
- Self-adaptive: `pytest gabbe/tests/test_route_properties.py` (PII→LOCAL; complexity routing).
- Self-healing: `pytest gabbe/tests/test_chaos_fault_injection.py` (escalation/hardstop after repeated failure).
- Dynamic-load-or-ask: `verify_use_cases.py` scenario passes for `dynamic-capability-loading.md`.
- `gabbe verify --chaos` → all fault-injection self-checks PASS.

**5 — Compatibility & emission proven (works standalone, every target agent):**
```
# For each supported client (claude, cursor, copilot, gemini, codex, + new additive ones):
python3 agents/scripts/compile_skills.py --platform <client> --skills-dir agents/skills --target-dir /tmp/gabbe-<client>
# Confirm new skills/personas/templates appear in each client's emitted output.
python3 scripts/init.py  (or: npx gabbe init)   # clean init succeeds end-to-end with the new content
```

**6 — Release mechanics complete:** version = 1.0.0 (`pyproject.toml`, `package.json`); CHANGELOG v1.0
entry; README/llms.txt compatibility matrix + honest world-first framing; `docs/V1_RELEASE_CHECKLIST.md`
present and all boxes ticked; full CI (validate matrix py3.9–3.13 + lint + gates) green.

**7 — Forward-adaptability proven:** `extension-protocol.md` walkthrough adds a throwaway sample
skill/template/persona/MCP and passes all validators + gates (proving new things can always be added
additively); then revert the sample. Confirms "any future methodology can be absorbed without a
breaking change."

**8 — Install / Update / Uninstall reversible & isolated (every target × agent):**
```
pytest scripts/tests/test_install_manifest.py scripts/tests/test_uninstall.py \
       scripts/tests/test_install_isolation.py scripts/tests/test_remove_agents.py -v
```
Manual matrix (tmp dirs): for scope ∈ {project, custom-dir, global} and a representative agent set —
install → confirm only target written (item: zero writes outside target except `--global`) → `update`
(user files preserved) → `uninstall --dry-run` (no change) → `uninstall` → **target byte-identical to
pre-install state**, `.bak` restored, preserve files intact. Confirm install also works from each
channel (npx / pipx / curl|sh / git-clone). Unselected agents get zero files; `--remove-agents` removes
only the named agent.

**9 — Evals & standards-grounded guardrails proven (Track E):**
- `python3 agents/scripts/eval_skills.py` (assertions-only subset) green per-commit; nightly
  `GABBE_LIVE_LLM=1 python3 agents/scripts/eval_skills.py --live` scorecard within threshold of the
  stored baseline (non-blocking) → no prompt-drift regression on the seeded golden set.
- `agents/guides/security/ai-risk-standards-map.md` present and validated: **every OWASP LLM01–LLM10
  row maps to ≥1 named GABBE skill/gate/persona**; `prompt-injection-defense` + `output-validation`
  skills registered in `00-index.md` and reachable from `ai-safety-guardrails.skill.md`.

**10 — Published library: one-command install, autodetect, multi-OS, fully reversible (Track E8):**
```
pytest scripts/tests/test_autodetect.py scripts/tests/test_one_command_install.py -v
```
- CI `install-matrix` green on {ubuntu, macos, windows} × {npx / pip|pipx / curl|sh | install.ps1}:
  install (single command) → `gabbe doctor` (detects OS/arch, runtimes, agents, scope; all checks PASS)
  → emit for every detected agent → `update` → `uninstall` → target byte-identical to pre-install.
- `release-verify` installs the **published** package (npm / PyPI / raw URL) on the OS matrix and passes
  the same smoke checks; unknown/absent agents are skipped cleanly (never error).

> Definition of done for v1.0: items 1–10 all green on a clean checkout and in CI. No item may be waived.

## Critical files
- Lifecycle/spine: `agents/guides/processes/loki-sdlc-phases.md`, `agents/skills/brain/loki-mode.skill.md`, `agents/guides/processes/full-system-lifecycle.md`
- Indexes: `agents/skills/00-index.md`, `agents/templates/00-index.md`, `agents/personas/00-index.md`
- Memory templates: `agents/templates/core/SDLC_TRACKER.md`, `agents/memory/PROJECT_STATE_TEMPLATE.md`
- Upgrades: `agents/skills/coding/testing-strategy.skill.md`, `agents/skills/architecture/arch-review.skill.md`, `agents/personas/eng-qa.md`
- Validators (the docs' test harness): `agents/scripts/validate_*.py`, `agents/scripts/verify_*.py`
- Track B: `pyproject.toml`, `.github/workflows/ci.yml`, `gabbe/mcp_server.py`, `gabbe/verify.py` + `gabbe/main.py`, `gabbe/tests/conftest.py`
- Track C: `agents/scripts/compile_skills.py` + `scripts/init.py` (emitters), `README.md`, `llms.txt`, `docs/SCHEMA.md`, `CHANGELOG.md`, new `agents/guides/ai/{self-evolving-skills,dynamic-capability-loading,gabbe-innovations}.md`, `agents/guides/processes/extension-protocol.md`, `docs/V1_RELEASE_CHECKLIST.md`
- Track D: `bin/install.js`, `scripts/init.py`, `install.sh` + `install.ps1` (+ new `uninstall.sh`/`uninstall.ps1`), `agents/scripts/compile_skills.py`, `gabbe/main.py` (new `uninstall`/`update` subcommands), new `docs/INSTALL.md`, new `scripts/tests/test_{install_manifest,uninstall,install_isolation,remove_agents}.py`
- Track E (evals/guardrails/cognitive/graph/published-verify): new skills `agents/skills/coding/{eval-driven-development,agent-trajectory-eval,output-validation}.skill.md`, `agents/skills/ai/{llm-as-judge,rag-evaluation}.skill.md`, `agents/skills/security/prompt-injection-defense.skill.md`, `agents/skills/brain/cognitive-testing.skill.md`; upgrade `agents/skills/security/ai-safety-guardrails.skill.md`; new templates `agents/templates/coding/{EVAL_PLAN_TEMPLATE,GOLDEN_DATASET_TEMPLATE,EVAL_RUBRIC_TEMPLATE}.md`; new guides `agents/guides/principles/evaluation-strategy.md`, `agents/guides/security/ai-risk-standards-map.md`; harness `agents/scripts/eval_skills.py` + `agents/skills/<cat>/evals/*.eval.yaml`; new validator `agents/scripts/validate_methodology_graph.py`; `gabbe/main.py` (+ new `run_evals()`/`run_doctor()` modules), `pyproject.toml` (`[evals]` extra), `.github/workflows/{ci.yml (install-matrix + nightly eval),release.yml (release-verify)}`; tests `gabbe/tests/test_{mcp_contract,brain_invariants,loki_shadow}.py`, `scripts/tests/test_{autodetect,one_command_install}.py`; docs `docs/MCP_CONFIGURATIONS.md`, `SECURITY.md`

---

## AI Agent Suggestions & Review (Added Post-EOF)

The master plan is exceptionally comprehensive, heavily focused on backward compatibility, deterministic testing, and rigorous methodology. Based on a holistic review, here are a few areas that could be enhanced or clarified for absolute v1.0 completeness:

### 1. Security & Compliance Integration (Track A)
While Day-0 (Discovery) and Day-2 (Ops/Sunset) are being added, formal **Threat Modeling** (e.g., STRIDE) and **Compliance** (GDPR/CCPA/SOC2) skills are not explicitly named as new skills. 
- **Suggestion:** Consider adding `threat-modeling.skill.md` (Architecture phase) and `compliance-governance.skill.md` (Day-0/Day-2) to explicitly ground security methodology the same way ADD 3.0 and ATAM ground architecture.

### 2. Multi-OS CI for Distribution Scripts (Track D)
Track D mentions Python tests for install/uninstall manifest (`test_install_manifest.py`, etc.). However, there are OS-specific bootstrap scripts (`install.sh`, `install.ps1`, `uninstall.sh`, `uninstall.ps1`) and Node scripts (`bin/install.js`, and potentially a missing `bin/uninstall.js`).
- **Suggestion:** Ensure the `.github/workflows/ci.yml` validates the shell, PowerShell, and npm paths on multiple OS runners (Ubuntu, Windows, macOS) to guarantee these scripts don't bit-rot. Also, consider explicitly adding `bin/uninstall.js` for `npx gabbe uninstall` feature parity.

### 3. Update Failure / Rollback Strategy (Track D)
Track D mentions `update` and tracking backups (`.bak`). `uninstall` restores them.
- **Suggestion:** Explicitly define an automated rollback: if an `update` fails mid-flight (e.g., network timeout, permission error), it should automatically restore from the `.bak` files to leave the system in a known good state, avoiding a partially updated kit.

### 4. Code & Architecture Documentation (Track C)
Track C focuses on release readiness and updating `README.md`, `llms.txt`, and adding extension protocol docs.
- **Suggestion:** For a v1.0 release, ensuring a high-level `docs/ARCHITECTURE.md` (explaining the Python CLI vs. Markdown Kit relationship) exists and is updated would help new contributors understand the codebase structure and "brain inference" patterns at a glance.
