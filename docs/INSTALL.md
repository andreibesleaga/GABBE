# Installing, Updating & Uninstalling GABBE

GABBE installs are **isolated**: nothing is ever written outside the chosen target
unless you pass `--global`.

> **Reversibility — scope.** Since 1.1.4 every installer records what it creates in
> `.gabbe/manifest.json`: the Node installer (`npx gabbe-kit init`, also reached through
> `curl … | sh`), the Python wizard (`gabbe setup` / `python scripts/init.py`) and
> `gabbe update`. `gabbe uninstall` removes exactly what is recorded and nothing else; without
> Python, `npx gabbe-kit uninstall` does the same (since 1.2.0).
> An install made by `npx gabbe-kit init` 1.1.3 or earlier has no record: `gabbe uninstall`
> then stops with an error and removes nothing. Re-run `npx gabbe-kit init` (1.1.4 or later)
> with the same `--agents` to create the record.

## One-command install (every channel)

| Channel | Command | Notes |
|---|---|---|
| npm / Node | `npx gabbe-kit init` | Python-independent; bundles the kit and wires the agents you name with `--agents` (none named: the root `AGENTS.md` and `.agents/skills` only). Also `npx gabbe-kit update`, `uninstall` and `doctor` (below) |
| PyPI | `pipx install gabbe` (or `pip install gabbe` / `uvx gabbe`) | adds the `gabbe` **CLI** (doctor/brain/route/gateway). The kit is Python-independent — land it with `npx gabbe-kit init` / `curl … \| sh` / a checkout. `gabbe setup` wires the kit only from a checkout. |
| Shell bootstrap | `curl -fsSL https://raw.githubusercontent.com/andreibesleaga/GABBE/main/install.sh \| sh` | picks the best available installer and passes your arguments to it (`sh install.sh init --agents claude --yes`). Without Node it needs a checkout and a terminal: the wizard knows `--force` and `--hooks` only, and the script lists the arguments it ignores |
| PowerShell bootstrap | `irm …/install.ps1 \| iex`, or `./install.ps1 -Agents claude -Yes` | the same choice; `-Agents`, `-Yes`, `-Force` and `-Help` become the installer's flags |
| Git checkout | `git clone … && python3 scripts/init.py` | the interactive wizard |

### Which install, which init

| Command | What it does | Needs |
|---|---|---|
| `npx gabbe-kit init` | **installs the kit**: copies `agents/`, wires the agents you name, records the install; no questions | Node |
| `python3 scripts/init.py` or `gabbe setup` | **the wizard**: the same install, plus questions about the project, the stack and the first prompt | Python and a checkout |
| `gabbe init` (PyPI CLI) | creates the CLI's database (`project/state.db`) only; installs no kit | `pipx install gabbe` |

`npm i -g gabbe-kit` also puts a `gabbe` command on your `PATH`; it is the kit installer, so
there `gabbe init` installs the kit. Use `gabbe-kit` as the command name to avoid the clash.

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
- **Skill layout.** Both installers emit real `<slug>/SKILL.md` folders for Claude Code,
  Copilot, VS Code, Antigravity, OpenCode, Windsurf, Cline and Devin. Before 1.2.0 the wizard
  linked `.windsurf/skills`, `.cline/skills` and `.devin/skills` to `agents/skills` instead
  (tools do not discover that tree); a new wizard run replaces that link, which the earlier
  record names, by the folders, and puts back a folder of yours that the link had replaced.
- **Your `docs/` folder** is not touched. (Up to 1.1.3 the Node installer copied the kit's
  documents into it.) The kit's documents are online:
  <https://github.com/andreibesleaga/GABBE/tree/main/docs>.
- **An `agents` that is a link** to a kit kept elsewhere: the installers use it as it is and
  copy nothing into it.
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
`gabbe`, but not the same one: on npm it is the kit installer (`init`, `update`, `uninstall`,
`doctor`), on PyPI it is the CLI. Their `init` and `doctor` are different commands.

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
end-of-install warning listing them so blank fields are never shipped silently. The wizard
lists the field names, each with where its value comes from (for example `repo_url`: your git
remote), and counts the free-text spots. The Node installer prints the count. Fill them in
`agents/AGENTS.md`, or ask your agent: it is step 2 of `BOOTSTRAP_MISSION.md`.

After installing, run `gabbe doctor` (the PyPI CLI's command; `npx gabbe-kit doctor` is a
different, smaller check, see below) to print an environment + install report
(detected OS/arch, runtimes, agent clients, and per-check PASS/WARN). It also prints
**post-install next steps** — which MCP servers to enable and how. For the full
environment-setup walkthrough (MCP servers, local-GitHub servers, policy/budgets,
validation), see `docs/POST_INSTALL.md`.

## Optional hooks

Hooks are small programs that Claude Code, Cursor or git run at a fixed point (before a shell
command, before a commit) and that ask or refuse. **They are off unless you pass `--hooks`**:
`npx gabbe-kit init --agents claude,cursor --hooks`, or `python3 scripts/init.py --hooks` (the wizard
asks no new question; `npx gabbe-kit init --wizard --hooks` forwards the flag). `update` keeps the hooks
the record names and never adds any.

| Where | What `--hooks` does |
|---|---|
| Claude Code (named in `--agents`, or chosen in the wizard) | merges the entries of `agents/hooks/claude-code/settings.fragment.json` into `.claude/settings.json`: a shell guard that asks before commit, push, tag, publish, deploy and destructive git commands; an edit guard for protected paths; a session-start note |
| Cursor | the same for `agents/hooks/cursor/hooks.fragment.json` into `.cursor/hooks.json` (shell guard only) |
| a git repository | copies `pre-commit` (refuses a staged secret) and `pre-push` (refuses a push to `main`, `master` or a configured branch, and a force push) into `.git/hooks`. Not a git repository: skipped, one line says so |

Your own settings are never replaced. Only entries that are not there yet are added, no other key
is touched, and the file is backed up first (`settings.json.gabbe-bak`, never overwriting a backup).
A settings file that is not plain JSON (comments), a link, or a `.claude` that is a link is left
alone and the installer prints what to add by hand. A git hook of yours is not replaced; when
`core.hooksPath` is set no git hook is installed. Every touched file is in `.gabbe/manifest.json`
(`hook-merge` for a merged settings file, `copy` for a git hook).

**Remove them:** `gabbe uninstall` or `npx gabbe-kit uninstall` takes out exactly the recorded entries
and nothing else. A settings file the installer created and nothing else uses is deleted; yours is
kept with your other settings (back to its original bytes when you changed nothing). The guide with
the manual steps is `agents/guides/ops/hooks.md`.

> **Old CLI.** A project installed with `--hooks` should be uninstalled with `gabbe` 1.2.0 or later.
> `gabbe` 1.1.4 does not know the `hook-merge` record: it deletes the settings file and puts the
> backup back, so the file returns to what it was before `--hooks` and changes you made to it
> afterwards are lost (the backup is not lost).

## Claude Code plugins and the context budget

The skills ship as Claude Code plugins. There is **one overall plugin, `gabbe`**: 49 curated
skills (the skills flagged `core: true`) that cover the whole system. It starts with the
skill `gabbe-start`, which carries the operating rules and the map, because a plugin install
has none of the kit's always-loaded files (`agents/AGENTS.md`, `agents/CONSTITUTION.md`).
`gabbe` is the plugin submitted to Anthropic's directory; once listed, install it from
there. It is also in the project's own marketplace:

```bash
claude plugin marketplace add andreibesleaga/GABBE
claude plugin install gabbe@gabbe
```

Ten optional **topic plugins** (`gabbe-ai`, `gabbe-architecture`, `gabbe-brain`,
`gabbe-coding`, `gabbe-coordination`, `gabbe-data`, `gabbe-industry`, `gabbe-ops`,
`gabbe-product`, `gabbe-security`) hold the other skills, plus `gabbe-extras` for the
kit-maintenance skills of `agents/skills/core/`. They are in the project's marketplace only
and are not submitted. A skill is in exactly one plugin.

**Why a curated set.** Claude Code lists every installed skill's name and description in
context so that Claude knows what exists. The budget is 1% of the model's context window.
When the listing is over it, Claude Code drops descriptions, starting with the skills you use
least; names always stay. Each entry's text is capped at 1,536 characters
(<https://code.claude.com/docs/en/skills.md>, "Skill descriptions are cut short", read
21 Nov 2026). To change it, set `skillListingBudgetFraction` (for example `0.02`) or the
`SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable, or set rarely used skills to
`"name-only"` in `skillOverrides`. `/doctor` estimates the cost and `/skill-doctor` shows
each skill's cost and use.

**Measured for `gabbe` (our computation, 21 Nov 2026).** 49 skills; names plus descriptions
as the plugin lists them come to about 13,000 characters, about 3,300 tokens at four
characters per token. The same sum over all skills is several times larger. 1% of a 200k
context is about 2,000 tokens, so on a 200k context Claude Code may drop some descriptions
of the least-used skills (nothing fails); on a 1M context (about 10,000 tokens) the whole
listing fits. `claude plugin details gabbe` reports Claude Code's own figure for an
installed plugin; the figures here were computed from the generated skill files, not read
from it. `plugins/gabbe` has under 100 files and under 1 MB, within the directory's limits
(at most 512 files, each text file under 256 KiB).

**What the plugin leaves out.** Loki mode and Brain mode (they orchestrate personas and guides
that the plugin does not carry), the personas, guides, installers and most other skills. For
the full kit run `npx gabbe-kit init` in the project: it downloads and runs the `gabbe-kit`
package from npm and writes files into the current folder, so you decide whether to run it.

## Install scopes (targets)

- **Project (default):** the current directory. Nothing is written elsewhere.
- **Global:** `--global` (of `gabbe update` and `gabbe uninstall`) → `$XDG_DATA_HOME/gabbe`
  (falls back to `~/.local/share/gabbe`).
- **Custom:** `--dir <path>` → an explicit directory.

Resolution order for `update` / `uninstall`: `--dir` > `--global` > project (cwd).

**The wizard's "Global" choice is a different place.** It installs the kit to `~/agents`
(your home folder), writes no `.gabbe/manifest.json` for it, and so `gabbe update --global` and
`gabbe uninstall --global` do not see it: they work on `$XDG_DATA_HOME/gabbe`. To remove a
wizard "Global" install, delete `~/agents` yourself. The wizard says so when you pick it.

## Updating

```bash
gabbe update                 # refresh kit files; keep your changes and the install record
```

`update` runs from a checkout of this repository (the PyPI package does not contain the
kit). Without Python, `npx gabbe-kit update` refreshes the kit from the npm package. It is
`init` with the agents the install record already names (it adds and removes no agent), under
the same safe-copy rules, and it stops with exit status 1 when there is no usable record.
For each kit file under `agents/`:

- unchanged since install: replaced by the new version;
- changed by you: copied to `<name>.gabbe-bak` (never over an existing backup), then replaced;
- `AGENTS.md`, `CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json` and anything
  under `memory/` or `project/`: kept as they are once you have changed them;
- no longer shipped by the kit: removed only if you never changed it.

When `update` keeps a kit file you changed, it writes the kit's new version next to it as `<name>.gabbe-new` and says so; it never overwrites a `.gabbe-new` it does not own, and `uninstall` removes it while unchanged. A recorded path that is absolute, contains `..` or leaves the project is skipped with a message.

The earlier install record is merged, not replaced: wiring links and generated skill folders
stay as they are, on disk and in the record. `gabbe update` does not regenerate the skill folders
of your agents (`.claude/skills`, `.cursor/rules`, …); re-run the installer you used to
refresh them (`npx gabbe-kit update` does regenerate them). On an install without a record, `update` does not take ownership of files
that are already there and equal the kit's: it leaves them unrecorded, so a later
`uninstall` leaves them too. Re-run the installer first to create the record. `update`
refuses to write when `agents/` is a link to a folder outside the project.

Upgrading from 1.1.x to 1.2.0 needs a manual step for `agents/AGENTS.md` and `agents/CONSTITUTION.md`: see [UPGRADING.md](UPGRADING.md).

## Uninstalling (manifest-backed installs)

```bash
npx gabbe-kit uninstall --dry-run  # the same, without Python (Node installs and wizard installs)
gabbe uninstall --dry-run          # print exactly what would be removed
gabbe uninstall                    # remove it; restore linked backups
gabbe uninstall --agents cursor    # deselect one agent's wiring only
gabbe uninstall --purge            # same as a plain uninstall since 1.1.4 (kept for compatibility)
```

`npx gabbe-kit uninstall` takes `--dry-run`, `--agents a,b` and `--purge`, follows the same
rules as `gabbe uninstall`, prints the same "Removed N path(s)" line and uses the same exit
statuses. Since 1.2.0 `init`, `update`, `uninstall` and `doctor` take `--dir <path>` to act on another
folder than the current one. `npx gabbe-kit doctor` is a
read-only check: is there a kit, is the install record readable, how many recorded paths are
missing or changed, which agents are wired, how many `[PLACEHOLDER` fields are left, which
links dangle. It exits 0 when the install is consistent and 1 when not.

**Installing into a repository you do not trust.** `npx` reads the `.npmrc` of the folder it runs in, so
a cloned project can choose the registry `npx` downloads from, or add `node-options` that run its own code.
The bootstrap scripts (`install.sh`, `uninstall.sh` and the PowerShell pair) therefore run `npx` from an
empty temporary folder and pass the project with `--dir`. When you type the command yourself, do the same:
`cd` to another folder and run `npx gabbe-kit@<version> init --dir /path/to/project`.

`--agents` takes the same short names in both commands (`claude` for `claude-code`, and so on); a name that matches no recorded agent prints one note naming the recorded agents. When `init`, `update` or the wizard re-emits skills, a generated skill or rule file that an earlier install recorded and the kit no longer emits (a renamed skill) is removed if it is unchanged and sits in a folder that run emitted into; one you changed is kept and reported.

Or use the bootstrap scripts when the CLI is not on `PATH`. They use Node when it is there,
else the Python CLI (`pip install gabbe`), else print the manual steps; they pass your
arguments on, and their exit status is the tool's. Each bootstrap script runs the `gabbe-kit` release it was published with, not the newest one; set `GABBE_KIT_VERSION=<version>` to run another release, or `GABBE_KIT_VERSION=latest` for the newest on npm. The uninstall scripts call the `gabbe` command, or Python started without the current folder on its path, so a `gabbe/` folder in a project is never run:

```bash
sh uninstall.sh --dry-run                    # POSIX
pwsh ./uninstall.ps1 -DryRun                 # Windows / PowerShell
pwsh ./uninstall.ps1 -Dir C:\work\proj -Agents cursor -Purge
```

`uninstall.ps1` takes `-DryRun`, `-Agents`, `-Purge`, `-Dir` and `-Help`.

Uninstall reads `.gabbe/manifest.json` and removes **exactly** what is recorded there. It
restores a file of yours that the install replaced from its backup, takes the pointer block
out of your instruction files, keeps any installed file you edited where it is (it prints
`kept <path>: it changed since the install`; since 1.2.0 no `.gabbe-bak` copy is made), prunes
now-empty directories, and is idempotent (safe to run twice).

The record is treated as untrusted (a cloned repository can carry one). Uninstall, `update` and
`doctor` act on an entry only when it is a kind the installers write; they remove a file only when
its bytes match the recorded hash; they move a backup back only when it is named
`<path>.gabbe-bak` or `<path>.bak` (with an optional `.<n>`) and is a real file; they take out only
the kit's own hook entries, and only in `.claude/settings.json` and `.cursor/hooks.json`; under
`.git/` they touch only the two marked GABBE hooks; and they check every path again right before
use. An entry the record cannot prove (no hash, an unknown kind, a link that points outside
`agents/`) is kept with one line that says why.

It never deletes a file the install did not record. These always stay: your own files
(including your own skills inside `.claude/skills` and similar folders), files under
`agents/memory/` that you changed, and backups. A preserved kit file (`agents/AGENTS.md`,
`agents/CONSTITUTION.md`, …) is removed only if you never changed it; one you changed stays
where it is. A path that is no longer what was recorded (you replaced a file by a folder or
a link, or a link by a file) is left alone. Empty folders left under `agents/` are removed.
The command prints how many files are left under `agents/`. In a project where you changed
none of the installed files, every file is as it was before the install; empty folders are
not restored. `--dry-run` prints every path it would remove.

The pointer block is added and removed byte for byte: the encoding and line endings of
your file are not changed. A read-only instruction file is left alone, with a message.

Without a record (`.gabbe/manifest.json` missing), or with a record that cannot be read,
`gabbe uninstall` exits with status 1 and removes nothing, and `gabbe update` changes
nothing; see the scope note at the top. If an installer stops part-way, it still records
what it had written. A directory that 1.1.3 or earlier recorded
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
