# GABBE architecture

> **Audience:** contributors and maintainers. **Scope:** the parts of this repository, what
> each one reads and writes, and how they connect. The reasons behind the larger decisions
> are in [`docs/adr/`](adr/); the emitted file formats are in [SCHEMA.md](SCHEMA.md).

GABBE has two layers. The **kit** (`agents/`) is Markdown that a coding agent reads; it works
with no code running. Installers copy the kit into a project and compile its skills into
each agent's native format. The optional **CLI** (`gabbe/`, Python) adds enforced budgets,
policy, audit, an MCP server and replay on top of a project's SQLite state.

## Context

```mermaid
flowchart LR
    dev["Developer"]
    agent["AI coding agent<br/>(Claude Code, Cursor, Copilot, Gemini, Codex, …)"]
    mcpc["MCP client"]
    llm["OpenAI-compatible LLM API<br/>(GABBE_API_URL)"]
    reg["npm · PyPI · GitHub Packages<br/>GitHub Releases"]
    subgraph gabbe["This repository"]
        kit["Markdown kit<br/>agents/"]
        inst["Installers<br/>bin/install.js · install.sh · scripts/init.py"]
        cli["Optional CLI<br/>gabbe/"]
    end
    proj[("User project<br/>agents/ · AGENTS.md · .claude/ · .cursor/ …<br/>project/state.db")]

    dev -->|npx gabbe-kit init / curl install.sh / init.py| inst
    inst -->|copies kit, emits per-agent files| proj
    kit --> inst
    agent -->|reads AGENTS.md, skills| proj
    dev -->|gabbe …| cli
    cli -->|reads and writes| proj
    cli -->|HTTPS| llm
    mcpc -->|JSON-RPC over stdio| cli
    gabbe -->|v* tag workflows| reg
```

## Parts of the repository

```mermaid
flowchart TB
    subgraph content["Kit content (agents/)"]
        skills["skills/ · templates/ · guides/<br/>personas/ · memory/"]
        aMd["AGENTS.md · CONSTITUTION.md"]
        ascripts["scripts/<br/>compile_skills.py · setup-context.sh/.ps1<br/>state_export.sh · state_import.sh · validators"]
    end
    node["bin/install.js<br/>(Node installer, npm gabbe-kit)"]
    boot["install.sh · install.ps1<br/>(bootstrap: npx, else init.py)"]
    wizard["scripts/init.py<br/>(interactive wizard)"]
    plugin["scripts/build_claude_plugin.py"]
    regx["scripts/registry_export.py<br/>scripts/registry_import.py"]
    cliPkg["gabbe/ (PyPI gabbe)"]
    gates["scripts/verify_all.sh · scripts/gates/run_gates.sh<br/>gabbe/tests · scripts/tests"]
    out1[("project: agents/, docs/,<br/>AGENTS.md, .agents/skills/")]
    out2[("project: per-agent formats,<br/>.gabbe/manifest.json")]
    out3[("plugins/ ·<br/>.claude-plugin/marketplace.json")]

    boot --> node
    boot --> wizard
    content --> node --> out1
    content --> wizard
    wizard -->|runs| ascripts
    wizard --> out2
    wizard -.->|uses when importable| cliPkg
    content --> plugin --> out3
    cliPkg -->|gabbe registry publish / add| regx
    gates -.->|checks| content
    gates -.->|checks| cliPkg
```

- `bin/install.js` copies `agents/` and `docs/`, writes a root `AGENTS.md`, emits the universal
  `.agents/skills/<slug>/SKILL.md` tree and wires the agents named with `--agents`. It writes no
  manifest ([INSTALL.md](INSTALL.md)).
- `scripts/init.py` asks questions, copies the kit, calls `agents/scripts/compile_skills.py` for
  each selected agent's format, and records what it created in `.gabbe/manifest.json` so
  `gabbe uninstall` can reverse it. It uses `gabbe/detect.py` for brownfield detection when the
  `gabbe` package is importable.
- `scripts/build_claude_plugin.py` turns every `agents/skills/**/*.skill.md` into the Claude Code
  plugins under `plugins/` (generated; never edit by hand).
- The emitter golden vault (`scripts/tests/golden/baseline_v0.8.0`) hashes every file the wizard
  writes, which includes every file under `agents/`. Any change there needs a recapture; see
  [TESTING.md](../TESTING.md).

## The CLI (`gabbe/`)

Each `gabbe` command runs in the project found by walking up from the current directory to the
first folder with `project/`, `.git` or `pyproject.toml` (`gabbe/config.py`). State lives in
that project's `project/state.db` (SQLite, schema v3), span logs in `project/logs/`, policy in
`project/policies.yml`. The arrows are the imports inside the package.

```mermaid
flowchart TB
    main["main.py<br/>(argparse, 19 commands)"]
    subgraph cmds["Command modules"]
        sync["sync.py"]
        verify["verify.py"]
        status["status.py"]
        route["route.py"]
        brain["brain.py"]
        forecast["forecast.py"]
        mcp["mcp_server.py"]
        evals["evals.py"]
        doctor["doctor.py"]
        installer["installer.py"]
    end
    subgraph controls["Platform controls"]
        context["context.py<br/>(RunContext)"]
        budget["budget.py"]
        hardstop["hardstop.py"]
        policy["policy.py"]
        gateway["gateway.py"]
        audit["audit.py"]
        escalation["escalation.py"]
        replay["replay.py"]
    end
    llm["llm.py"]
    cache["cache.py"]
    database["database.py"]
    config["config.py"]
    detect["detect.py<br/>(used by scripts/init.py)"]

    main --> cmds
    main --> audit
    main --> escalation
    main --> replay
    main --> database
    brain --> context
    brain --> gateway
    brain --> llm
    brain --> audit
    brain --> escalation
    brain --> database
    mcp --> context
    mcp --> gateway
    verify --> mcp
    verify --> route
    verify --> hardstop
    verify --> escalation
    route --> llm
    llm --> cache
    llm --> audit
    context --> budget
    context --> hardstop
    context --> policy
    context --> gateway
    context --> audit
    context --> escalation
    context --> replay
    context --> database
    budget --> database
    audit --> database
    escalation --> database
    replay --> database
    sync --> database
    status --> database
    forecast --> database
    database --> config
```

`config.py` (environment variables and paths) is imported by most modules; those arrows are
left out. `evals.py` runs `agents/scripts/eval_skills.py`; `doctor.py`, `installer.py` and
`detect.py` import nothing else from the package. What each control does, with its Python
API, is in [PLATFORM_CONTROLS.md](PLATFORM_CONTROLS.md); every command and variable is in
[CLI_REFERENCE.md](CLI_REFERENCE.md).
