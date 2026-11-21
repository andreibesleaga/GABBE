# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 1.1.x   | ✅ |
| < 1.1.0 | ❌ |

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

- Preferred: open a [GitHub private security advisory](https://github.com/andreibesleaga/GABBE/security/advisories/new).

We aim to acknowledge within **5 working days** and to provide a remediation
timeline within **15 working days**. Please allow a **90-day coordinated
disclosure embargo**. Include: affected version/commit, reproduction steps,
impact, and any suggested mitigation.

## API key handling (LLM providers)

GABBE talks to OpenAI-compatible LLM endpoints (OpenAI by default; any
OpenAI-compatible provider such as OpenRouter works via `GABBE_API_URL`).

- **Never commit a real key.** No env file is tracked; real keys belong in a
  gitignored `.env` (read by `gabbe/config.py`) or in the process environment.
- **What a project `.env` may set (since 1.1.4).** A `.env` travels with a repository, so
  it is not trusted with security settings. Only these keys are read from it:
  `GABBE_API_KEY`, `GABBE_API_MODEL`, `GABBE_LLM_*`, `GABBE_MAX_*`, `GABBE_LOG_LEVEL`,
  `GABBE_ESCALATION_MODE`, `GABBE_ROUTE_THRESHOLD`, `GABBE_SUBPROCESS_TIMEOUT`. `GABBE_MCP_*`
  and `GABBE_POLICY_FILE` are never read from it, and no other variable (`PATH`,
  `PYTHONPATH`, …) is. `GABBE_API_URL` is read from `.env` only when `GABBE_API_KEY` does
  not come from your shell: otherwise a cloned repository could send your own key to a URL
  of its choosing. A refused `GABBE_*` key is named in a warning; export it in your shell.
- **Never log the key.** `gabbe/llm.py` keeps the key in the `Authorization`
  header only and never logs headers or payloads (see `test_llm_sanitizes_errors`).
- **Use a project-scoped key**; rotate at least every 90 days.
- **Set a hard ceiling at the provider** (billing quota) and via
  `GABBE_MAX_COST_USD` so a misconfigured loop cannot run up unbounded cost.

## The MCP server (`gabbe serve-mcp`) is a privileged surface

`gabbe serve-mcp` exposes a `run_command` tool over stdio. By default it now
runs **fail-closed**:

- **Command allowlist required.** With `GABBE_MCP_ALLOWED_COMMANDS` unset, all
  commands are **blocked**. Set it to a comma-separated list of permitted
  executables (e.g. `GABBE_MCP_ALLOWED_COMMANDS="pytest,ruff,git"`).
- **Authentication required.** With `GABBE_MCP_TOKEN` unset, the server starts
  but refuses tool calls until a token is configured and supplied in the
  `initialize` params.
- **Insecure opt-out.** `GABBE_MCP_INSECURE=1` restores the legacy permissive
  behavior (no auth, allow-all). Use only on a trusted, isolated host. The
  startup banner warns when insecure mode is active.
- **Bounded tool-input contract.** The `run_command` tool input is a single
  hardened JSON Schema (`_RUN_COMMAND_SCHEMA`, enforced by the gateway and
  advertised in `tools/list`): the `command` string is bounded by **charset**
  (a `pattern` forbidding C0 control characters and NUL) and **length**
  (`maxLength`), with `additionalProperties: false` to reject smuggled fields.
  This blunts injection-via-tool-feedback and oversized payloads (per the MCP-38
  threat taxonomy and NSA MCP security guidance) and is regression-guarded by
  `gabbe/tests/test_mcp_contract.py`.
- **An allowlist is not a sandbox.** An entry is matched by name and its arguments are
  not restricted, so allowing an interpreter or a tool that runs code (`python`, `npm`,
  `git`) allows arbitrary commands. The child process inherits the server's environment.
- **Planned for 1.2.0:** read-only tools by default; `run_command` only behind an explicit
  flag.

Treat `agents/AGENTS.md` `## Commands` (run by `gabbe verify`) and
`project/policies.yml` as trust boundaries: anything written there is executed.

## Sensitive-data handling (operator responsibility)

GABBE's cost router (`gabbe route`) performs best-effort PII detection before
sending a prompt to a remote model, but the regex patterns are **not a
guarantee**. The operator is responsible for de-identifying inputs and for
compliance with applicable regulation (e.g. GDPR Art. 9) before processing real
data. Audit logs under `project/logs/` may contain prompt/argument payloads;
redaction is applied on a best-effort basis — review your retention policy.
