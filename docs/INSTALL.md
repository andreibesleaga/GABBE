# Installing, Updating & Uninstalling GABBE

GABBE installs are **isolated**: nothing is ever written outside the chosen target
unless you pass `--global`.

> **Reversibility — scope.** Since 1.1.4 every installer records what it creates in
> `.gabbe/manifest.json`: the Node installer (`npx gabbe-kit init`, also reached through
> `curl … | sh`), the Python wizard (`gabbe setup` / `python scripts/init.py`) and
> `gabbe update`. `gabbe uninstall` removes exactly what is recorded and nothing else.
> An install made by `npx gabbe-kit init` 1.1.3 or earlier has no record: `gabbe uninstall`
> then stops with an error and removes nothing. Re-run `npx gabbe-kit init` (1.1.4 or later)
> with the same `--agents` to create the record.

## One-command install (every channel)

| Channel | Command | Notes |
|---|---|---|
| npm / Node | `npx gabbe-kit init` | Python-independent; bundles the kit and wires the agents you name with `--agents` (none named: the root `AGENTS.md` and `.agents/skills` only) |
| PyPI | `pipx install gabbe` (or `pip install gabbe` / `uvx gabbe`) | adds the `gabbe` **CLI** (doctor/brain/route/gateway). The kit is Python-independent — land it with `npx gabbe-kit init` / `curl … \| sh` / a checkout. `gabbe setup` wires the kit only from a checkout. |
| Shell bootstrap | `curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh \| sh` | picks the best available installer |
| Git checkout | `git clone … && python3 scripts/init.py` | the interactive wizard |

**Never-clobber + `--force`.** Both installers — the Node installer
(`npx gabbe-kit init`) and the Python wizard (`gabbe setup` / `python scripts/init.py`)
— back up ANY differing pre-existing file to `<name>.gabbe-bak` before refreshing it, so
nothing you already had is silently overwritten. A backup is never overwritten: if
`<name>.gabbe-bak` exists and holds something else, the next one is `<name>.gabbe-bak.1`,
and so on. The preserve-set (`AGENTS.md`, `CONSTITUTION.md`, `TASKS.md`, `policies.yml`,
`config.json`) is left as-is unless you pass `--force` (e.g. `npx gabbe-kit init --force`),
which opts into re-templating those too — and still backs each one up first.

**Files you already have (since 1.1.4).**

- **Instruction files** (root `AGENTS.md`, `.github/copilot-instructions.md`,
  `.claude/CLAUDE.md`, `.cursorrules`, `GEMINI.md` and the other per-agent rule files): your
  file is kept. The installer appends a short marked block that points to `agents/AGENTS.md`
  and saves the original as `<name>.gabbe-bak`. `gabbe uninstall` takes the block out again.
  With `--force` the file is replaced by a link to the kit's file after it is moved to
  `<name>.bak` (or `<name>.bak.1` if that name is taken).
- **Your own skills and rules** in `.claude/skills`, `.github/skills`, `.cursor/rules` and
  the like stay. If one has the same name as a kit skill, yours is saved next to the kit's
  file as `<name>.gabbe-bak`.
- **Your `docs/` folder** is not touched. (Up to 1.1.3 the Node installer copied the kit's
  documents into it.) The kit's documents are online:
  <https://github.com/andreibesleaga/GABBE/tree/main/docs>.
- **An `agents/` folder of your own:** your files in it are kept, and so is your
  `agents/AGENTS.md`. The Node installer then says that the kit's own `agents/AGENTS.md` was
  not installed; `--force` installs it and backs yours up first.
- **`.gemini/settings.json`, `.aider.conf.yml`, `opencode.json`:** kept if they exist.
- **Symbolic links of yours** (for example `AGENTS.md -> CLAUDE.md`, or `.claude/skills`
  linked to another folder): kept, and nothing is written through them. The installer says
  which paths it left alone. `--force` moves a link at an instruction-file path to
  `<name>.bak` and wires the kit's link instead.
- **If a backup cannot be made** (permissions, full disk) the installer stops before it
  overwrites anything.

**First prompt.** The wizard writes `BOOTSTRAP_MISSION.md` (or `SETUP_MISSION.md`) from your
answers. The Node installer asks no questions and writes a general `BOOTSTRAP_MISSION.md`;
it is not replaced if you already have one. Tell your agent: "Read BOOTSTRAP_MISSION.md and
follow it."

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
gabbe update                 # refresh kit files; keep your changes and the install record
```

`update` runs from a checkout of this repository (the PyPI package does not contain the
kit). For each kit file under `agents/`:

- unchanged since install: replaced by the new version;
- changed by you: copied to `<name>.gabbe-bak` (never over an existing backup), then replaced;
- `AGENTS.md`, `CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json` and anything
  under `memory/` or `project/`: kept as they are once you have changed them;
- no longer shipped by the kit: removed only if you never changed it.

The earlier install record is merged, not replaced: wiring links and generated skill folders
stay as they are, on disk and in the record. `update` does not regenerate the skill folders
of your agents (`.claude/skills`, `.cursor/rules`, …); re-run the installer you used to
refresh them. On an install without a record, `update` does not take ownership of files
that are already there and equal the kit's: it leaves them unrecorded, so a later
`uninstall` leaves them too. Re-run the installer first to create the record. `update`
refuses to write when `agents/` is a link to a folder outside the project.

## Uninstalling (manifest-backed installs)

```bash
gabbe uninstall --dry-run          # print exactly what would be removed
gabbe uninstall                    # remove it; restore linked backups
gabbe uninstall --agents cursor    # deselect one agent's wiring only
gabbe uninstall --purge            # also remove empty folders left under agents/
```

Or use the bootstrap scripts when the CLI is not on `PATH`:

```bash
sh uninstall.sh --dry-run          # POSIX
pwsh ./uninstall.ps1 -DryRun       # Windows / PowerShell
```

Uninstall reads `.gabbe/manifest.json` and removes **exactly** what is recorded there. It
restores a file of yours that the install replaced from its backup, takes the pointer block
out of your instruction files, keeps any installed file you edited as `<name>.gabbe-bak`
instead of deleting it, prunes now-empty directories, and is idempotent (safe to run twice).

It never deletes a file the install did not record. These always stay: your own files
(including your own skills inside `.claude/skills` and similar folders), files under
`agents/memory/` that you changed, and backups. A preserved kit file (`agents/AGENTS.md`,
`agents/CONSTITUTION.md`, …) is removed only if you never changed it; one you changed stays
where it is. `--purge` also removes the empty folders left under `agents/`. The command
prints how many files are left under `agents/`. In a project where you changed none of the
installed files, the result is byte-identical to the state before the install.

Without a record (`.gabbe/manifest.json` missing) `gabbe uninstall` exits with status 1 and
removes nothing; see the scope note at the top. A directory that 1.1.3 or earlier recorded
as a whole (for example `.claude/skills`) is no longer removed as a whole: only the files
the installer generated in it are removed.

To remove an unrecorded install by hand: delete `agents/` (after copying out anything of
yours), `.agents/skills/`, the per-agent folders and files the installer created
(`.claude/skills/<kit skill>/`, `.cursor/rules/<kit skill>.mdc`, `.github/skills/<kit skill>/`,
links such as `.claude/CLAUDE.md`, `.cursorrules`, `GEMINI.md`), the kit documents that
1.1.3 copied into `docs/`, and the root `AGENTS.md` link; then restore your originals from
`AGENTS.md.bak`, `copilot-instructions.md.bak` and any `<name>.gabbe-bak`.

## Verification

The reversibility and isolation guarantees are regression-tested
(`scripts/tests/test_install_manifest.py`, `test_uninstall.py`,
`test_install_isolation.py`, `test_remove_agents.py`, `test_install_roundtrip.py`,
`test_node_install.js`) and exercised across
`{ubuntu, macos, windows}` by the CI `install-matrix` job plus the post-publish
`release-verify` job (which installs the published package and runs `gabbe doctor`).
