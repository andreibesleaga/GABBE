# Changelog

All notable changes to GABBE are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- **GitHits MCP server** added to the catalog (now **66 MCP servers**). GitHits lets
  the agent navigate the open-source code your app depends on — searching, grepping,
  and reading dependency source, docs, issues, PRs, and changelogs without cloning,
  preventing dependency-API hallucination (no API key). Wired into
  `agents/templates/core/MCP_CONFIG_TEMPLATE.json` (Version Control section,
  default-enabled), documented in `docs/MCP_CONFIGURATIONS.md` (per-server guide +
  SWEBOK v4 Construction map), and surfaced as an essential server in `README.md`,
  `docs/README_FULL.md`, `docs/QUICK_GUIDE.md`, `docs/POST_INSTALL.md`, and
  `gabbe doctor` post-install next-steps. Setup: `npx githits@latest init`
  (auto-detect) — docs at <https://docs.githits.com/>.

---

## [1.1.1] — 2026-06-19 — Capability-layer content audit (consistency, accuracy, honesty)

Patch release. A deep semantic/structural audit of the Markdown capability layer
(skills, guides, templates, brain/loki docs) was run and its findings fixed.
Content-only and strictly additive — no public API / CLI / config / DB change;
all six backward-compat gates pass and the emitter golden vault was recaptured.

### Fixed — consistency
- **Unified the SDLC phase model** across skills, guides, templates and `AGENTS.md`:
  the lifecycle is consistently described as **S00–S13 (14 phases = 10-phase core
  build loop S01–S10 + Day-0 S00 + Day-2 S11–S13)**; resume-guards, checkpoint
  tables and `[X]/10` counters now cover S00–S13 so Day-0/Day-2 work is never
  treated as "not a real phase".
- **Unified the human-in-the-loop hard-gate set** to **S00 (GO/NO-GO), S01, S02,
  S07, S08** everywhere (S00 was previously dropped from several "canonical" lists).
- **Coverage gate** stated as `>= 99%` consistently; example logs that showed a
  sub-99% run as `PASS` were corrected.
- **`AGENTS_TEMPLATE.md` re-synced to the live operating spine** (Step 0 Preflight,
  the CRITICAL MANDATES, RESUME_POINTER continuity, Self-Evolving policy, Loki/Brain
  orchestration), honouring `AGENTS.md`'s "both modes share the same spine" invariant.
- **De-duplicated overlapping guides** (`design-patterns`↔`software-design-patterns`,
  `agentic-patterns`↔`agentic-design-patterns`) to a single source of truth + pointers.

### Fixed — accuracy & honesty
- **Brain/Active-Inference honesty**: `ADR-0002`, `beyond-llms.md`,
  `agent-only-cognition.md` and the `cost-benefit-router` skill now describe the
  **actual** mechanism (epsilon-greedy bandit + single-parent LLM rewrite; no
  crossover/culling; `gabbe route` is a separate one-shot decision) and label
  Active-Inference/Free-Energy framing as *framing, not implemented math*; removed
  "guarantees correctness"/"mathematically guarantees" superlatives.
- **Security/crypto**: corrected an inverted allow-list instruction; replaced a
  non-existent tool name (`Rebertha` → **Presidio**); down-ranked known-weak prompt
  defenses; fixed Ed25519/X25519 conflation, `RFC 7807`→`RFC 9457`, CRYSTALS-Kyber→
  **ML-KEM (FIPS 203)**, added a post-quantum/crypto-agility note; pseudonymization vs
  anonymization; keyed-HMAC blind indexing.
- **Restored a corrupted architecture diagram + step list** in `ai-agentic.md`.
- Fixed broken capability references, the "Lethal Trifecta" misuse in
  `critical-systems-arch.md`, conflicting monolith→microservices thresholds, stale
  frontier-model names, several typos, and markdownlint blank-line compliance.

> Lower-severity stylistic items remain tracked; this release clears every blocker
> and major finding from the audit.

---

## [1.1.0] — 2026-06-19 — Install safety, brownfield mode, fuller population, broader tests

Minor release. New features and a hardened install/uninstall contract. Backward
compatible: the public API / CLI / config / DB / emit schema remain additive
(all six backward-compat gates pass); the only intentional emitted-artifact
change is a richer `agents/AGENTS.md` (more fields populated), with the Gate 4 /
golden baseline recaptured to match.

### Fixed (pre-release content audit)
- **Markdown compliance** in `agents/AGENTS.md` and `AGENTS_TEMPLATE.md` — headings,
  fenced code blocks, and lists are now surrounded by blank lines (markdownlint
  MD022/MD031/MD032); whitespace-only.
- **Restored a corrupted diagram + step list** in `guides/ai/ai-agentic.md` (stray
  skill-table fragments had been spliced into the architecture diagram and the SDD
  Phase-3 numbered list).
- **Corrected an inverted security instruction** in `secure-coding.skill.md`
  (allow-list now reads "accept known **good** characters", not "bad").
- **Replaced a non-existent tool name** (`Rebertha` → **Presidio**) in
  `ai-safety-guardrails.skill.md`.
- **Fixed broken capability references**: `backend-coder` → `eng-backend`,
  `arch-architect` → `prod-architect`, `architecture-design` → `arch-design`.
- **Corrected a quality-gate example** that showed `84% coverage | PASS` against a
  ≥99% coverage gate (now `99%`).

### Added
- **Never-clobber install.** Both install paths (the Python wizard
  `scripts/init.py` and the Node installer `bin/install.js`) now back up any
  differing pre-existing file to `<name>.gabbe-bak` before refreshing it, so a
  project's existing `docs/`, agent rule files, etc. can never be silently lost.
  A new `--force` flag opts into re-templating preserve-set files (still backed
  up first).
- **Reversible wizard installs.** The wizard now records everything it creates
  under the project (copied kit files, wiring symlinks, generated skill trees,
  config files) into `.gabbe/manifest.json`, so `gabbe uninstall` fully reverses
  a wizard install and restores any backed-up user file.
- **Brownfield autodetect + refactor mode.** `gabbe/detect.py` sniffs the target
  for an existing codebase (language/framework/package-manager/git). When one is
  found the wizard asks a greenfield-vs-refactor Mode question, prefills detected
  defaults, and in refactor mode scaffolds a `BROWNFIELD_ONBOARDING.md` discovery
  brief instead of greenfield mission docs.
- **Fuller placeholder population.** Derivable `[PLACEHOLDER:]` fields in
  `AGENTS.md` (dev/test/lint/format/typecheck/coverage commands, `repo_url`,
  `ci_cd`, `deployment_target`) are filled from your answers and detection.
  Genuinely project-specific fields are kept but tagged `<!-- OPTIONAL -->` and
  reported in an end-of-install warning — never shipped as silent blanks.

### Fixed
- **Uninstall no longer follows symlinks.** `_resolve_within` resolves the parent
  only, so wired entries (e.g. `.cursorrules`, root `AGENTS.md`) are removed
  directly instead of being dereferenced and left behind.
- **Uninstall preserves user edits.** A user-modified installed file is backed up
  to `<name>.gabbe-bak` (with a warning) instead of being silently deleted, and
  now-empty wiring directories (`.claude/`, etc.) are pruned.

### Tests
- New end-to-end coverage: never-clobber/backup (Python + a zero-dependency Node
  e2e), wizard manifest round-trip, brownfield detection + wizard flow, placeholder
  population, MCP-over-stdio (handshake/auth/`serverInfo.version`), markdown-plane
  emission, a slow wheel-build-and-install sandbox, a wizard-flow snapshot, and
  mermaid diagram validation.

---

## [1.0.3] — 2026-06-18 — Kit-version stamps refreshed; emitter golden vault recaptured

Patch release. Supersedes 1.0.2 (whose `GABBE CI` run was red — the kit-version
stamp bump below changed byte-frozen emitter artifacts without recapturing the
golden baseline). Strictly additive to the public API / CLI / config / DB / emit
schema; the kit-version-stamp change is an intentional, reviewed content update
to emitted artifacts, with the Gate 4 / golden baseline recaptured to match.

### Changed
- **Kit-version stamps now read 1.0.3** in `agents/AGENTS.md`,
  `agents/CONSTITUTION.md`, and `agents/templates/coordination/AGENTS_TEMPLATE.md`
  (they had drifted to 0.9.6 / 0.8.0). `scripts/registry_export.py` and
  `agents/scripts/state_export.sh` read this stamp, so exports now report 1.0.3.
- Recaptured the emitter golden baseline (`scripts/tests/golden/baseline_v0.8.0`)
  so the golden-emitter tests and **Gate 4 (emitter fixture vault)** stay green
  with the refreshed stamps.

### Fixed
- Carries forward the 1.0.2 fix: MCP `serverInfo.version` reads
  `gabbe.__version__` dynamically (no drift from the package version).

---

## [1.0.2] — 2026-06-18 — MCP server version no longer drifts from the package

Patch release. Strictly additive — no public API / CLI / config / DB / emit
change; the backward-compat gates stay green.

### Fixed
- **MCP `serverInfo.version` reported `1.0.0` on the published `gabbe` 1.0.1.**
  The version string in `gabbe/mcp_server.py` was hardcoded and was not bumped at
  release time, so an MCP client calling `initialize` saw `1.0.0` even though
  `gabbe --version` reported `1.0.1`. The server now reads `gabbe.__version__`
  dynamically, so `serverInfo.version` always tracks the package version and
  cannot drift again.

---

## [1.0.1] — 2026-06-17 — Registry publish (`gabbe-kit` on npm) + install-doc accuracy

Patch release. Registry publishing is now live and all install channels were
audited end-to-end. Strictly additive — no public API / CLI / config / DB / emit
change; the 6 backward-compat gates stay green.

### Changed
- **npm package is now `gabbe-kit`** — `npx gabbe-kit init`. npm's name-similarity
  policy refuses the unscoped `gabbe`, so the npm channel ships as `gabbe-kit`. The
  **PyPI package and the installed command stay `gabbe`**; the package exposes both
  `gabbe` and `gabbe-kit` bins, so the `gabbe` command is unchanged.

### Fixed
- **Shell / PowerShell bootstrap** (`install.sh`, `install.ps1`) `exec`'d
  `npx --yes gabbe init` (404) — corrected to `gabbe-kit`, restoring the
  `curl … | sh` install channel.
- CLI hints in `gabbe/main.py` (and the `MANIFEST.in` / `pyproject.toml` comments)
  now point to `npx gabbe-kit init`.

### Docs
- README documents all four install channels explicitly (npm / PyPI / shell / git).
- Corrected install-channel claims to match audited behavior: manifest-backed
  `update` / `uninstall` is scoped to the Python `gabbe` CLI path — the
  `npx` / `curl` / `scripts/init.py` installs are not manifest-tracked (remove
  manually); `pip install gabbe` installs the **CLI only** (the kit lands via
  `npx gabbe-kit init` / `curl … | sh` / a checkout, and `gabbe setup` wires the
  kit only from a checkout).

---

## [1.0.0] — 2026-06-17 — Cradle-to-grave ADLC, evals & guardrails, advanced testing, reversible multi-OS install

The v1.0 release. Strictly **additive and backward-compatible**: all 6 CI gates
(api-surface, cli-help, config-schema, db-schema, emitter-vault, cve-delta) and
the additive-only emit pipeline stay green — no public API/CLI/config/DB/emit key
is removed or retyped, so existing agents, prior-version projects, and existing
procedures keep working unchanged. v1.0 broadens the methodology layer to the
**entire** lifecycle (S00–S13), adds an evaluation + standards-grounded guardrails
layer, deterministic property/fuzz/chaos/mutation testing, hardened self-*
capabilities, and a fully reversible, autodetecting, multi-OS install/update/
uninstall path.

> **Honesty note (carried into the skills themselves):** PBT/metamorphic tests and
> evals **sample** an input space and **raise confidence** — they do **not** prove
> correctness. LLM-as-judge is biased-but-useful and is calibrated against human
> labels, never treated as ground truth (`pass^k`/`pass@k` reliability is reported,
> never "proof"). The AI-risk standards map documents **coverage, not
> certification**. v1.0 claims best-in-class coverage, not mathematically guaranteed
> 100% correctness.

> **Distribution note:** the npm package ships as **`gabbe-kit`** (`npx gabbe-kit init`)
> because npm's name-similarity policy refuses the unscoped `gabbe`. The installed
> command and the PyPI package remain **`gabbe`** (`pip install gabbe`, then `gabbe …`).

### Added — Methodology layer
- **Cradle-to-grave ADLC.** New **Day-0 phase S00 — Strategy & Discovery** (opportunity
  framing, ideation, Wardley mapping, market scan, North-Star/HEART, RICE; go/no-go
  human gate before S01) and **Day-2 phases S11–S13** (S11 Operate & Maintain, S12
  Evolve & Continuously Improve, S13 Decommission & Sunset) extend the existing
  S01–S10 SDLC end to end.
- **~19 new skills** grounded in named industry methods — **ADD 3.0** (`attribute-driven-design`),
  **ATAM** (explicit in `arch-review`), **Wardley/JTBD/RICE/North-Star** (`opportunity-assessment`,
  `user-research-synthesis`, `ideation-facilitation`), **DORA/SPACE** (`product-analytics`),
  **ADKAR** (`change-management`), plus `estimation-sizing`, `financial-governance`,
  `fitness-functions`, `spec-driven-development`, `retrospective`, and the Day-2 ops
  set (`observability-stack-setup`, `feature-flag-management`, `runbook-authoring`,
  `dependency-lifecycle`, `decommission-sunset`). Self-contained prose, no inline
  citation URLs.
- **New mid-phase quality gates:** **S02.5** Cost & Feasibility, **S04.5** Parallelism/
  Dependency feasibility, **S06.5** Performance-regression, **S07.5** Sustainability
  (green-software) — documented in `loki-sdlc-phases.md` and `orch-judge`.
- **2 new personas:** `prod-product-ops` (Day-2 metrics/analytics/experimentation owner;
  wired into S11/S12) and `prod-integration` (third-party integration / vendor-SLA
  architect; wired into S02/S03/S05).
- **~13 new templates** (estimation, ADD workbook, fitness function, retrospective,
  runbook, dependency graph, experiment plan, change-management plan, decommission
  plan, property-test checklist, eval plan/golden-dataset/rubric), each registered in
  `agents/templates/00-index.md` and wired to the phase/skill that produces it.

### Added — MCP ecosystem (SWEBOK v4 priority map)
- **8 new opt-in MCP servers** in `MCP_CONFIG_TEMPLATE.json` (now 65 total): `knowledge-graph-memory`
  (Anthropic persistent memory), `mcp-evals` (↔ `eval-driven-development.skill`), `mcp-chaos-rig`
  (↔ `chaos-fault-injection.skill` + `gabbe verify --chaos`), `supabase`, `pagerduty` (Day-2 S11),
  `cloudflare`, `obsidian`, `discord`, plus `google-genai-toolbox`.
- **SWEBOK v4 priority map** in `docs/MCP_CONFIGURATIONS.md` — best self-hostable servers mapped to
  the software-engineering knowledge areas, each tied to a GABBE phase/skill.
- `time-complexity` documented as a **local-GitHub** MCP server (build from source); `semgrep` and
  `google-genai-toolbox` annotated with local-install steps.

### Added — SWEBOK v4 alignment, agentic-AI patterns & AI assurance
- **SWEBOK v4 foundations** — full coverage of all knowledge areas via skills `professional-practice`
  (ACM/IEEE-CS ethics), `empirical-methods` (measurement/experiment design), `configuration-management`
  (SCM discipline), and guides `mathematical-foundations`, `computing-foundations`, `modeling-methods`.
- **Agentic-AI skills** — `context-engineering` (Write/Select/Compress/Isolate, prompt caching),
  `ai-red-teaming` (offensive testing, ASR gating, PyRIT/Garak/Promptfoo), `agent-sandboxing`
  (four-domain intrinsic isolation, locked at creation), `reasoning-patterns` (CoT/ToT/ReAct/Reflexion
  selection), `agent-workflow-patterns` (chaining/routing/parallelization/orchestrator-workers/
  evaluator-optimizer; workflow-vs-agent decision).
- **Agentic-AI guides** — `agent-identity-trust` (KYA, OAuth-for-agents, signed mandates, A2A/AGNTCY),
  `model-customization-decisions` (prompt vs RAG vs fine-tune, SLMs, routing/cascades), plus two
  catalogs: `agentic-design-patterns` (full agentic taxonomy) and `software-design-patterns`
  (classical GoF / architectural / DDD / enterprise-integration patterns).
- **AI-assurance templates** — `MODEL_CARD`, `DATASHEET`, and `SYSTEM_CARD` to make governance concrete.
- **Standards map expanded** — ISO/IEC 5338 (AI lifecycle), 23894 (AI risk), 25059 (AI quality), 22989,
  IEEE 7000-series, NIST AI 600-1 (GenAI Profile), EU AI Act GPAI Code of Practice, Google SAIF→CoSAI;
  `agent-communication` refreshed for the converged protocol stack (A2A→Linux Foundation, AGNTCY /
  Internet-of-Agents, MCP OAuth authorization).
- **Post-install workflow** — `gabbe doctor` prints which MCP servers to enable + how; new
  `docs/POST_INSTALL.md` full environment-setup guide.
- **Methodology upgrades** — predictive cost admission control (reserve→reconcile), multi-agent
  topology-selection matrix + named swarm failure modes, and a grounded-self-critique rule (reflection
  loops require an external anchor) folded into the existing orchestration/patterns skills.
- **Security hardening** — installer agent-name validation + path-containment (the isolation invariant
  holds even against a tampered manifest), with regression tests.

### Added — Evaluation & guardrails (Track E)
- **Eval methodology skills:** `coding/eval-driven-development` (offline eval suites,
  golden datasets, 3-tier assertions deterministic→semantic→LLM-judge, `pass@k`/`pass^k`
  statistical gating), `ai/llm-as-judge` (rubric scoring + known-bias mitigations),
  `ai/rag-evaluation` (Ragas-grounded faithfulness/relevance/context precision-recall),
  `coding/agent-trajectory-eval` (tool-selection precision/recall/F1, trajectory
  in-order match; τ-bench / SWE-bench Verified grounding).
- **Self-eval harness** `agents/scripts/eval_skills.py` (no new core dep; assertions-only
  per-commit, optional LLM-judge under `live_llm`/nightly; emits a JSON scorecard) +
  promptfoo-compatible `agents/skills/<cat>/evals/*.eval.yaml` golden datasets; optional
  **`gabbe eval`** subcommand (new public `run_evals()`).
- **Standards-grounded guardrails:** `security/prompt-injection-defense` (direct vs.
  indirect injection, lethal trifecta, dual-LLM/quarantine, spotlighting; OWASP
  **LLM01:2025**) and `coding/output-validation` (schema-validated output, constrained
  decoding, PII masking; OWASP **LLM05/LLM02**); `ai-safety-guardrails` upgraded with the
  input/output/dialog/retrieval/execution rails taxonomy.
- **`agents/guides/security/ai-risk-standards-map.md`** — coverage map of every GABBE
  skill/gate/persona to **OWASP LLM Top 10 (2025)**, **NIST AI RMF (+ GenAI Profile)**,
  **MITRE ATLAS**, **ISO/IEC 42001**, and the **EU AI Act** (documents coverage, not
  certification).
- **MCP contract hardening:** every string tool input bounded by charset + length
  (`pattern` + `maxLength`); `test_mcp_contract.py` proves schemas valid + adversarial
  payloads fail-closed.
- **Cognitive-mode tests:** `test_brain_invariants.py` and `test_loki_shadow.py`
  (mutually-exclusive states, toy convergence, resume-pointer integrity, loop/resource
  guards, confidence-threshold escalation, self-heal→restore) + new
  `brain/cognitive-testing` skill.
- **`agents/scripts/validate_methodology_graph.py`** — lifecycle state-machine DAG +
  persona-handoff graph + memory state model + skill-shape validator, joining the
  `validate_*`/`verify_*` suite.

### Added — Advanced testing (Track B)
- **Hypothesis property-based test suites** for `budget`/`sync`/`route`/`replay`
  invariants (budget cap never exceeded, sync idempotency/convergence, route
  PII→LOCAL + complexity threshold, replay round-trip).
- **MCP fuzzing** (`hypothesis-jsonschema` against the validated `run_command` handler +
  malformed JSON-RPC envelope fuzzing).
- **Chaos / fault injection** (subprocess timeout, sqlite `OperationalError` mid-txn,
  LLM failure → assert escalation/hardstop/rollback).
- **Mutation testing** (`mutmut`, nightly/non-blocking) and `slow`/`live_llm`/`mutation`
  pytest markers.
- **`gabbe verify --chaos`** — new public `run_chaos_checks()` runs the fault-injection
  self-checks (additive flag; only `cli_help/verify.txt` baseline regenerated).

### Added — Distribution (Track D)
- **`.gabbe/manifest.json` install manifest** recording exactly what each installer
  created (path/kind/points_to/agent/hash/backup_of/versions) — the backbone of
  reversibility.
- **Multi-target install:** project (default), `--global`
  (`$XDG_DATA_HOME/gabbe`, refcounted), and `--dir <abs-path>` custom scope, with a
  tested isolation invariant (nothing written outside the chosen target unless
  `--global`).
- **`uninstall` / `update`** (`npx gabbe-kit …`, `gabbe …`, plus `uninstall.sh`/`uninstall.ps1`):
  manifest-driven, idempotent, restores `.bak` backups, never touches preserve files
  (`memory/*`, `project/*`, `policies.yml`, `AGENTS.md`/`CONSTITUTION.md` edits);
  `--dry-run`, `--purge`, `--remove-agents <list>` deselection.
- **`gabbe doctor`** — single read-only environment + install report that autodetects
  OS/arch, runtimes, installed agent clients, chosen scope, and manifest integrity, with
  a PASS/FAIL per check; multi-OS install verification (`{ubuntu, macos, windows}` ×
  `{npx / pip|pipx / curl|sh | install.ps1}`) plus post-publish `release-verify` of the
  real published artifact.

### Added — Self-* hardening (Track C)
- **Honest self-* guides:** `agents/guides/ai/self-evolving-skills.md`,
  `agents/guides/ai/dynamic-capability-loading.md` (load-or-ask-the-user flow), and
  `agents/guides/processes/extension-protocol.md` (the canonical additive way to add a
  skill/template/persona/guide/agent-client/MCP/model without a breaking change).
- Each self-* capability (self-evolving, self-adaptive, self-healing, dynamic capability
  loading) is paired with an executable proof scenario, and the **"brain inference via
  skills" / self-evolving genes** framing is stated honestly: the production
  `gabbe/brain.py` is epsilon-greedy with a monotonic success-rate, and the free-energy /
  Active-Inference framing is conceptual, not literal math.

## [0.9.6] — 2026-06-12 — Operating spine, universal install, more agents, registry interop

Strictly backward-compatible with the last released tag, v0.8.0-beta (6 gates +
golden + validators green). All new behavior is additive; the only removals are
pre-release internals that never shipped in any tagged release (see Removed).

### Added — operating spine (markdown, runtime-agnostic)
- **`core/preflight`** (mandated Step 0): auto-check + load index summaries + memory
  headers + cost posture + recommend the optimal capability set, then clarify.
- **`core/clarify`**: uncertainty-aware clarifying questions at every step + a
  reasoning-pattern menu.
- **`core/state-preserve` + `core/state-portability`** (+ `state_export.sh` /
  `state_import.sh`): continuous + pre-cutoff checkpointing (RESUME_POINTER) so a
  token/time/crash cutoff never loses progress; portable, agent-agnostic state
  export/import to continue in any other coding agent/LLM.
- **`core/update-scan`**: discover + adopt the best skills/tools/MCPs/models, gated
  by `GABBE_AUTONOMY` + budget; A2-only evolution + misaligned-replay guard;
  protected files; policy-as-code self-enforcement.
- **`coordination/persona-selector`** (selection/tiering/delegation/voting) +
  **`coordination/self-optimize`** (autonomy levels L0–L3 + macro/meso/micro alignment).
- **`core/skills-registry`** + **`core/final-review`** skills.

### Added — first-class concerns
- **Observability**: AGENTS.md/CONSTITUTION mandates + OTel GenAI semantic
  conventions in `gabbe/audit.py` (`genai_usage_attributes`, `record_genai_usage`,
  content-redaction toggle).
- **Spec-Driven**: spec → evals → test → code; EARS; golden-thread traceability.
- **Human–Agent Collaboration**: manager-not-operator; Purpose/Transparency/Control
  (`guides/principles/human-agent-collaboration.md`, `guides/ai/agent-operating-ergonomics.md`).

### Added — agents, install, registry, CLI
- **Six more coding agents**: Antigravity, OpenCode, Zed, Continue, Roo Code,
  Kilo Code (Gemini split out, backward-compatible); universal `.agents/skills/`
  emitter; new golden platforms `antigravity` + `opencode`.
- **Universal install**: `npx gabbe-kit init` (`bin/install.js`), `install.sh` /
  `install.ps1`, `MANIFEST.in` (kit in sdist), `release.yml` (wheel + npm + tarball).
- **Skills-registry interop**: `scripts/registry_export.py` / `registry_import.py`;
  `gabbe registry publish|add` + `gabbe setup` CLI verbs.
- **Per-project policy**: `GABBE_AUTONOMY` + `project/gabbe.config.json`
  (`gabbe/config.py`); pre-step cost reservation `budget.reserve()`/`can_afford()`.
- **`scripts/verify_all.sh` + `TESTING.md`**: one-stop verification + how-to-test.

### Security — release-hardening sweeps (PRs #13–15)
- **Policy engine fail-closed**: a present `policies.yml` with no/empty/null
  `tools` section now denies all (was allow-all / crashed on `tools:` null).
- **Audit redaction closure**: OTel `gabbe.input`/`gabbe.output` span attributes
  are redacted like the JSONL path; non-JSON-serializable objects are
  stringified-then-redacted so `__str__` output can't smuggle PII/secrets past
  `json.dumps(default=str)`.
- **`state_import.sh` hardening**: fatal portable `mktemp` template (no
  predictable temp dir), `pipefail`, `--no-same-owner --no-same-permissions`
  extraction; symlink/hardlink + traversal members already rejected.
- **`setup-context.ps1`**: link detection by `LinkType` (SymbolicLink / Junction /
  HardLink) — never moves a real file/dir mistaken for a link.
- **Consistency gate** grown to 8 invariants (dangling concrete-path scan with
  `agents/` prefix handling, guides-count parity, fence balance, persona
  resolution, gate-label drift, …).

### Changed — typing + hardening pass (Gemini/Antigravity audit + follow-ups)
- **`gabbe/` core fully typed**: `mypy --strict` clean across all 23 core modules.
- **`brain.py`**: gene selection now implements the documented epsilon-greedy
  policy (20% exploration of the newest generation) instead of pure greedy.
- **`sync.py`**: Windows-safe atomic writes (`os.replace` PermissionError retry).
- **`gateway.py`**: tool-argument validation is fail-closed — a parameterized
  tool refuses to execute when `jsonschema` is unavailable (and `jsonschema>=4`
  is now a required dependency, so it always is available on a normal install).
- **`llm.py`**: opt-in `GABBE_LLM_CACHE` (cache identical deterministic LLM
  calls locally; 0 tokens on a hit; off by default) + malformed-JSON handling.
- **New checks**: `scripts/tests/test_capability_layer.py` (kit-wide link +
  frontmatter CI test); `scripts/fill_placeholders.py` interactive setup utility.
- **`update-scan.skill.md`**: self-evolution git-branching workflow (never
  mutate `main`; `evolve/{feature}` branch + tests + human review before merge).
- New regression tests: `GABBE_AUTONOMY` precedence (env > project config >
  `hybrid`), `budget.reserve()` semantics, real-jsonschema gateway validation.

### Removed — pre-release internals (never shipped in a tagged release)
- `gabbe.audit.traced` decorator, `gabbe.config.SKILLS_DIR`,
  `gabbe.config.UNDERLINE` (unused internals; the public span API is
  `start_span`/`end_span`).

## [0.9.0] — 2026-06-10 — Audit Hardening (strict backward-compatible)

### Security
- **MCP server fail-closed by default** (was unauthenticated + allow-all): `gabbe serve-mcp` now blocks commands unless `GABBE_MCP_ALLOWED_COMMANDS` is set and requires a token; `GABBE_MCP_INSECURE=1` restores legacy behavior. Added a subprocess timeout and MCP `protocolVersion` (2025-11-25).
- Skill-name slug sanitization blocks path traversal in the emitter.
- Audit logs (`project/logs/*.jsonl`) now redact emails/keys/tokens.

### Added
- **Dual license**: Apache-2.0 (`LICENSE-CODE`) for code + CC-BY-SA-4.0 for content; SPDX headers on all `.py`.
- `docs/SCHEMA.md` (emitted-format contract), `SECURITY.md`, `CODE_OF_CONDUCT.md`, `docs/adr/` (3 ADRs).
- Golden emitter tests + `scripts/gates/` backward-compat gate harness.
- `requirements-lock.txt` (hashed); ruff/black/mypy tooling; `init.py --bench`.
- CI: docs-lint, security-baseline (osv/pip-audit/trivy), scorecard, SBOM release, dependabot; Python matrix 3.8–3.13.
- Root `AGENTS.md` + `GEMINI.md` emitters; `gabbe-schema-version` in all emitted artifacts.
- Cross-process advisory lock for `gabbe sync`.

### Changed
- **Claude Code skills now emit `.claude/skills/<name>/SKILL.md` directories** (agent-skills standard) — previously symlinked `*.skill.md` files that Claude Code could not discover. Cursor rules are now agent-requested (no `globs: *`).
- `docs/MCP_CONFIGURATIONS.md`: corrected package names verified against npm/PyPI (2026-06-10).

### Fixed
- Installer no longer clobbers user files on the symlink-fallback path.
- `compile_skills.py` backup `.bak` no longer drops file extensions.

---

## [0.8.0] — 2026-03-05

### Changed
- Refactored directories, filenames, and structure
- Updated README.md and fixed inaccuracies in QUICK_GUIDE.md
- Fixed full docs links

### Added
- **Kit Installation Safeguards**: Upgraded `init.py` with `safe_merge_directory()` to natively block overarching uninstalls and safeguard all files in `project/`, `memory/`, `TASKS.md`, `policies.yml`, and `config.json` when pulling GABBE ecosystem upgrades across Local, Global, and Custom architectures.
- **Time Complexity MCP Integration**: Added `time-complexity-mcp` (Big-O static analysis via tree-sitter) as a first-class capability:
  - New skill: `agents/skills/coding/time-complexity.skill.md`
  - New guide: `agents/guides/patterns/time-complexity-analysis.md`
  - New template: `agents/templates/coding/TIME_COMPLEXITY_REPORT_TEMPLATE.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Security & Code Quality section)
  - Updated all index files, `README.md`, and `README_FULL.md`
- **MCP Configurations Guide**: Created `docs/MCP_CONFIGURATIONS.md` — comprehensive per-server installation, API key setup, and usage guides for all 42+ MCP servers in the template. Cross-referenced from `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`, and `MCP_CONFIG_TEMPLATE.json`.
- **Excalidraw MCP Integration**: Added `@cmd8/excalidraw-mcp` for programmatic Excalidraw diagram creation:
  - New skill: `agents/skills/coding/excalidraw.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
- **Sketch-to-Diagram Pipeline**: Added `mcp-image-recognition` + Excalidraw for converting hand-drawn sketches to formal diagrams:
  - New skill: `agents/skills/coding/sketch-to-diagram.skill.md`
  - New template: `agents/templates/coding/SKETCH_TO_DIAGRAM_TEMPLATE.md`
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Sections 4-5)
  - MCP config entry for `image-recognition` in `MCP_CONFIG_TEMPLATE.json`
- **tldraw MCP Integration**: Added `@talhaorak/tldraw-mcp` for persistent visual canvas (9 tools):
  - New skill: `agents/skills/coding/tldraw-canvas.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 5)
- **Visual Product Design Phase**: End-to-end pipeline for processing visual inputs into structured specs before implementation:
  - New guide: `agents/guides/planning/visual-product-specs.md` (input catalogue, recognition pipeline, output mapping, design readiness gate)
  - New skill: `agents/skills/product/visual-specs.skill.md` (5-phase workflow: collect → recognize → structure → generate → assemble)
  - New template: `agents/templates/product/VISUAL_SPEC_PACKAGE_TEMPLATE.md` (7-section package with design readiness checklist)
  - Updated PRD template: Section 6.1 Visual Data Model + Section 8 tldraw/Visual Spec Package refs
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 7 cross-ref)

### Added (Phase 13: Specialized Systems & Standards)
- **Industry Category**: Added specialized software engineering support for:
  - **Telecom & Networks**: TMF ODA, CAMARA APIs, GSMA eSIM (skill, guide, template).
  - **Healthcare**: HL7 FHIR clinical data exchange (skill, guide, template).
  - **Industrial IoT**: OPC UA, MQTT, Purdue Model (skill, guide, template).
  - **Global Standards**: UN SDGs, ITU-T, OSI/OpenSSF compliance (skill, guide, template).
  - **Engineering Standards**: IEEE, ACM Ethics, ISO/IEC 12207 audits (skill, guide, template).
- **Core Specialized Systems**:
  - **FinOps**: Cloud cost optimization auditing (guide, skill).
  - **Scalability**: Horizontal and Vertical scaling architecture audit (skill, guide, template).
  - **Green Tech & Sustainability**: ESG checks, Carbon intensity (SCI) reporting (skills, guides, template).
  - **Blockchain & DLT**: Smart contract and distributed ledger design (skill, guide, template).
  - **Semantic Web**: RDF/OWL Ontology design for meta-knowledge (skill, guide, template).


### Fixed
- Quote Mermaid node labels with parentheses
- Fixed diagrams
- General CLI, format, and Windows compatibility fixes

### Removed
- Removed Android/iOS installation instructions
- Removed loki leftovers from tests

### Audited & Verified
- Conducted a full GABBE deep-audit to guarantee stability across workflows, codebase, and documentation.
- **Workflows & Logic Verification**: `init.py` handles step 0 / step 1 initialization perfectly. The `gabbe` CLI tool `sync`, `router`, and `status` modes execute accurately.
- **Test Suite Execution**: Checked the baseline test health using `pytest`. **`251 / 251` tests passed** natively with zero regressions.
- **Documentation Parity**: `agents/skills/00-index.md` matches exactly 126 backend `.skill.md` files. `agents/templates/00-index.md` categorizes all 60+ template definitions. Markdown structure tree diagrams (`README.md`, `README_FULL.md`) correctly reflect the recent refactoring.
- **Codebase Cleanliness**: Swept the repository for `TODO`, `FIXME`, and `HACK`. No loose tech-debt markers exist in the source code; they correctly only exist inside rules or testing string assertions.
- **Architectural Purity**: Clean workspace with zero stranded, orphaned, or unused script files left behind.
- **Scripts Validation**: Validated that all 126 skills and 60+ templates exist exactly as advertised with zero broken internal links using `agents/scripts/comprehensive_checker.py` and `validate_skills.py`.
- **CLI Reference Fixed**: Replaced outdated `0.3.0` CLI references across the docs with the actual `0.7.0` version to perfectly reflect the release state.

---

## [0.7.1] — 2026-02-25

### Added — MVA Platform Control Layer
- **`gabbe/budget.py`**: `Budget` and `BudgetEnforcer` — token, cost, tool call, wall-time, and iteration limits per run; pricing loaded from `pricing_registry` table; `BudgetExceeded` exception.
- **`gabbe/hardstop.py`**: `HardStop` — absolute iteration/depth/timeout guards with `tick()`, `remaining_steps()`, and `should_wrap_up()`.
- **`gabbe/policy.py`**: `PolicyEngine` with YAML-driven `ToolAllowlistPolicy`, `RolePolicy`, `ContentSafetyPolicy`, `ParameterRangePolicy`; deny-all secure default when policy file is absent.
- **`gabbe/gateway.py`**: `ToolGateway` — single mediated execution point with rate limiting, circuit breaker, JSON Schema validation, and audit integration.
- **`gabbe/audit.py`**: `AuditTracer` — structured spans to SQLite `audit_spans` + JSONL + optional OTel; `snapshot_budget()`.
- **`gabbe/escalation.py`**: `EscalationHandler` — three modes (`cli`, `file`, `silent`); `EscalationPaused` exception for `file` mode; `[e]dit context` option in CLI mode.
- **`gabbe/replay.py`**: `CheckpointStore` + `ReplayRunner` — deterministic replay from `checkpoints` table; `diff()` to compare two runs.
- **`gabbe/context.py`**: `RunContext` context manager wiring all platform controls together; `from_checkpoint()` for replay.
- **`gabbe/forecast.py`**: `run_forecast()` — project remaining work cost/token estimates; writes to `forecast_snapshots`.
- **New CLI commands**: `gabbe runs`, `gabbe audit`, `gabbe replay`, `gabbe resume`.
- **Schema v3**: 7 new tables — `pricing_registry`, `runs`, `audit_spans`, `budget_snapshots`, `checkpoints`, `pending_escalations`, `forecast_snapshots`.
- **New env vars**: `GABBE_MAX_COST_USD`, `GABBE_MAX_TOKENS_PER_RUN`, `GABBE_MAX_TOOL_CALLS_PER_RUN`, `GABBE_MAX_ITERATIONS`, `GABBE_MAX_WALL_TIME`, `GABBE_MAX_RECURSION_DEPTH`, `GABBE_MAX_RETRIES_PER_TOOL`, `GABBE_POLICY_FILE`, `GABBE_ESCALATION_MODE`, `GABBE_OTEL_ENABLED`, `GABBE_SUBPROCESS_TIMEOUT`, `GABBE_MCP_TOKEN`, `GABBE_MCP_ALLOWED_COMMANDS`.
- MCP server: `GABBE_MCP_TOKEN` authentication and `GABBE_MCP_ALLOWED_COMMANDS` allowlist for `run_command`.
- 251-test suite covering all platform control modules (`test_budget`, `test_hardstop`, `test_gateway`, `test_policy`, `test_audit`, `test_replay`, `test_escalation`, `test_context`, `test_brain_integration`).
- `docs/PLATFORM_CONTROLS.md` and `docs/CLI_REFERENCE.md` documenting the full control layer.

### Fixed
- Reasoning token cost calculation for o1/o3-class models (`budget.py`).
- Audit span timestamps now reflect span start time, not end time (`audit.py`).
- Exception detection uses `isinstance()` instead of string matching (`context.py`).
- `EscalationPaused` correctly propagates without double-escalation (`brain.py`).
- Deny-all default when `project/policies.yml` is absent (`policy.py`).
- Forecast zero-tasks division-by-zero and DB connection leak (`forecast.py`).
- Checkpoint replay lookup uses per-node occurrence index (`replay.py`).
- Hash delimiter added in sync state hash (`sync.py`).
- LIMIT query parameterized in `gabbe runs` (`main.py`).

---

## [0.7.0] — 2026-02-19

### Added
- GABBE CLI 0.7.0 (Stable) with Zero-Dependency architecture.
- Full Antigravity / Gemini support.
- Comprehensive Troubleshooting Guide.
- AI-Native Engineering Scenarios guide.
- Self-Healing loop with 5-attempt limit and human escalation.
- Multi-agent swarm (Loki Mode) with 30+ personas.
- 4-layer memory architecture (Working, Episodic, Semantic, Procedural).
- Comprehensive checker scripts for kit integrity.
- GABBE CLI 0.7.0: `gabbe init`, `gabbe sync`, `gabbe status`, `gabbe verify`, `gabbe route`, `gabbe brain`
- Bidirectional `TASKS.md ↔ SQLite` sync with timestamp arbitration (`gabbe sync`)
- Brain Mode with Active Inference loop and Evolutionary Prompt Optimization (`gabbe brain`)
- Cost-Effective LLM Router (`gabbe route`) — LOCAL vs REMOTE decision based on complexity + PII detection
- Self-Healing Watchdog (`gabbe brain heal`) — checks DB connectivity and required project files
- Schema migration system (`schema_version` table) for forward-compatible DB upgrades
- `UNIQUE(title)` constraint on `tasks` table to prevent silent duplicate corruption
- Atomic file writes in `export_to_md` (temp-file + `os.replace`)
- Expanded PII detection patterns (email, phone, SSN, credit card, credential keywords)
- All configurable values exposed via environment variables:
  `GABBE_API_URL`, `GABBE_API_KEY`, `GABBE_API_MODEL`, `GABBE_LLM_TEMPERATURE`,
  `GABBE_LLM_TIMEOUT`, `GABBE_ROUTE_THRESHOLD`
- `[project.optional-dependencies] dev` in `pyproject.toml` for `pytest`
- `[tool.pytest.ini_options]` in `pyproject.toml`
- `scripts/tests/conftest.py` with shared `tmp_project` and `db_conn` fixtures
- Unit test files: `test_config.py`, `test_database.py`, `test_llm.py`, `test_route.py`,
  `test_sync.py`, `test_verify.py`
- CI pipeline now installs the package and runs `pytest scripts/tests/`

### Changed
- `gabbe/verify.py`: `parse_agents_config()` now only reads the `## Commands` section
  of `AGENTS.md`; commands outside that section are silently ignored
- `gabbe/verify.py`: `run_command()` uses `shell=False` with `shlex.split()` — eliminates
  shell injection risk
- `gabbe/llm.py`: raises `EnvironmentError` when `GABBE_API_KEY` is unset (was silently
  returning a mock string)
- `gabbe/llm.py`: default model updated from `gpt-4-turbo-preview` → `gpt-4o`
- `gabbe/status.py`: reads `current_phase` from `project_state` table (was hardcoded)
- `gabbe/brain.py`: `run_healer()` performs real checks (was a stub returning 100% Nominal)
- `gabbe/brain.py`, `gabbe/status.py`: DB connections closed with `try/finally`
- `gabbe/sync.py`: handles "both empty" edge case explicitly; multi-format timestamp
  parsing; atomic file export
- `gabbe/config.py`: removed `MAGENTA = '\033[95m'` duplicate of `HEADER`; added
  `LLM_TEMPERATURE`, `LLM_TIMEOUT`, `ROUTE_COMPLEXITY_THRESHOLD`, `PROGRESS_BAR_LEN`
- `gabbe/__init__.py`: removed eager imports to prevent side effects on import
- `gabbe/main.py`: all command dispatches wrapped in `try/except` for user-friendly errors

### Fixed
- Shell injection vulnerability in `verify.py`
- Silent mock LLM responses masking missing API key
- Unclosed SQLite connections in `brain.py` and `status.py`
- Non-atomic TASKS.md writes causing potential corruption on crash
- Duplicate `MAGENTA`/`HEADER` ANSI code in `Colors` class
- Dead code `if ... : pass` branch in `init.py`

---

## [0.1.0] — 2026-02-01

### Added
- Initial release of the GABBE Agentic Engineering Kit
- `init.py` Universal Skill Compiler (Cursor, VS Code, Claude Code, Gemini)
- Skill, Template, Guide, and Persona framework (`.agents/` directory)
- `AGENTS.md` + `CONSTITUTION.md` for agent governance
- Multi-platform skill distribution
- Initial documentation: `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`
- Research whitepapers in `docs/`
