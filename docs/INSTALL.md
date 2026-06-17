# Installing, Updating & Uninstalling GABBE

GABBE installs are **isolated**: nothing is ever written outside the chosen target
unless you pass `--global`.

> **Reversibility — scope.** Manifest-backed, precise `update`/`uninstall` (recorded
> in `.gabbe/manifest.json`) covers kits managed by the Python `gabbe` CLI — i.e.
> after a `gabbe update` from a checkout / editable install, which writes the
> manifest. The Python-independent installers (`npx gabbe-kit init`, `curl … | sh`,
> and the `scripts/init.py` wizard) copy the kit but do **not** write a manifest, so
> `gabbe uninstall` cannot auto-reverse them — remove those manually (delete the
> created `agents/`, `.agents/`, per-agent dirs, and root `AGENTS.md`), or run
> `gabbe update` from a checkout to begin manifest tracking.

## One-command install (every channel)

| Channel | Command | Notes |
|---|---|---|
| npm / Node | `npx gabbe-kit init` | Python-independent; bundles the kit and wires detected agents |
| PyPI | `pipx install gabbe` (or `pip install gabbe` / `uvx gabbe`) | adds the `gabbe` **CLI** (doctor/brain/route/gateway). The kit is Python-independent — land it with `npx gabbe-kit init` / `curl … \| sh` / a checkout. `gabbe setup` wires the kit only from a checkout. |
| Shell bootstrap | `curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh \| sh` | picks the best available installer |
| Git checkout | `git clone … && python3 scripts/init.py` | the interactive wizard |

After installing, run `gabbe doctor` to print an environment + install report
(detected OS/arch, runtimes, agent clients, and per-check PASS/WARN). It also prints
**post-install next steps** — which MCP servers to enable and how. For the full
environment-setup walkthrough (MCP servers, local-GitHub servers, policy/budgets,
validation), see `docs/POST_INSTALL.md`.

## Install scopes (targets)

- **Project (default):** the current directory. Nothing is written elsewhere.
- **Global:** `--global` → `$XDG_DATA_HOME/gabbe` (falls back to `~/.local/share/gabbe`).
- **Custom:** `--dir <path>` → an explicit directory.

Resolution order for `update` / `uninstall`: `--dir` > `--global` > project (cwd).

## Updating

```bash
gabbe update                 # additive refresh of kit files; prunes orphans
```

`update` preserves user/preserve files (`CONSTITUTION.md`, `policies.yml`) and
your memory/project files; it only refreshes managed kit artifacts and removes
ones that are no longer emitted.

## Uninstalling (manifest-backed installs)

```bash
gabbe uninstall --dry-run          # print exactly what would be removed
gabbe uninstall                    # remove it; restore any .bak backups
gabbe uninstall --agents cursor    # deselect one agent's wiring only
gabbe uninstall --purge            # also remove the agents/ kit and .gabbe/
```

Or use the bootstrap scripts when the CLI is not on `PATH`:

```bash
sh uninstall.sh --dry-run          # POSIX
pwsh ./uninstall.ps1 -DryRun       # Windows / PowerShell
```

Uninstall reads `.gabbe/manifest.json`, removes **exactly** what was installed,
restores any shadowed user files from their `.bak`, prunes now-empty directories,
and is idempotent (safe to run twice). When a manifest is present the result is
byte-identical to the pre-install state. **Note:** `npx` / `curl` / wizard installs
are not manifest-tracked (see the scope note at the top); for those, delete the kit
directories manually or run `gabbe update` from a checkout first.

## Verification

The reversibility and isolation guarantees are regression-tested
(`scripts/tests/test_install_manifest.py`, `test_uninstall.py`,
`test_install_isolation.py`, `test_remove_agents.py`) and exercised across
`{ubuntu, macos, windows}` by the CI `install-matrix` job plus the post-publish
`release-verify` job (which installs the published package and runs `gabbe doctor`).
