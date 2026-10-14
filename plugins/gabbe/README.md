# GABBE (Claude Code plugin)

GABBE core: 44 agent skills for the everyday engineering loop — spec, plan, TDD, review, research, security, memory and audit, with Brain and Loki mode. Add the gabbe-* topic plugins from the same marketplace for the rest of the 214.

GABBE (Generative Architectural Brain Base Engine) is a Markdown agentic engineering kit. This plugin carries part of its skill library in the Agent Skills format, so Claude Code can load each skill when a task matches its description. The plugin is content only: Markdown skills and the templates they name. It has no hooks, no MCP servers and no executables, and it sends nothing anywhere.

## Install

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe@gabbe
```

Or install single skills with the skills CLI (skills.sh):

```bash
npx skills add andreibesleaga/GABBE -a claude-code
```

Installed as this plugin, `code-review` and `debug` are namespaced (`/gabbe:code-review`). The skills CLI writes them unprefixed to `.claude/skills/`, where they take the place of Claude Code's built-in `/code-review` and `/debug` in that project.

Claude Code keeps each installed skill's name and description in context within about 1% of the context window. This plugin costs about 2,700 tokens per session (`claude plugin details gabbe`): over the budget of a 200k context, where Claude Code drops the descriptions of the least-used skills (nothing fails), and within that of a 1M context.

Version 1.1.1. Generated from `agents/skills/` by `scripts/build_claude_plugin.py`; edit the sources, not these files.

## Skills

- `agent-analytics` — Tracks key performance indicators (KPIs) for AI Agents: Token Usage, Task Duration, Loop Cycles, and Success Rate.
- `agentic-linter` — Enforce architecture layer boundaries defined in AGENTS.md — detect and fix import violations
- `api-design` — Design REST/GraphQL/OpenAPI contracts before implementation — API-first approach
- `arch-design` — Design system architecture from approved requirements — quality attributes, style selection, arc42/4+1 views, ADRs.
- `arch-review` — Review existing architecture (ATAM-lite) against quality-attribute scenarios; find risks, tradeoffs, anti-patterns; report.
- `audit-trail` — Maintain append-only structured audit log of all agent and human decisions and outcomes
- `brain-mode` — Meta-cognitive orchestrator — adds Active Inference, cost-routing, and episodic memory to the SDLC loop (System-2 planning).
- `clarify` — Generate high-quality clarifying questions for any task/step, escalating when self-estimated uncertainty is high.
- `clean-coder` — Enforces Clean Code standards, identifies code smells, and ensures SOLID principles.
- `code-review` — Systematic code review covering security, performance, architecture, and style
- `cost-benefit-router` — Intelligent routing of tasks between Local (OS) and Remote (Cloud) resources based on complexity, privacy, and cost constraints.
- `debug` — Systematic root-cause debugging — reproduce, isolate, hypothesize, fix with TDD
- `decompose` — Decompose specs/plans into atomic, testable tasks — enforces the 15-Minute Rule and populates project/TASKS.md.
- `documentation` — Generate docstrings, JSDoc, API docs, and README updates that reflect current code
- `emerging-tech` — Architecture assistance for 2026-2030 technologies (6G, Matter IoT, Vector DBs).
- `empirical-methods` — Apply empirical and measurement methods to engineering decisions with sound experiment design, honest statistical interpretation, and root-cause analysis.
- `final-review` — Expert end-of-work review — catch errors/gaps/risks and propose optimizations before declaring done.
- `git-workflow` — Conventional commits, PR creation, and quality gate verification
- `integrity-check` — End-to-end 8-dimension verification — requirements through delivery, all aligned and correct
- `knowledge-connect` — Manage knowledge integration via MCP, Vector DBs, and A2A connectors.
- `knowledge-gap` — Detect unknown territory before acting — a research gate forcing authoritative verification of unknown APIs/libraries.
- `loki-mode` — Master multi-agent swarm orchestration — coordinates personas across the 14-phase lifecycle (10-phase core build loop S01–S10, plus Day-0 S00 and Day-2 S11–S13) with checkpoints, memory, and HITL gates.
- `meta-prompting` — Agents optimizing prompts for other agents (Chain of Thought, Tree of Thoughts).
- `persona-selector` — Rank/select the best Loki persona(s) per task; persona delegation, consensus voting, bounded self-refinement — cost-gated.
- `preflight` — Mandated first action — auto-check, load index summaries + memory + cost, recommend the optimal set, then clarify.
- `refactor` — Safe refactoring with test guard — improve code quality without changing behavior
- `req-elicitation` — Structured requirements elicitation — derive complete, verifiable requirements from stakeholder goals (IEEE 29148, IREB, EARS).
- `research` — Find authoritative answers from official docs, RFCs, standards, and academic sources — never from blogs or opinions
- `retrospective` — Run a blameless retrospective — gather a timeline, generate insights, decide a few owned dated actions, and feed lessons into CONTINUITY.md memory.
- `safety-scan` — Active security enforcement — scan for vulnerabilities (SAST), secrets (Gitleaks), insecure deps (SCA) before commit/deploy.
- `sdlc-checkpoint` — Save SDLC milestone snapshot, verify phase gates, advance tracking, and tag git commit
- `secure-coding` — Implementing OWASP Proactive Controls (Input Validation, Output Encoding, AuthZ/AuthN).
- `security-audit` — OWASP Top 10 security audit, SAST/DAST/SCA scanning, secrets detection, and dependency vulnerability check
- `self-heal` — Autonomous diagnose-research-fix-verify loop — up to 5 attempts before human escalation
- `self-optimize` — Tune skill/guide/persona/model selection to the project for quality+cost; gabbe.config.json + autonomy levels + alignment.
- `session-resume` — Cold-start resume — load all memory and project state to continue any interrupted project
- `skills-registry` — Discover, import, and publish skills to/from universal SKILL.md registries (Agent Garden, skills.sh, …) — validated + gated.
- `spec-writer` — Generate Product Requirements Document with EARS syntax and structured ambiguity clarification
- `state-portability` — Dehydrate/hydrate full working state into a portable, agent-agnostic bundle — switch coding agent or LLM and continue.
- `state-preserve` — Continuously persist working state + a resume pointer so a token/time/crash cutoff never loses progress — resume losslessly.
- `system-lifecycle` — Orchestrate the full SDLC from Requirement to Code to Test (Traceability).
- `tdd-cycle` — Red-Green-Refactor TDD loop with mandatory false-positive check
- `threat-model` — STRIDE threat modeling before implementing security-sensitive features
- `update-scan` — Discover new skills/tools/MCPs/models; recommend or auto-adopt the best per scenario within cost + permission bounds.

## Licence

The skills are GABBE content under CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), © 2026 Andrei Nicolae Besleaga. Source: https://github.com/andreibesleaga/GABBE
