# Quick Commands & Prompts Reference

This guide provides a quick reference for the most common commands, setup instructions, and copy-paste prompts used in the GABBE Agentic Engineering Kit.

## 1. Setup Commands

| Goal | Command | Description |
|---|---|---|
| **Initialize Kit** | `python3 scripts/init.py` | Runs the setup wizard to configure the kit, wire your AI agents (Claude, Cursor, Gemini), and generate `BOOTSTRAP_MISSION.md` (or `SETUP_MISSION.md`) |
| **Manual Wiring (UNIX)** | `./agents/setup-context.sh` | Manually symlinks the skills into your IDE's agent folder. |
| **Manual Wiring (Windows)** | `.\agents\setup-context.ps1` | PowerShell equivalent of the manual wiring script. |
| **Install GABBE CLI (Optional)**| `pip install -e .` | Installs the GABBE CLI 0.2.0 (Stable) locally. |

---

## 2. GABBE CLI 0.2.0 Reference

| Command | Description |
|---|---|
| `gabbe init` | Initializes the SQLite database (run after `scripts/init.py`). |
| `gabbe sync` | Bidirectional sync between `project/TASKS.md` and SQLite DB. |
| `gabbe verify` | Programmable integrity check (files, tests, lint). |
| `gabbe status` | Visual dashboard of project phase and task progress. |
| `gabbe brain activate` | Activates Active Inference loop (requires API key). |
| `gabbe brain evolve --skill NAME` | Evolutionary Prompt Optimization for a named skill. |
| `gabbe brain heal` | Self-healing watchdog: checks DB and required files. |
| `gabbe route <prompt>` | Arbitrates prompt between Local and Remote LLMs (requires API key). |

---

## 3. Top 15 Essential Skills (Trigger Words)

You can invoke these skills directly in your IDE chat (e.g., Cursor, GitHub Copilot) or via Slash Commands (e.g., Claude Code `/tdd-cycle`).

| Phase | Skill | Trigger Word | Purpose |
|---|---|---|---|
| **Product** | `spec-writer` | "write spec", "spec" | Generates PRD.md with EARS syntax. |
| **Design** | `arch-design` | "design architecture" | Generates C4 architecture and `PLAN.md`. |
| **Design** | `threat-model` | "threat model", "stride"| Analyzes security risks using STRIDE. |
| **Tasks** | *(built-in logic)* | "decompose tasks" | Breaks down `PLAN.md` into 15m tasks. |
| **Coding** | `tdd-cycle` | "test", "tdd" | Red-Green-Refactor loop. |
| **Coding** | `debug` | "fix", "debug" | Root Cause Analysis (RCA) and fixing. |
| **Coding** | `refactor` | "refactor" | Safe code restructuring. |
| **Coding** | `vibe-coding` | "vibe", "aesthetic" | Creative, high-fidelity frontend coding. |
| **Review** | `code-review` | "review", "audit" | Security, performance, and style check. |
| **Security**| `security-audit` | "owasp", "audit" | Comprehensive security review. |
| **Security**| `safety-scan` | "safety scan" | Pre-commit safety guardrails. |
| **Core** | `research` | "research", "find" | Deep research using authoritative sources. |
| **Core** | `self-heal` | "fix error" | Autonomous auto-recovery loop. |
| **Modes** | `loki-mode` | "loki", "swarm" | 10-phase SDLC orchestration. |
| **Modes** | `brain-mode` | "brain activate" | Meta-cognitive orchestrator. |

*(For the complete 120+ skills list, see `agents/skills/00-index.md`)*

---

## 4. Common Actions (Copy-Paste Prompts)

Copy and paste these exact prompts into your AI chat window to kick off standard workflows.

### New Project from Scratch
> "Read AGENTS.md. I want to build [description]. Start with spec-writer skill."

**Flow:** Spec → Design → Tasks → TDD Implementation → Security → Deploy

### Resume Existing Project
> "Read AGENTS.md and agents/memory/PROJECT_STATE.md. Resume the project."

### Fix a Bug
> "Read AGENTS.md. Bug: [description]. Use debug skill with TDD."

**Flow:** Reproduce → Root Cause → Failing Test → Fix → Green → Regression Check

### Refactor / Pay Tech Debt
> "Use tech-debt skill on [directory]. Then refactor the top-priority item."

### Security Audit
> "Run security-audit skill on the entire codebase."

### Architecture Review
> "Run arch-review skill. Check for SOLID violations and coupling."

### Software Engineering & System Architecture
> "Act as a Principal Staff Engineer. Review the codebase in [directory] and generate a C4 system architecture diagram (Context and Container levels). Identify any bottlenecks and propose scaling strategies."

> "Use the design-patterns and domain-model skills. We are building a [feature segment]. Propose the optimum architecture pattern (e.g. Event-driven, CQRS, Hexagonal) and define the core domain entities."

### Vibe-Coding (Creative Frontend)
> "Use the vibe-coding skill. Build a [component/page] using [framework]. I want it to feel [aesthetic, e.g. glassmorphism, cyberpunk, sleek corporate]. Include micro-animations and smooth transitions. Prioritize visual WOW over generic utility."

### Activate Brain Mode (Complex Goals)
> "Activate Brain Mode. Goal: [build X / migrate Y / solve Z]."

### Activate Loki Mode (Large Projects)
> "Activate Loki Mode. Goal: [build X / migrate Y / refactor Z]."
