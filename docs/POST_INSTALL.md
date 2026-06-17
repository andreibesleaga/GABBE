# Post-Install Setup — Full Environment

After `npx gabbe init` (or `gabbe setup` / `curl … | sh`) lands the kit and wires
your detected agents, run **`gabbe doctor`** for an environment report, then follow
these steps to finish a full setup. Steps are safe for a human OR an agent to execute.

## 1. Verify the install

```bash
gabbe doctor          # autodetects OS/arch, runtimes, agent clients; prints next steps
```

All agent clients GABBE detected are already wired. Anything missing is reported.

## 2. Enable MCP servers (the main post-install task)

GABBE ships a catalog of **65 MCP servers** in
`agents/templates/core/MCP_CONFIG_TEMPLATE.json`. Most are opt-in (`"_enabled": false`).
To enable one: set `"_enabled": true`, fill the listed env vars, and point your agent
at the config (e.g. `.mcp.json`, `.cursor/mcp.json`, or your client's MCP settings).

### Essential (recommended for every project)

| Server | Purpose | Setup |
|---|---|---|
| `context7` | Up-to-date SDK docs (prevents API hallucination) | npx; no key |
| `filesystem` | Read-only project file access (internal RAG) | npx; set root path |
| `sequential-thinking` | Chain-of-thought reasoning | npx; no key |
| `github` | PR review, code search, issue mgmt | npx; `GITHUB_TOKEN` |
| `brave-search` or `tavily` | Authoritative web research | npx; API key |

### Locally-installed servers (clone/build/binary, not a plain npx one-liner)

| Server | How to install locally |
|---|---|
| `time-complexity` | **GitHub server**: `git clone` the time-complexity-mcp repo, `npm install && npm run build`, then set its `args` to the built `dist/index.js`. Big-O time/space static analysis (tree-sitter, no code execution). Pairs with `coding/time-complexity.skill`. |
| `semgrep` | `pip install semgrep-mcp`; runs via `python -m semgrep_mcp`. Static security scanning. |
| `google-genai-toolbox` | Download the `genai-toolbox` (MCP Toolbox for Databases) Go binary from its GitHub releases; run `toolbox --stdio`. |

### Pick servers by lifecycle phase

See the **SWEBOK v4 priority map** in `docs/MCP_CONFIGURATIONS.md` for the best
self-hostable servers per software-engineering area (Requirements/Design,
Construction, Testing/Quality, Operations, Management, Foundations). Highlights:
- **Testing/quality:** `sentry`, `snyk`, `semgrep`, `mcp-evals`, `mcp-chaos-rig`
- **Operations (Day-2):** `pagerduty`, `cloudflare`, `grafana`, `datadog`
- **Memory/RAG:** `knowledge-graph-memory`, `qdrant`, `chroma`

> Security: prod databases must be configured read-only; dev read-write. Keep keys in
> env vars, never in the committed config. Most servers run locally via Docker/Node so
> credentials never leave your host.

## 3. Configure GABBE policy + budgets (optional, for the Python CLI)

If using the optional `gabbe` CLI, set controls via env or `project/gabbe.config.json`:
`GABBE_API_KEY`, `GABBE_AUTONOMY` (ask|auto|hybrid), budgets (`GABBE_MAX_COST_USD`,
`GABBE_MAX_TOKENS_PER_RUN`), and `project/policies.yml` (tool allowlist, fail-closed).
See `docs/PLATFORM_CONTROLS.md` and `docs/CLI_REFERENCE.md`.

## 4. Validate the setup

```bash
gabbe verify              # files + AGENTS.md commands
gabbe verify --chaos      # fault-injection self-checks (resilience)
gabbe eval                # deterministic skill-eval self-check
```

## 5. Updating / uninstalling later

```bash
gabbe update              # additive kit refresh; preserves user files
gabbe uninstall --dry-run # preview the exact, reversible removal
```

See `docs/INSTALL.md` for scopes (project / `--global` / `--dir`) and channels.
