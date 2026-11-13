# Installing, Updating & Uninstalling GABBE

GABBE installs are **isolated**: nothing is ever written outside the chosen target
unless you pass `--global`.

> **Reversibility — scope.** Manifest-backed, precise `update`/`uninstall` (recorded
> in `.gabbe/manifest.json`) covers kits managed by the Python `gabbe` CLI **and**
> the Python wizard (`gabbe setup` / `python scripts/init.py`), which now writes a
> manifest recording everything it created under the project (copied kit files,
> wiring symlinks, generated skill trees, config files). So `gabbe uninstall` fully
> reverses a wizard install too. The remaining Python-independent installers
> (`npx gabbe-kit init`, `curl … | sh`) copy the kit but do **not** write a manifest,
> so `gabbe uninstall` cannot auto-reverse them — remove those manually (delete the
> created `agents/`, `.agents/`, per-agent dirs, and root `AGENTS.md`), or run
> `gabbe update` from a checkout to begin manifest tracking.

## One-command install (every channel)

| Channel | Command | Notes |
|---|---|---|
| npm / Node | `npx gabbe-kit init` | Python-independent; bundles the kit and wires detected agents |
| PyPI | `pipx install gabbe` (or `pip install gabbe` / `uvx gabbe`) | adds the `gabbe` **CLI** (doctor/brain/route/gateway). The kit is Python-independent — land it with `npx gabbe-kit init` / `curl … \| sh` / a checkout. `gabbe setup` wires the kit only from a checkout. |
| Shell bootstrap | `curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh \| sh` | picks the best available installer |
| Git checkout | `git clone … && python3 scripts/init.py` | the interactive wizard |

**Never-clobber + `--force`.** Both installers — the Node installer
(`npx gabbe-kit init`) and the Python wizard (`gabbe setup` / `python scripts/init.py`)
— back up ANY differing pre-existing file to `<name>.gabbe-bak` before refreshing it, so
nothing you already had is silently overwritten. The preserve-set (`AGENTS.md`,
`CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json`) is left as-is unless you
pass `--force` (e.g. `npx gabbe-kit init --force`), which opts into re-templating those
too — and still backs each one up first.

**Package names.** On npm the package is **`gabbe-kit`** (npm refuses the unscoped `gabbe`);
on PyPI it is **`gabbe`**; the npm package is also mirrored on GitHub Packages as
`@andreibesleaga/gabbe-kit` (npmjs stays canonical). Both packages install a command named
`gabbe`, but not the same one: on npm it is the kit installer (`gabbe init` only), on PyPI it
is the CLI.

### New or existing project

In an empty directory the wizard runs the greenfield flow unchanged. In an **existing
codebase** (detected via `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`,
`composer.json`, `pom.xml`, `Gemfile`, a `.git` repo, etc.) it adds a **Mode** question —
greenfield build vs **Upgrade / Refactor existing** — prefills the detected language /
framework / package-manager / project-name as defaults, and in refactor mode scaffolds a
`BROWNFIELD_ONBOARDING.md` discovery brief (map → assess → baseline → backlog) instead of
greenfield mission docs.

**Placeholders.** The wizard auto-fills derivable `[PLACEHOLDER:]` fields in `AGENTS.md` —
dev/test/lint/format/typecheck/coverage commands (by package manager), `repo_url` (from the
git remote), and `ci_cd` / `deployment_target` (from detected files). Fields it can't derive
are kept and tagged `<!-- OPTIONAL: fill this in yourself -->`, and the installer prints an
end-of-install warning listing them so blank fields are never shipped silently. Fill them in
or re-run `gabbe setup`.

After installing, run `gabbe doctor` (a command of the PyPI CLI; the npm package's
`gabbe` command is the kit installer and has no `doctor`) to print an environment + install report
(detected OS/arch, runtimes, agent clients, and per-check PASS/WARN). It also prints
**post-install next steps** — which MCP servers to enable and how. For the full
environment-setup walkthrough (MCP servers, local-GitHub servers, policy/budgets,
validation), see `docs/POST_INSTALL.md`.

## Claude Code plugins and the context budget

The skills also ship as Claude Code plugins (`claude plugin marketplace add andreibesleaga/GABBE`,
then `claude plugin install gabbe@gabbe` for the core skills and `gabbe-<topic>@gabbe` for the
topic plugins). Claude Code keeps every installed skill's name and description in context,
within about 1% of the context window. All 214 skills would need far more than that; the core
plugin alone costs about 2,700 tokens per session (`claude plugin details gabbe`), a little over
the ~2,000-token budget of a 200k context and well within that of a 1M context. Over budget,
Claude Code drops the descriptions of the least-used skills; nothing fails. Install only the
topics you use.

## Install scopes (targets)

- **Project (default):** the current directory. Nothing is written elsewhere.
- **Global:** `--global` → `$XDG_DATA_HOME/gabbe` (falls back to `~/.local/share/gabbe`).
- **Custom:** `--dir <path>` → an explicit directory.

Resolution order for `update` / `uninstall`: `--dir` > `--global` > project (cwd).

The wizard's own "Global" choice installs to `~/agents` and is not manifest-tracked; `--global` of `update`/`uninstall` targets `$XDG_DATA_HOME/gabbe` only.

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
restores any shadowed user files from their `.gabbe-bak`/`.bak` backup, preserves any
file you edited after install as `<name>.gabbe-bak` instead of deleting it, prunes
now-empty wiring directories, and is idempotent (safe to run twice). When a manifest is
present the result is byte-identical to the pre-install state. The wizard
(`gabbe setup` / `python scripts/init.py`) now writes a manifest, so its installs are
fully reversible too. **Note:** only `npx` / `curl` installs remain non-manifest-tracked
(see the scope note at the top); for those, delete the kit directories manually or run
`gabbe update` from a checkout first.

## Verification

The reversibility and isolation guarantees are regression-tested
(`scripts/tests/test_install_manifest.py`, `test_uninstall.py`,
`test_install_isolation.py`, `test_remove_agents.py`) and exercised across
`{ubuntu, macos, windows}` by the CI `install-matrix` job plus the post-publish
`release-verify` job (which installs the published package and runs `gabbe doctor`).
