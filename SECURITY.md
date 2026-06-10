# Security Policy

## Supported versions

| Version | Supported |
| ------- | --------- |
| 0.8.x   | ✅ |
| < 0.8.0 | ❌ |

## Reporting a vulnerability

Please report security issues **privately** — do not open a public issue.

- Preferred: open a [GitHub private security advisory](https://github.com/andreibesleaga/GABBE/security/advisories/new).

We aim to acknowledge within **5 working days** and to provide a remediation
timeline within **15 working days**. Please allow a **90-day coordinated
disclosure embargo**. Include: affected version/commit, reproduction steps,
impact, and any suggested mitigation.

## API key handling (LLM providers)

GABBE talks to OpenAI-compatible LLM endpoints (OpenRouter by default).

- **Never commit a real key.** Only the `env` template (placeholder, empty
  `GABBE_API_KEY=`) is tracked; real keys belong in a gitignored `.env`.
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

Treat `agents/AGENTS.md` `## Commands` (run by `gabbe verify`) and
`project/policies.yml` as trust boundaries: anything written there is executed.

## Sensitive-data handling (operator responsibility)

GABBE's cost router (`gabbe route`) performs best-effort PII detection before
sending a prompt to a remote model, but the regex patterns are **not a
guarantee**. The operator is responsible for de-identifying inputs and for
compliance with applicable regulation (e.g. GDPR Art. 9) before processing real
data. Audit logs under `project/logs/` may contain prompt/argument payloads;
redaction is applied on a best-effort basis — review your retention policy.
