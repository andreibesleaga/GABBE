<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# GABBE — Features, Value & Innovations (v1.1.1)

> **GABBE** = *Generative Architectural Brain Base Engine* — a universal, runtime-agnostic
> Markdown "agentic engineering kit" that turns any AI coding agent (Claude Code, Cursor,
> GitHub Copilot, Gemini/Antigravity, Codex, OpenCode, Zed, Continue, Roo Code, Kilo Code,
> Windsurf, Cline, Aider) into a **governed software-engineering team**, with an optional
> Python control plane for budgets, policy, audit, and MCP tooling.
>
> **At a glance (v1.1.1):** 214 skills · 86 guides · 100 templates · 36 personas · 24 runtime
> modules · 14 supported agents · install via `npx gabbe-kit init` / `pip install gabbe` /
> `curl …/install.sh | sh` / git checkout.
>
> **Honesty note (by design):** this document follows GABBE's own anti-overclaim doctrine
> (`agents/guides/ai/gabbe-innovations.md`). Where a capability is *framing on top of a simpler
> reality*, it says so. No "guaranteed", "mathematically proven", or "best-in-class" claims.

---

## 1. What it is and why it delivers real value (short summaries)

Each line is a feature → the concrete value it delivers.

- **Runtime-agnostic Markdown kit** — the whole methodology is plain structured Markdown an
  agent reads and follows; **no runtime lock-in**. *Value:* adopt it in whatever coding agent
  your team already uses; nothing to host, no SDK to learn, no migration cost.
- **Universal "write-once, run-everywhere" skill compiler** — one source kit emits the *native*
  format for each agent (`.cursor/rules/*.mdc`, `.claude/skills/<slug>/SKILL.md`,
  `.github/skills/…`, `.gemini/…`, universal `.agents/skills/…`). *Value:* a single, consistent
  engineering standard across a mixed-tool team instead of per-tool rule drift.
- **Cradle-to-grave ADLC** — a 14-phase lifecycle (Day-0 strategy `S00`; core build loop
  `S01–S10`: requirements → architecture → spec → design → implement → test → review →
  integrate → release → production; Day-2 `S11–S13`: operate → evolve → sunset). *Value:* the
  agent is driven by an actual engineering process, not ad-hoc "vibe coding".
- **Human-in-the-loop gates** at `S00/S01/S02/S07/S08`. *Value:* humans stay managers, not
  spectators — approval is required at the expensive/irreversible decision points.
- **Loki Mode — multi-persona "swarm"** — 36 specialized roles (architect, backend, QA,
  security, SRE, …), each with explicit Role / Does-NOT / scope / outputs. *Value:* role
  separation and review discipline that a single undifferentiated prompt doesn't give you.
- **Brain Mode — meta-cognitive planner/router** — a System-2 layer that picks the next
  strategic action and routes work by complexity/budget, wrapping the System-1 SDLC. *Value:*
  cheaper, more deliberate execution (don't use a frontier model or a swarm for trivial work).
- **Four-layer durable memory** — project state, continuity-of-failures, episodic session
  snapshots, and an authoritative audit log, all as files on disk. *Value:* real cross-session
  continuity; the agent stops repeating past mistakes and survives a context/crash cutoff.
- **Portable state export/import** — checkpoint and resume the *same* task in a *different*
  agent/LLM. *Value:* no vendor lock-in mid-project; move work between tools freely.
- **Optional Python control plane (`gabbe` CLI)** — budget enforcement, fail-closed policy,
  an MCP tool gateway, audit tracing, human escalation, and deterministic replay. *Value:* when
  you need *enforced* (not just requested) cost/safety controls, you bolt them on without
  changing the methodology.
- **Spec-driven & test-first** — EARS requirements → evals → tests → code. *Value:* specs become
  executable contracts; less architectural drift, fewer hallucinated requirements.
- **Standards-grounded guardrails** — prompt-injection defense, output validation, an OWASP
  LLM-Top-10 coverage map, and an AI-risk standards map. *Value:* security posture grounded in
  recognized standards rather than ad-hoc rules.
- **Reversible, isolated install** — manifest-backed install/update/uninstall that restores the
  pre-install state byte-for-byte (Python CLI path). *Value:* safe to try and safe to remove.

---

## 2. What's new since `v0.8.0-beta` (the shipped delta → `v1.1.1`)

`v0.8.0-beta` was an experimental, largely single-target Markdown kit. The line below is now a
**published, multi-agent engineering platform** with a typed runtime, hardened security defaults,
universal install, release automation, and CI that catches its own drift.

**`0.9.x` — audit hardening + the operating spine**
- Re-scored the project on an 8-pillar audit rubric (**18/40 → ~36/40**).
- **Dual license** done right: Apache-2.0 (code) + CC-BY-SA-4.0 (content), SPDX headers.
- **MCP server made fail-closed by default** (was unauthenticated/allow-all): token + allowlist
  required, subprocess timeout, protocol version.
- **Policy engine fail-closed**; **gateway fail-closed tool-argument validation** (`jsonschema`
  now a hard dependency); audit-log redaction closure (emails/keys/tokens, incl. OTel attrs).
- **Operating spine** as runtime-agnostic Markdown: mandated `preflight` (Step 0), `clarify`,
  `final-review`, continuous + pre-cutoff `state-preserve`, portable state export/import.
- **`gabbe/` core fully typed** (`mypy --strict` clean on core modules).
- Universal, Python-independent install (`npx`, `install.sh/ps1`), kit shipped in the sdist,
  CI matrix 3.9–3.13, dependabot, **CycloneDX SBOM on release**, OpenSSF Scorecard.

**`1.0.x` — v1.0 release + registry publishing**
- **v1.0.0**: cradle-to-grave ADLC, evals + standards-grounded guardrails, advanced testing,
  one-command multi-OS install with autodetect + `gabbe doctor`.
- **Registry publishing went live**: **npm `gabbe-kit`** (`npx gabbe-kit init`) and **PyPI
  `gabbe`** (`pip install gabbe`); a `vX.Y.Z` tag drives `release.yml` → npm + PyPI + GitHub
  Release (wheel, sdist, npm tgz, kit tarball, SBOM) + a multi-OS post-publish verify.
- Install-doc accuracy + a bootstrap-script fix so `curl …/install.sh | sh` works end-to-end.
- MCP `serverInfo` version now tracks the package (no drift); kit-version stamps refreshed.

**`1.1.x` — install safety, brownfield mode, and a content audit**
- **Never-clobber install**: both install paths back up any differing pre-existing file before
  refreshing it; a `--force` flag opts into re-templating preserve-set files.
- **Reversible wizard installs**: everything created is recorded in `.gabbe/manifest.json`, so
  `gabbe uninstall` fully reverses an install and restores backed-up files.
- **Brownfield autodetect + refactor mode**: sniffs an existing codebase
  (language/framework/package-manager/git) and offers greenfield-vs-refactor.
- **Fuller population**: the wizard fills more `AGENTS.md` fields, tags OPTIONAL, warns on
  unfilled placeholders. Broader test coverage (MCP stdio e2e, wheel-install sandbox, wizard
  snapshot, mermaid validation).
- **v1.1.1 — capability-layer content audit**: a deep semantic/structural pass unified the SDLC
  phase model and HITL gate set across the whole kit, re-synced `AGENTS_TEMPLATE.md` to the live
  spine, de-duplicated overlapping guides, corrected the Brain/Active-Inference docs to match the
  *actual* code (and removed overclaim superlatives), and fixed security/crypto accuracy items.

---

## 3. What's distinctive — "world-first / unlike what else exists"

Framed honestly against the 2026 landscape. These are **distinctive combinations** where we are
not aware of a direct equivalent — *not* bald "world-first" claims. Where the broader market
already does something, it's noted.

1. **A universal *skill compiler* across 14 agents, not a single-agent rule set.** The market has
   plenty of per-agent rule files (`CLAUDE.md`, `.cursor/rules`, Copilot instructions) and curated
   rule packs; **AGENTS.md** itself is now a Linux-Foundation standard. GABBE is unusual in
   *compiling one source kit into each agent's native format* — so a mixed-tool team shares one
   engineering standard. *Distinctive: the breadth (14 targets) + an `agentskills.io` registry
   import/export for sharing skills.*

2. **A methodology kit, not a runtime framework.** MetaGPT, CrewAI, AutoGen, LangGraph, OpenHands
   are Python frameworks you *build agents with*. GABBE is a portable Markdown methodology that
   *drops into the agent you already use* — zero hosting, zero SDK. The role-based "software
   company" idea overlaps with MetaGPT/CrewAI, but those require their runtime; GABBE's 36-persona
   swarm is followed by whatever agent reads the kit.

3. **Whole-lifecycle, not just spec→code.** Spec-driven tools (GitHub Spec Kit, Kiro, BMAD,
   OpenSpec) center on spec → plan → tasks → implement. GABBE includes that (EARS, spec→evals→
   test→code) **but extends to Day-0 strategy and Day-2 operate/evolve/sunset**, plus memory,
   governance, and self-improvement in one kit. Most competitors solve a single slice.

4. **Methodology *and* an optional enforcement runtime, cleanly separated.** Tools are usually
   either a methodology (docs/specs) *or* a runtime (a framework). GABBE ships both: the Markdown
   works alone, and the optional `gabbe` CLI turns "asked-to" conventions (budget, policy,
   tool-allowlist, hard stops) into *fail-closed enforced* controls via an MCP gateway with audit
   tracing and deterministic replay.

5. **A real (if modest) self-improving prompt loop, described honestly.** `gabbe/brain.py` runs
   an **epsilon-greedy bandit over prompt "genes" with LLM-driven mutation and a success-rate
   reward** (Evolutionary Prompt Optimization). What's distinctive isn't the algorithm (it's
   simple) but the **discipline of shipping it with an explicit honesty doc** that separates the
   working loop from the "Active Inference / free energy" *framing* (which is wording, not computed
   math). Truth-in-advertising as a design value is itself rare in this space.

> **Caveat (read with §1).** "Works in any agent" and "swarm" depend on the host agent honoring
> the Markdown; in a pure-Markdown runtime the gates/budgets are strong instructions, not
> environment-imposed guarantees — that's exactly when the optional `gabbe` CLI is worth adding.

---

## 4. Full feature catalog (everything else)

**Methodology & content layer**
- 214 skills (packaged workflows w/ triggers + constraints), 86 guides (language/domain/principles
  expertise), 100 templates (PRD, SPEC, NFR, ADR, C4, test/eval plans, runbooks, …), 36 personas.
- Operating spine: `preflight` (Step 0) → `clarify` → plan → TDD (red/green) → `verify` →
  refactor → log/complete, with a mandated final review.
- Index + frontmatter conventions make skills discoverable and auto-selectable by keyword.

**Cognition & orchestration**
- **Brain Mode** (System 2): meta-cognitive planning, complexity/budget routing (`gabbe route`,
  LOCAL vs REMOTE), epsilon-greedy prompt optimization, self-optimization (autonomy L0–L3 via
  `GABBE_AUTONOMY = ask|auto|hybrid`).
- **Loki Mode** (System 1): the 14-phase SDLC state machine with persona handoffs, per-phase
  checkpoints, quality gates, and human-approval gates.
- Dynamic capability loading (load-or-ask), persona selector, swarm consensus/voting.

**Memory & continuity**
- Four layers: `PROJECT_STATE.md`, `CONTINUITY.md`, episodic `SESSION_SNAPSHOT`s, `AUDIT_LOG.md`.
- `RESUME_POINTER` continuous + pre-cutoff checkpointing; portable state export/import across
  agents/LLMs; recency/relevance retrieval policy.

**Platform / control plane (optional `gabbe` CLI, 24 modules)**
- Budget enforcement (`can_afford()` / `reserve()` pre-step reservation); fail-closed policy
  engine; MCP tool gateway (token + allowlist + arg-schema validation + subprocess timeout);
  audit tracing (OpenTelemetry GenAI semantic conventions, redact-by-default); human escalation;
  deterministic replay; run history; `gabbe doctor` environment report; `gabbe verify --chaos`
  fault-injection self-checks.
- Registry interop: `registry_export`/`registry_import` (agentskills.io), `gabbe registry
  publish|add`, `gabbe setup`.

**Quality, security & release engineering**
- Self-* demonstrated by tests: self-evolving (gene generations), self-adaptive (PII→LOCAL /
  complexity routing), self-healing (chaos escalation/hard-stop).
- Guardrails: prompt-injection defense, output validation, OWASP LLM01–LLM10 coverage map,
  AI-risk standards map; secrets policy; redaction.
- Six backward-compat gates (API surface, CLI `--help` byte-equal, config schema, DB schema,
  emitter golden vault, CVE delta) + golden emitter vault per agent; eval harness
  (assertions-only per-commit; live LLM-as-judge nightly).
- Supply chain: CycloneDX 1.6 SBOM on release, OpenSSF Scorecard, OSV/Trivy/pip-audit, dependabot,
  `requirements-lock.txt`, CI matrix Python 3.9–3.13 on {Linux, macOS, Windows}.

**Install & distribution**
- Channels: `npx gabbe-kit init` (Python-independent), `pip install gabbe` / `pipx` / `uvx`,
  `curl …/install.sh | sh`, `git clone` + `python3 scripts/init.py`.
- Scopes: project / `--global` / `--dir`; never-clobber with `.gabbe-bak` backups + `--force`;
  manifest-backed reversible `update` / `uninstall`; multi-OS post-publish verify.
- 14 target agents incl. universal `.agents/skills/` for any agentskills.io-compatible tool.

---

## Sources (competitive landscape)

- AGENTS.md as an open/Linux-Foundation standard — [deployhq guide](https://www.deployhq.com/blog/ai-coding-config-files-guide), [AGENTS.md vs CLAUDE.md vs Cursor Rules (2026)](https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/)
- Multi-agent SWE frameworks — [MetaGPT](https://github.com/FoundationAgents/MetaGPT), [framework comparison 2026](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared)
- Spec-driven development — [GitHub Spec Kit](https://github.github.com/spec-kit/), [Kiro](https://kiro.dev/), [Martin Fowler: SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
- GABBE internal honesty inventory — `agents/guides/ai/gabbe-innovations.md`, `agents/guides/ai/self-evolving-skills.md`

_Compiled 2026-06-19 for GABBE v1.1.1. Feature counts verified against the repo; novelty framed honestly per GABBE's own anti-overclaim doctrine._
