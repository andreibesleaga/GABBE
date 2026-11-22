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

Since 1.2.0 the server is **read-only by default**:

- **On by default:** `list_skills`, `read_skill`, `search_skills`, `get_template` and
  `project_status`. They read only inside `<project root>/agents` and
  `<project root>/project` (the real path is checked, so links pointing outside are
  refused), cap their output at 64 KiB, change nothing, and need no token and no
  allow-list. They are not subject to the tool allow-list in `project/policies.yml`
  because they act on nothing.
- **`run_command` is off by default.** It is registered and listed only with
  `gabbe serve-mcp --enable-run-command` or `GABBE_MCP_ENABLE_RUN_COMMAND=1`.
  `GABBE_MCP_INSECURE=1` does not enable it by itself. Setting a token, an allow-list
  or `GABBE_MCP_INSECURE` without enabling it logs a start-up warning.
- **Once enabled, `run_command` runs fail-closed.** With `GABBE_MCP_ALLOWED_COMMANDS`
  unset, all commands are **blocked**; set it to a comma-separated list
  (e.g. `pytest,ruff,/usr/bin/git`). An entry is a bare command name, which matches
  that name and the one path your `PATH` resolves it to (a lookalike `./git` or
  `/tmp/x/git` does not match), or an absolute path, which matches only that path.
  Paths are compared as written, without following links, so another name linked to
  the same file (a busybox applet, `view` for `vim`) is not permitted.
  The executable is resolved with `PATH` and the resolved path is run.
- **The policy file must allow it too.** `project/policies.yml` must list `run_command`
  under `tools.allowed`; with no policy file the engine denies every tool. The
  installers do not create that file, so enabling `run_command` is always a deliberate
  edit in the project.
- **Authentication for `run_command`.** With `GABBE_MCP_TOKEN` unset, `run_command`
  refuses every call. Legacy clients (MCP `2025-11-25` and earlier) send the token in
  the `initialize` params; modern clients (`2026-07-28`, no handshake) send it in each
  request's `_meta` under `io.github.andreibesleaga.gabbe/token`. A legacy login does
  not authorise modern requests. The read-only tools never need a token.
- **Minimal child environment.** A `run_command` child gets only `PATH`, `HOME`,
  `LANG`, `LC_ALL`, `TERM` and the names listed in `GABBE_MCP_PASS_ENV`;
  `GABBE_API_KEY` and other secrets do not reach it.
- **Insecure opt-out.** `GABBE_MCP_INSECURE=1` makes an enabled `run_command`
  permissive (no token, allow-all). Use only on a trusted, isolated host. The startup
  banner warns when insecure mode is active.
- **Bounded tool-input contract.** Every tool input is a strict JSON Schema (for
  `run_command`, `_RUN_COMMAND_SCHEMA`), enforced by the gateway and advertised in
  `tools/list`: bounded strings, `additionalProperties: false`, and for `command` a
  `pattern` forbidding C0 control characters and NUL. This blunts
  injection-via-tool-feedback and oversized payloads (per the MCP-38 threat taxonomy
  and NSA MCP security guidance) and is regression-guarded by
  `gabbe/tests/test_mcp_contract.py`.
- **Size limits.** A request line over 1 MiB is refused and the rest of it is discarded
  without being held in memory; a deeply nested line gets a parse error (`-32700`) and
  the server keeps running. `run_command` returns at most 1 MiB of standard output and
  1 MiB of standard error: a longer stream is cut, ends with
  `[output cut at 1048576 bytes]`, and the reply carries `stdout_truncated` or
  `stderr_truncated`. The cut applies before the audit trace. The child's standard
  input is closed. The output is read through pipes and the rest is discarded without
  being written to disk; a command that writes more than 16 MiB to one stream is ended.
  On timeout (exit 124) or at that limit the whole process group is ended (SIGTERM, then
  SIGKILL after 0.5 s) on POSIX; on Windows only the child is ended.
- **Search path.** Empty, `.` and other relative `PATH` entries are ignored when a command
  name is resolved and in the child's `PATH`, so an allowed name never runs a file of the
  project folder. A name that cannot be resolved returns 127.
- **State paths that are links.** If `project/`, `project/state.db` or `project/logs` is
  a symbolic link, or leads outside the project, GABBE writes nothing there. The tool
  server then runs without an audit trail (read-only tools only; `run_command` is
  refused and the message names the path). A command-line command that needs the
  database stops with one line and exit status 1.
- **No audit trail, no `run_command`.** In a folder without `project/`, or with a
  database that cannot be opened, the server serves the read-only tools and refuses
  `run_command` with a message; a database that was never initialised is set up at
  start.
- **An allowlist is not a sandbox.** An entry is matched by name or path and its
  arguments are not restricted, so allowing an interpreter or a tool that runs code
  (`python`, `npm`, `git`) allows arbitrary commands. The minimal environment limits
  what the child can read from the server's environment; it does not confine the
  child's access to files or the network.

Treat `agents/AGENTS.md` `## Commands` (run by `gabbe verify`) and
`project/policies.yml` as trust boundaries: anything written there is executed.

## Sensitive-data handling (operator responsibility)

GABBE's cost router (`gabbe route`) performs best-effort PII detection before
sending a prompt to a remote model, but the regex patterns are **not a
guarantee**. The operator is responsible for de-identifying inputs and for
compliance with applicable regulation (e.g. GDPR Art. 9) before processing real
data. Audit logs under `project/logs/` may contain prompt/argument payloads;
redaction is applied on a best-effort basis — review your retention policy.

Since 1.2.0:

- The same payloads are stored in `project/state.db` (table `audit_spans`), not only in
  `project/logs/`.
- Redaction covers the value of any `NAME=value` or `NAME: value` whose name contains
  `password`, `passwd`, `pwd`, `passphrase`, `secret`, `token`, `api_key` or `api-key` (the
  name is kept), JSON members named like secrets, `Authorization` headers, passwords in
  URLs and connection strings, `--password`/`--token`/`--api-key` options, Slack tokens
  and webhooks, Google API keys, GitHub (`ghp_`, `gho_`, `github_pat_` …), npm, GitLab,
  Hugging Face and Stripe tokens, JSON Web Tokens, PEM and OpenSSH private-key blocks, and
  the earlier `sk-`, `AKIA` and bearer shapes. It stays best-effort: it does not cover a
  bare `-pVALUE`, `auth=`, `credentials:`, `Cookie:` headers, or a secret under a name
  that holds none of the words above.
- On POSIX systems GABBE creates `project/logs` with mode 0700, and `state.db` and the
  run logs with mode 0600. Files that already exist keep their mode.

## Untrusted projects, bundles and skill packs

A repository you cloned, a state bundle someone hands you and a skill pack from a
registry are untrusted input. Since 1.2.0:

- The installers, `update` and `uninstall` act only inside the target folder. A path in
  `.gabbe/manifest.json` that is absolute, contains `..`, or leaves the target is
  refused; a record file or state file that is a link is not written through.
- Inside the target the record is not trusted either. An entry is acted on only when it
  is a kind the installers write; a file is removed only when its bytes match the
  recorded hash; a backup is moved back only when it is named `<path>.gabbe-bak` or
  `<path>.bak` and is a real file; only the kit's own hook entries are taken out, and only
  in the settings files the installers write; under `.git/` only the two marked GABBE hooks
  are touched. Every path is checked again right before use.
- The wizard runs the skill compiler of the kit being installed, never a
  `compile_skills.py` found in the target project.
- The uninstall scripts never import a `gabbe/` package from the current folder. The
  bootstrap scripts pin the npm package to their own release and run `npx` from an empty
  temporary folder with `--dir <project>`, so a project's `.npmrc` (`registry=`,
  `node-options`) and its `node_modules` do not decide what runs. Your own `~/.npmrc`
  still applies. If you type `npx gabbe-kit …` inside a project yourself, that project's
  `.npmrc` applies: run it from another folder with `--dir /path/to/project`.
- `state_import.sh` refuses a bundle whose member names contain a backslash or a control
  character, and any path that would leave `agents/memory`.
- Imported skill packs stay untrusted: the registry scan is a heuristic safety net, not a
  sandbox. Review every imported skill before use.
- A `.env` that is not valid UTF-8 is ignored with one warning.

## How releases are built, and what you can verify

- A `vX.Y.Z` tag starts the release workflows in `.github/workflows/`. Each first runs a
  shared gate (`gate.yml`): the tag must equal every version number in the repository and
  the Python and Node test suites must pass. Nothing is published or attached to a
  GitHub release unless the gate passes. A manual re-run is accepted only from a version tag.
- **npm (`gabbe-kit`)**: published from the workflow with npm trusted publishing, which
  adds a provenance attestation. In a project that has installed it, run
  `npm audit signatures` to verify the registry signatures and attestations.
- **PyPI (`gabbe`)**: published by the same release workflow. It uses a project token, or
  PyPI trusted publishing when no token is configured. Files published through trusted
  publishing carry PyPI attestations; files published with a token do not. Check the
  file's page on pypi.org to see which applies to a given version.
- **SBOM**: a CycloneDX 1.6 file, `sbom.json`, is attached to each GitHub release. It lists
  the runtime dependencies of the built wheel.
- **Not provided**: signed git tags, and a checksums file for the release assets. Do not
  assume a download can be checked against either.
- GitHub Actions used by the workflows are pinned to commit SHAs.
