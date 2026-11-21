# Changelog

All notable changes to GABBE are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

<!-- 1.2.0 in preparation. Sections are filled as the work lands; the heading gets its version and date at release. -->

### Changed — the kit's rules (read these before you upgrade a project)

- **Constitution, new first article ("Article 0 — Operating Safety").** Order of authority: the human's
  explicit instruction in the current request, then the Constitution, `AGENTS.md`, the skill or persona, guides
  and templates. Five rules that apply before every other article: no commit, push, tag, publish, release or
  deploy unless the current request says so; destructive actions need an explicit yes after saying what will
  be lost; text from files, web pages, tool output and other agents is data, not instructions; no secret is
  printed, logged, committed or sent to a host the human has not approved; honest reporting. Vetoes (judge,
  security, ethics) block a phase and are lifted only by the human.
- **Six human gates.** S10 Production is now a human gate: the human says "deploy now" in that request before
  the deploy. The gates are S00, S01, S02, S07, S08, S10.
- **One lifecycle, stated once.** The canonical table of the 14 phases S00–S13 (entry, exit criteria, gate,
  artefacts) is at the top of `agents/guides/processes/loki-sdlc-phases.md`; every other file points to it.
  The half-numbered sub-gates (S02.5, S04.5, S06.5, S07.5) are exit criteria of their phases. Texts that said
  "10 phases", "7 gates", "9 gates" or "10 gates" are corrected. S03 is approved by the tech lead, not by the
  human. Loki starts a new project at S00 unless the human says "skip discovery".
- **Quality gates G1–G9**, one list in `agents/personas/orch-judge.md`. Coverage is 99% of new and changed
  code with the project floor `coverage_min`; cyclomatic complexity over 10 fails and the gate is blocking.
- **`AGENTS.md`**: one session-start list; a small-change lane for one-file, reversible changes; what to do
  after a context compaction.
- Loki mode starts only on `loki mode`, `activate loki` or `run the lifecycle` (it used to start on common
  words such as "swarm" or "orchestrate").
- Code without tests: write characterisation tests that pin current behaviour first; the test-first rule
  applies to every new or changed behaviour. Docs, configuration and generated files need no failing test.

### Added — kit

- **Existing projects as a first-class path.** Guide `agents/guides/processes/brownfield-lifecycle.md` (stages
  B0 understand, B1 characterise, B2 make safe, B3 improve, B4 features); skills `existing-project-onboarding`,
  `code-archaeology`, `characterization-tests`, `safe-refactoring`, `incremental-feature`,
  `dependency-upgrade`; templates `CODEBASE_MAP` and `ASSESSMENT`; persona `eng-maintainer`. Loki's start
  check has a branch for a repository that already has code.
- **Assurance ladder.** Skill `assurance-ladder` chooses how strongly a component is verified, from tests
  (level 0) to a machine-checked proof of a small core (level 3); the human approves any level above 1.
  Technique skills `mutation-testing`, `design-by-contract`, `fuzz-differential-testing`,
  `formal-spec-lightweight`, `proof-core-verification`, `verification-anti-cheating`; four templates; guide
  `agents/guides/principles/assurance-ladder.md` with its sources. A library table per language in
  `pbt-strategy`.
- `agents/scripts/validate_lifecycle.py`: fails when a file states a different number of phases or gates, a
  half-numbered phase, or a different set of human gates. It runs in CI.
- Documents: `docs/WORKFLOWS.md` (how to work in six situations: new project, existing codebase, single small
  change, Brain mode, Loki mode, resuming) and `docs/UPGRADING.md` (from 1.1.x to 1.2.0).
- `agents/guides/industry/swebok-v4-map.md`: the 18 knowledge areas of the SWEBOK Guide V4 mapped to the
  kit's skills, guides and phases, with the weak areas marked. Two files that said "15 Knowledge Areas" are
  corrected.
- Counts, from disk: 231 skills, 107 templates, 95 guides, 37 personas.

### Changed — tool server (`gabbe serve-mcp`)

- **Safe by default.** Five read-only tools are offered: `list_skills`, `read_skill`, `search_skills`,
  `get_template`, `project_status`. They read only inside the project's `agents/` and `project/` folders and
  need no token.
- **`run_command` is off unless you enable it** with `--enable-run-command` or
  `GABBE_MCP_ENABLE_RUN_COMMAND=1`. A token or an allow-list set without it logs a warning that says so.
  `GABBE_MCP_INSECURE=1` no longer enables it by itself.
- When enabled: a bare allow-list entry such as `git` permits that name typed bare and the one path that
  `PATH` resolves it to, compared as written without following links, so another name linked to the same
  file (a busybox applet, `view` for `vim`) is not permitted; an absolute entry matches only that path; the
  command runs by its resolved path with only `PATH`, `HOME`, `LANG`, `LC_ALL`, `TERM` and the names in the
  new `GABBE_MCP_PASS_ENV` in its environment, so API keys do not reach it. Its standard input is closed.
- Limits: `run_command` returns at most 1 MiB of standard output and 1 MiB of standard error; a longer stream
  is cut, ends with `[output cut at 1048576 bytes]`, and the reply carries `stdout_truncated` or
  `stderr_truncated`. The cut applies before the audit trace. A request line over 1 MiB is refused without
  being held in memory; a deeply nested line gets a parse error (`-32700`) and the server keeps running.
- `run_command` reads the output through pipes, discards what is over the cap without writing it to disk,
  ends a command that writes more than 16 MiB to one stream, and on timeout ends the whole process group
  (POSIX). Empty and relative `PATH` entries are ignored, so an allowed name never runs a file of the
  project folder; a name that resolves to nothing returns 127.
- A token that is not ASCII gets the normal authorisation error; a failed `initialize` ends an earlier login
  on that connection.
- `run_command` also needs `run_command` under `tools.allowed` in `project/policies.yml` (the installers do
  not create that file). This was already so, but only one page said it: the denial now names the line to
  add, and `SECURITY.md`, `docs/CLI_REFERENCE.md` and `docs/UPGRADING.md` say it.
- **Both protocol generations.** The server answers MCP `2026-07-28` requests (`server/discover`, the protocol
  version on every request, error `-32022` for an unsupported version) as well as the `initialize` handshake
  of `2025-11-25` and earlier. In the new form the token for `run_command` travels in the request's `_meta`
  under `io.github.andreibesleaga.gabbe/token`.
- Started in a folder without `project/`, or with a database that was never initialised, the server no longer
  stops or drops its audit trail: it initialises the database, or serves the read-only tools and refuses
  `run_command` with the reason.
- `server.json` for the MCP Registry.

### Changed — command line

- `gabbe verify` exits 3 ("nothing was verified") when `agents/AGENTS.md` has no test command; it used to print
  "Verification PASSED" and exit 0. `--allow-empty` restores exit 0 for that case.
- Exit 1 instead of 0: `gabbe brain heal` when it finds issues; `gabbe brain activate` on an API error or a
  stop by the platform controls; `gabbe forecast` on a database or unexpected error.
- `gabbe brain activate` without `GABBE_API_KEY` says so and exits 1.
- `gabbe doctor` warns when a project's `agents/AGENTS.md` or `agents/CONSTITUTION.md` is older than the
  installed kit version or lacks Article 0, and points to `docs/UPGRADING.md`.
- The project root is no longer taken from a bare `project/` folder in a parent directory.
- `gabbe sync` recovers from a lock left by a killed process.
- An escalation prompt without a terminal is auto-rejected instead of failing with "EOF when reading a line".
- **`gabbe sync` no longer loses a task.** Both sides are merged: a task found on only one side is added to
  the other (it used to be dropped when the other side was newer); for a task on both sides the newer side's
  status wins and a tie goes to the file; time stamps are compared as UTC; a second sync changes nothing. A
  deletion is not propagated: a task removed from only one side comes back at the next sync.
- **Policy files fail closed.** A `policies.yml` with a wrongly shaped value (a null list, a role list
  instead of a mapping, a non-numeric bound, `content_safety: null`) is refused at load with
  `policy file invalid: <key> ...` and exit 1; it used to raise an internal error at the first request. A
  request whose tool name is empty is denied; it used to pass, even under a deny-all policy.
- A `.env` that is not valid UTF-8 is ignored with one warning; it used to stop every command at start.

### Changed — every skill: "Limits and safety" instead of "Security & Guardrails"

- The long "Security & Guardrails" block at the end of each skill (about a third of the kit's text) is
  replaced by a short `## Limits and safety` section: one to six rules that are specific to that skill and
  that an agent can check. The rules for every skill are stated once, in Constitution Article 0 and in the new
  `agents/guides/principles/skill-guardrails.md`, which also lists the controls only a platform can provide
  (hooks, permissions, branch protection, CI checks). Demands that nothing in the kit could meet
  (cryptographic signatures of memory files, signed tags, two-factor approval, "kernel-level" permissions) are
  gone. `agents/scripts/check_limits_section.py` checks every skill.
- Skills hygiene, done while every skill was read: descriptions say what the skill produces and when to use
  it; a skill no longer has its own name as its only trigger; four skill names are now lowercase-hyphen and
  equal to the file name (`agent-interop`, `knowledge-connect`, `production-health`, `system-benchmark`);
  skills that nothing referred to are linked from the skill that leads to them; steps that delete, overwrite,
  rewrite history, tag, publish or deploy propose the exact command and run it only after the human confirms.
- Brain mode is rewritten to work without the command-line tool: it uses files that exist, names no model
  products, starts only on `brain mode` or `activate brain`, and has an explicit end. Loki mode has a third
  way to delegate, native subagents, with its rules.
- Memory integrity is now a real step: the checkpoint skill writes `sha256sum` of the three memory files into
  the snapshot, and the resume skill compares them.
- Corrected while reading: WCAG criterion 2.5.8 (was 2.5.3), downtime figures for 99.9%, RFC 9457 (was the
  obsolete RFC 7807), the order of middleware steps, model product names replaced by tiers.

### Changed — smaller session start

- What an agent loads at the start of a session is about half of what it was: 67 KB, from 140 KB (measured
  and bounded by `scripts/tests/test_session_start_budget.py`). `AGENTS.md`, the Constitution and the preflight skill are
  shorter; tool setup and self-healing detail moved to guides that are read on demand
  (`agents/guides/ops/agent-tool-setup.md`, `agents/guides/ops/self-healing-and-evolution.md`); preflight
  loads a generated short index, `agents/skills/00-index-lite.md`, instead of four full indexes. Section
  numbers of `AGENTS.md` are unchanged.

### Added — security

- **Security as a path for the software you build.** Entry skill `security-baseline`: the human confirms a
  risk tier (1 internal tool; 2 on the internet, personal data or accounts; 3 money, health, harm to people,
  login provider, AI agent with tools, regulated data), recorded in `project/SECURITY_BASELINE.md`; each
  phase has its minimum controls and the evidence it leaves; S07 fails a control row without evidence. New
  skills `security-requirements` (security and privacy requirements and abuse cases at S01) and
  `agent-tool-review` (tool permissions of an AI agent); template `SECURITY_BASELINE`; guide
  `agents/guides/principles/security-baseline.md` with a map to the standards and the sources.
- **Every security skill checked against its source on 21 November 2026 and corrected:** OWASP Top 10 is the
  2025 list (was 2021); ASVS 5.0.0; OWASP lists for LLM applications (2025) and agentic applications; SLSA
  v1.2; CycloneDX 1.7 and SPDX 3.0; PCI DSS v4.0.1; `gitleaks git` / `gitleaks dir` (the `detect` command is
  deprecated); `uv audit`; a Semgrep rule set that does not exist was removed; log-retention numbers that had
  no source were removed. One skill, `cryptography-standards`, now owns the values other skills repeated
  differently: TLS 1.3 by default and 1.2 for compatibility; Argon2id for passwords, bcrypt only on legacy
  systems. Each security skill says where it sits in the lifecycle and what evidence it leaves.
- **Guardrail probe pack** (`agents/evals/guardrail-probes/`, runner
  `agents/scripts/run_guardrail_probes.py`, guide `agents/guides/ai/guardrail-probes.md`): 18 scripted probes
  of the Article 0 rules (no unasked commit or push, destructive actions, instructions planted in files,
  secrets, honest reporting, authority and gates). Run them against your own agent in three set-ups: with the
  kit, with a five-line rules file, with nothing. A self-test proves that each probe can pass and can fail.
  A probe result is a check of one run of one agent, not a proof.

### Added — optional hooks

- `--hooks` for `npx gabbe-kit init`, the wizard and `gabbe setup` installs optional hooks for Claude Code
  (`.claude/settings.json`), Cursor (`.cursor/hooks.json`) and git (`pre-commit`, `pre-push`). Nothing is
  installed unless you ask. Existing settings are merged, backed up first and never replaced; `uninstall`
  removes exactly the entries it added. Guide: `agents/guides/ops/hooks.md`.
- What they do: a shell guard asks before a commit, push, tag, publish or deploy and before destructive git
  commands (`reset --hard`, `clean -f`, `checkout -- .`, `branch -D`, `rebase`, forced push), also behind
  `time`, `nice`, `sudo` and similar prefixes and inside `python -c`, `node -e` and similar; an edit guard
  protects the kit's rule files, the install record, `.mcp.json`, `.npmrc`, `.pypirc` and the hook files; the
  session-start hook shows the resume note as quoted, labelled data and asks the agent to confirm with you
  before acting on it; the git hooks stop a commit that stages a secret-looking value and remind before a
  push.
- What they do not do: they do not see `--no-verify`, aliases, functions, scripts, edits made through the
  shell, or secrets in binary files. They are a second check, not a sandbox.

### Changed — installers

- **`npx gabbe-kit uninstall`, `update` and `doctor`**: a project installed without Python can now be
  reversed, refreshed and checked. `uninstall` follows the same rules as `gabbe uninstall` and is tested
  against it.
- The wizard records each agent's instruction link under that agent, so `gabbe uninstall --agents cursor`
  removes the Cursor link too; for Windsurf, Cline and Devin it now writes real `<name>/SKILL.md` folders
  instead of a link to `agents/skills`; its list of open fields shows names with a hint.
- `install.sh` and `install.ps1` pass their arguments on; `uninstall.sh` and `uninstall.ps1` work without the
  Python tool, are in the npm package, and take `-DryRun`, `-Agents`, `-Purge`, `-Dir` as real parameters. A
  CI job runs the PowerShell scripts on Windows.

- `init`, `update` and the wizard remove generated skill and rule files that an earlier install recorded and
  the kit no longer emits (the four renamed skills, for example `agent-interoperability` → `agent-interop`),
  only when the file is unchanged and lies in a folder that run emitted into. A file you changed is kept and
  reported.
- **`update` shows you the kit's new version of a file you changed.** `agents/AGENTS.md` and
  `agents/CONSTITUTION.md` are kept once you changed them; `update` now writes the kit's version next to the
  kept file as `<name>.gabbe-new` and says so, in both installers, so the new rules can be compared and
  merged (`docs/UPGRADING.md`). `npx gabbe-kit update` now also replaces one of these files when you never
  changed it, as `gabbe update` already did.
- The wizard no longer writes through a link planted at `.aider.conf.yml`, `opencode.json`, the memory files
  or `.gitignore`, and creates no folder under a planted folder link.
- **A wizard install is reversed byte for byte.** The wizard appended `.env` lines to an existing
  `.gitignore` without a backup or a record, so uninstall left the change; the lines now go into a marked
  block, after a backup, and both uninstallers restore the file exactly. A declined merge into an `agents/`
  folder that holds no kit stops with exit 1 instead of printing "Template not found" and exiting 0.
- Python caches (`__pycache__`, `.pyc`) of a used checkout are no longer copied into a project; the kit's
  integrity check no longer writes them and now passes inside an installed project. The count the Node
  installer prints equals the number of paths in the record. `gabbe init` creates an empty `project/TASKS.md`
  when it is absent, so `gabbe verify` passes its file check right after an install. Windsurf no longer gets
  a stray link inside `.windsurf/skills`. The package build asks for the setuptools version it needs (77).
- **The wizard no longer overwrites `agents/memory/PROJECT_STATE.md`.** With "Agent Analytics" on (the
  default answer) every run wrote a one-line stub over the file, which lost the project's recorded state on
  a re-run. The file is now created only when it is absent, and the PowerShell set-up script writes the same
  14-phase state as the shell script (it still wrote the old `S00_INITIALIZED`).
- The Node installer's output is complete when it goes to a small or slow pipe; a long list, for example
  `uninstall --dry-run`, could be cut while the exit code stayed 0. The wizard ends with one error line, not
  a traceback, when a folder it needs is a dangling link.
- `gabbe uninstall --agents` accepts the same short names as `npx gabbe-kit uninstall` (`claude` for
  `claude-code`); a name that matches no recorded agent prints the agents the record has.

### Changed — Claude Code plugins

- **One overall plugin, `gabbe`**: 49 skills that cover the whole system (a start-here skill that carries
  the operating rules and the map, session and memory, requirements and design, build and verify, release,
  existing projects, security, assurance, research). It is the plugin for Anthropic's directory. Its README
  says what it includes, how to start, what it runs and what it does not include.
- Loki mode and Brain mode are no longer in `gabbe`: they need the personas and guides of the full kit and
  are in `gabbe-brain`. Eight kit-operation skills moved to a new plugin, `gabbe-extras`. The ten topic
  plugins stay in the project's own marketplace.

### Security — fixes from an audit of this release before it was tagged

Two audits of the working tree on 21 November 2026 (code and tools; supply chain, CI and kit text) and new
property tests found the defects below. All are fixed and pinned by tests.

- **Installers treat a project as untrusted input.** `gabbe uninstall` followed a recorded path ending in `..`
  in a tampered `.gabbe/manifest.json` and deleted files in the folder above the project; the Node installer's
  cleanup of renamed skills could delete a generated file in another project. A recorded path that is
  absolute, contains `..` or leaves the target is now refused in both installers. The wizard ran the target
  project's own `agents/scripts/compile_skills.py`; it now runs the compiler of the kit being installed. The
  install record is no longer written through a link.
- **The install record is untrusted inside the project too** (found by a second audit, which attacked the
  first fixes). A tampered record could name a planted link as a "backup"; `gabbe uninstall` moved it into
  place and then deleted files through it, outside the project. A record could also delete `.env` or git
  files, or swap a local settings file for the repository's. Now uninstall, `update` and `doctor` check every
  path again right before use, remove a file only when its bytes match the recorded hash, move a backup back
  only under the two backup names and only when it is a real file, keep unknown kinds, keep `.git/` files
  other than the two marked hooks, and take out only the kit's own hook entries. An edited kit file now
  stays in place instead of being backed up and removed.
- **State files are not written through links.** With `project/`, `project/state.db` or `project/logs` a link,
  GABBE writes nothing there: the tool server runs read-only without an audit trail and command-line commands
  stop with one line and exit 1.
- **Bootstrap scripts.** `uninstall.sh` and `uninstall.ps1` no longer import a `gabbe/` package from the
  project folder. All four scripts run `gabbe-kit@<their release>` instead of the newest version (override
  with `GABBE_KIT_VERSION`; `latest` gives the old behaviour).
- **Tool server**: the allow-list, size limits and token fixes listed under "tool server" above.
- **Audit trail.** Redaction now covers assignments whose name contains `password`, `secret`, `token` or
  `api_key` (`OPENAI_API_KEY=`, `AWS_SECRET_ACCESS_KEY=`), JSON members named like secrets, `Authorization`
  headers, passwords in URLs and connection strings, `--password`-style options, GitHub, npm, GitLab, Slack,
  Google, Hugging Face and Stripe tokens, JSON Web Tokens and private-key blocks (list in `SECURITY.md`). On POSIX, `project/logs` is created with mode 0700 and `state.db` and the run logs
  with 0600. The content cache neither writes nor reads through a link.
- **`state_import.sh`** refuses a bundle whose member names contain a backslash or a control character and
  any path that would leave `agents/memory`; a crafted name could replace files under `agents/`. With
  `--apply` it also refuses to write when the destination, a folder above it or the backup folder is a link.
- **Skill packs.** A skill description copied into a generated Cursor rule is reduced to one line, so it can
  no longer add keys such as `alwaysApply`. The registry import scan also flags `wget`/`fetch` piped to a
  shell, `<(curl` and reads of `~/.ssh/`, reverse shells, download-then-run, reads of `.env`, cloud
  credentials and browser profiles, PowerShell download-and-`iex`, invisible characters and
  prompt-override phrases; every redirect is checked, downloads stop at 20 MiB, special files are refused.
  Import accepts only the frontmatter keys the kit's own skills use and refuses a skill named like a kit
  skill; the compiler keeps the kit's skill on a name collision and copies only known keys.
- **Policy engine and `.env`**: the fail-closed fixes listed under "command line" above.
- **Hooks**: the pre-commit secret check could be bypassed by a line starting with `++ `; `merge-hooks.js
  --remove` removed more than GABBE's own entries, and the helper wrote through links. All fixed before first
  release. The shell guard also asks before about thirty more publish and deploy commands (`gh workflow
  run`, `docker build --push`, `twine upload`, `npm unpublish`, `terraform destroy`, `kubectl delete` …); the
  pre-commit check knows `github_pat_`, `npm_`, `glpat-` and `AIza` tokens and reads UTF-16 files.
- **Publish workflows** no longer leave the job token in the checkout while `npm publish` runs; a manual
  npm publish validates the dist-tag and uses `next` for a prerelease tag.
- **Package launchers pinned.** Every `npx` line in the MCP template and guide and in the skills names an
  exact version, verified on npm on 21 November 2026 (35 MCP servers pinned). 28 template entries name
  packages that npm does not have: they are marked `_review` and switched off. Five deprecated servers are
  pinned to their last version and marked. A Semgrep line that named the wrong npm package and a
  `curl … | sh` line for Lean are replaced by pointers to the official install pages.
- Still open, and said so in `SECURITY.md`: git tags are not signed, the release assets have no checksums
  file, and `npx` prefers a project-local `gabbe-kit` of the same version.

### Added — GABBE's own assurance

- Property and stateful tests of the parts that can lose a user's work: task sync (a state machine against
  a model), the policy engine, the installers (sequences of install, update, uninstall and user edits: nothing
  outside the target changes, no user file is lost, no backup is overwritten), `.env` loading and the
  instruction-file pointer block. They found twelve defects; all are fixed in this release.
- A mutation-score floor for `budget`, `sync` and `route` (measured 59.6%, floor 55%) checked in the nightly
  CI job by `scripts/gates/check_mutation_floor.py`. The nightly mutation step had not produced a result
  before: it installed a version of the tool whose options had changed.

### CI and release

- **One release gate in front of every publishing path** (`.github/workflows/gate.yml`): the tag must equal
  every version number (Python package, npm package, `server.json`, `CITATION.cff`, the four bootstrap
  scripts) and the Python and Node suites must pass before anything is published to PyPI, npm or GitHub
  Packages or attached to a release. A manual run publishes only from a version tag. The gate can be run by
  hand as a dry run.
- Every GitHub Action is pinned to a commit; `trivy-action` is pinned to the release its advisory names as
  safe. CI's gate job and the release gate install from the hashed lock file.
- PyPI: the publish job can use trusted publishing (no long-lived token) and has only the permissions it
  needs. The wheel and the source archive no longer contain the test suite.
- The npm package now includes `SECURITY.md` and `CHANGELOG.md`.
- `SECURITY.md` says how releases are built and what you can verify.
- `CITATION.cff`; `docs/SUPPORT.md` (what is stable, supported versions, maintenance after 1.2.0).

## [1.1.4] — 2026-11-21 — safety and truth

Fixes for defects that could lose a user's files, weaken security, or made a document false. No new
feature. Found by a full audit of 1.1.3 on 21 November 2026.

### Fixed — installing, updating and uninstalling

- **`gabbe update` no longer damages a wizard install.** In 1.1.3 it replaced `agents/AGENTS.md` and
  `agents/CONSTITUTION.md` without a backup, removed wiring links and stopped with
  `Is a directory`. It now keeps the earlier install record and everything in it, keeps the
  preserved files you changed, and copies a kit file you edited to `<name>.gabbe-bak` before
  replacing it. A kit file that is no longer shipped is removed only if you never changed it.
- **`gabbe uninstall` removes only what an install recorded.** It no longer deletes your own files
  inside `.claude/skills`, `.github/skills` or `.cursor/rules`. `--purge` no longer deletes the
  whole `agents/` folder: your own files, files you changed, memory files and backups stay, and
  the command says how many files it kept. `--dry-run` lists exactly what a real run removes. A
  preserved kit file you never changed (`agents/CONSTITUTION.md`, …) is now removed too, so an
  untouched install uninstalls to the exact state before it. A link you later replaced with a
  file of your own is left alone.
- **The npm installer keeps an instruction file you already have.** A root `AGENTS.md`,
  `.github/copilot-instructions.md`, `.cursorrules` and the other per-agent files are no longer
  replaced by a link: the installer appends a short marked block that points to
  `agents/AGENTS.md` and saves the original as `<name>.gabbe-bak`. The wizard does the same.
  `--force` still replaces the file, after moving it to a backup name that is not in use.
- **The npm installer records what it installs** in `.gabbe/manifest.json`, like the wizard, so
  `gabbe uninstall` can reverse it. On an install without a record, `gabbe uninstall` now exits
  with status 1 and an explanation; it used to print "Removed 0 path(s)" and exit 0.
- **A backup is never overwritten.** If `<name>.gabbe-bak` (or `<name>.bak`) exists and holds
  something else, the next backup is `<name>.gabbe-bak.1`. Re-running an installer after a second
  edit no longer loses that edit.
- **Your own skill or rule with the same name as a kit skill** is saved next to the kit's file
  instead of being overwritten (npm installer and wizard).
- **Symbolic links of yours are kept and never written through.** A link at a path the kit wants
  (`AGENTS.md -> CLAUDE.md`, a linked `.claude/skills`, a linked file under `agents/`) used to be
  removed or followed, which could overwrite a file outside the project. `gabbe update` refuses
  an `agents/` folder that links outside the project.
- **A failed backup stops the install** before anything is overwritten (it used to continue). An
  install that stops part-way still records what it had written.
- **The pointer block keeps your bytes.** It is added and removed without changing the encoding or
  the line endings of your file. A read-only instruction file is left alone with a message.
- **A damaged install record is never acted on and never deleted**: `gabbe uninstall` and
  `gabbe update` stop with an explanation. A recorded path that you replaced by a folder or a link
  no longer stops `update` or `uninstall`; it is left alone.
- `gabbe uninstall --dry-run` prints every path. `--purge` is kept for compatibility and is the
  same as a plain uninstall, which now also removes the empty folders left under `agents/`.
- `agents` that is a regular file is refused with a message; `agents` that is a link is used as it
  is, and nothing is copied into it.
- A file that was already there and equals the kit's is not recorded as installed, so uninstall
  does not remove it.
- **The npm installer no longer copies the kit's documents into your `docs/` folder.**
- **The wizard no longer overwrites** an existing `.gemini/settings.json` (kept), `SETUP_MISSION.md`,
  `BOOTSTRAP_MISSION.md` or `BROWNFIELD_ONBOARDING.md` (backed up first), and records
  `BOOTSTRAP_MISSION.md` for uninstall.
- **Credentials in the git remote address are no longer written into `agents/AGENTS.md`.** A remote
  such as `https://user:token@host/o/r.git` is recorded as `https://host/o/r`.
- **The npm installer writes `BOOTSTRAP_MISSION.md`**, the first prompt the guides tell you to give
  your agent, prints that next step, and says how many `[PLACEHOLDER]` fields `agents/AGENTS.md`
  still has. An unknown option now exits with status 2; it used to print the help and exit 0.
- Three memory templates named in the template index were missing from the repository and the
  packages: `PROJECT_STATE_TEMPLATE.md`, `CONTINUITY_TEMPLATE.md`, `VOTING_LOG_TEMPLATE.md`.
- `agents/scripts/state_import.sh` runs under `dash` (`/bin/sh` on Debian and Ubuntu), removes its
  temporary directory on every exit, and exits 0 after a successful `--apply` without a backup.

### Security

- **A project `.env` can no longer switch off the tool server's protection or redirect your API
  key.** Only an allow-list of keys is read from `.env` (see `SECURITY.md`). `GABBE_MCP_*` and
  `GABBE_POLICY_FILE` are never read from it, and no non-GABBE variable is. `GABBE_API_URL` is read
  from `.env` only when `GABBE_API_KEY` does not come from your shell. **If you keep `GABBE_API_URL`
  in `.env` and export the key in your shell, export the URL as well**; a warning names any refused
  key.
- Redaction of long strings no longer takes seconds (an email pattern was quadratic: 8 s on 40 kB).
- The tool server refuses oversize requests before it traces or validates them.

### Changed — tool server (`gabbe serve-mcp`)

- A command that fails (non-zero exit, blocked by the allow-list, timed out) is returned with
  `isError: true`.
- An unknown tool or invalid arguments answer `-32602` (was `-32603`); a request that is not a JSON
  object, or has non-object `params`, answers `-32600`; a parse error carries `"id": null`; a
  policy denial answers `-32001` with the reason; an open circuit, rate limit or exhausted budget
  answers `-32002`.
- `ping` is answered. `initialize` returns the protocol version the client asked for when the
  server supports it (`2025-11-25`, `2025-06-18`, `2025-03-26`, `2024-11-05`). A notification (a
  message without `id`) is never answered. The MCP revision `2026-07-28`, which has no
  `initialize` handshake, is not implemented.
- A malformed command (unbalanced quote, missing executable) is an error result and no longer
  counts against the circuit breaker; an open circuit lets one trial call through after 30 seconds.
- A tool's `allowed_roles` are enforced.
- Notice: in 1.2.0 the server will offer read-only tools by default, and `run_command` only behind
  an explicit flag.

### Changed — kit and documents

- Skills: destructive steps ask first. `production-health` (`kill -9`, deleting working memory),
  `safety-scan` (removing a secret), `ci-autofix` (commit and push), `sdlc-checkpoint` (`git tag`)
  and `dev-workflow` (rebase) now propose the action and run it only after the human confirms or
  asked for it in that request.
- The Loki activation prompt no longer says "Do not ask me for permission": it stops at every Human
  Approval Gate and before any commit, push, publish or deploy (README, guides).
- Documents corrected against the code: what the installers do to existing files, `update` and
  `uninstall`, the budget keys that are and are not enforced, "zero-dependency" (true for the npm
  installer and the kit; the Python CLI needs three packages), 66 MCP entries, agent counts, roadmap
  version and hook rows, unsupported figures in the quick guide.
- `agents/AGENTS.md` points to the online kit documentation instead of a `docs/` path that only
  existed in npm installs.

### CI

- The vulnerability gate (`scripts/gates/run_gates.sh`, gate 6) compares against the baseline
  whenever `pip-audit` produced results; it used to compare only when there were none. It audits
  the pinned dependency set (`requirements-lock.txt`), not the tools of the environment it runs in.
- The Node installer tests run in CI, with an install → `gabbe uninstall --purge` round trip, and
  the state export/import round trip runs under `sh`.
- The nightly mutation job writes its result to the job summary and stores it as an artifact.
- New tests: install, edit, update and uninstall round trips in a project that has its own files
  (`scripts/tests/test_install_roundtrip.py`), `.env` cases (`gabbe/tests/test_env_file.py`),
  tool-server protocol cases (`gabbe/tests/test_mcp_protocol.py`).

## [1.1.3] — 2026-10-31

Fixes from the documentation audit of 29–30 October 2026; no new feature, no change to a default.

### Changed
- `project/state.db` is no longer tracked. It is runtime state that `gabbe init` and `gabbe db --init` create and that tests and agents change on every run; contributors no longer need `git update-index --skip-worktree` for it.
- **npm publishing uses npm trusted publishing (OIDC).** `publish-npm.yml` is now the only npm publisher: it runs
  on every version tag and by hand, needs no `NPM_TOKEN`, and adds npm provenance. `release.yml` no longer
  publishes to npm. A token-based publish had started to fail because npm now asks for a one-time password.
- Docs: final audit corrections (CLI dependencies, `gabbe brain` and `gabbe route` behaviour, template counts, lifecycle stage names, test counts, `compile_skills.py` command, `--wizard` flag).
- Docs: corrected stale commands, paths, flags and claims found by a documentation audit (`gabbe doctor` vs the npm `gabbe`, the QUICK_GUIDE install line, `GABBE_MCP_TOKEN` and `GABBE_AUTONOMY` behaviour, `setup-context.sh` and guide paths, Python 3.9+); added `docs/ARCHITECTURE.md`, a CI workflow table in `TESTING.md` and a release procedure in `CONTRIBUTING.md`.
- `gabbe setup --force` passes `--force` to the wizard; `npx gabbe-kit init --help` lists `--force`.
- Kit: Security & Guardrails sections in `visual-whiteboarding` and `performant-php` (all 214 skills now have one);
  kit stamps read 1.1.2; fixed `setup-context` paths, the PRD template placeholder and a nonexistent `gabbe budget`.
- Contributor `AGENTS.md` at the repository root; `mypy --strict` passes on `gabbe/*.py`; SECURITY.md lists 1.1.x.

### Fixed

- **The npm installer rejects unknown commands.** `npx gabbe-kit doctor` (or any unknown word) used to fall
  through to `init` and copy the kit into the current folder; it now prints the usage and exits 1.
- **The wizard no longer copies `setup-context.sh`/`.ps1` to the project root.** Run from there, the script
  wrote `.claude/`, `.cursorrules`, `memory/` and other files into the folder above the project. Run it from
  `agents/scripts/`.
- **MCP template package names.** `@context7/mcp-server` and `@sentry/mcp` do not exist on npm; the template and
  the agentic guide now use `@upstash/context7-mcp` and `@sentry/mcp-server`.
- `agents/scripts/verify_e2e_init_flows.py` always failed (it matched `gabbe verify` in `python -m gabbe.main verify`);
  it now passes its 12 permutations and runs in CI.
- The serve-mcp stdio tests run in a temporary project, so test runs no longer write into `project/state.db`.

## [1.1.2] — 2026-10-23 — `gabbe verify` exit code; Claude Code plugins

### Fixed
- **`gabbe verify` now exits 1 when verification fails.** It printed "Verification FAILED" but exited 0, so CI
  jobs and scripts that ran it always passed. `gabbe verify --chaos` already exited 1. Two tests cover both
  outcomes (`gabbe/tests/test_main.py`).
- README: the opening bullet no longer claims to be the first such project world-wide.

### Added
- **Claude Code plugins + marketplace** — `scripts/build_claude_plugin.py` converts all 214
  `agents/skills/**/*.skill.md` into Agent Skills `SKILL.md` folders under `plugins/` (name =
  file name, description + "Use when:" triggers, `license: CC-BY-SA-4.0`, metadata with the
  source path; body unchanged; templates and guides a skill names, with or without the
  `agents/` prefix, are copied beside it at that path) and writes
  `.claude-plugin/marketplace.json`. Eleven plugins: `gabbe` (core, 44 skills) plus ten topic
  plugins (`gabbe-ai` … `gabbe-security`), because all 214 descriptions exceed Claude Code's
  skill-listing budget. Install: `claude plugin marketplace add andreibesleaga/GABBE` then
  `claude plugin install gabbe@gabbe`; skills.sh: `npx skills add andreibesleaga/GABBE -a
  claude-code`. `scripts/tests/test_claude_plugin.py` keeps the tree in sync and checks the
  format, the plugin-directory limits, the icon (source `docs/assets/claude-plugin-icon.png`),
  that every kit template or guide a skill names is copied, and that the plugins are content
  only. The generated `plugins/` tree is skipped by markdownlint and lychee and marked
  `linguist-generated`.
- **`docs/ROADMAP.md`** — the planned work after 1.1.1: an off-by-default agent hook set
  (`npx gabbe-kit init --hooks`) for the four rules a hook can enforce, what stays prose, the
  per-agent coverage, and the `gabbe verify` exit-code fix.
- **GitHub Packages mirror** — `.github/workflows/publish-github-packages.yml` publishes the npm
  package a second time to GitHub Packages as `@andreibesleaga/gabbe-kit` (owner scope required there)
  on every `v*` tag or by manual dispatch, so it is listed in the repository "Packages" sidebar.
  npmjs.com stays canonical (`gabbe-kit`), PyPI stays `gabbe` (PyPI has no GitHub Packages
  equivalent); the committed `package.json` is untouched and already-published versions are skipped.
- **GitHits MCP server** added to the catalog (now **66 MCP servers**). GitHits lets
  the agent navigate the open-source code your app depends on — searching, grepping,
  and reading dependency source, docs, issues, PRs, and changelogs without cloning,
  preventing dependency-API hallucination (no API key). Wired into
  `agents/templates/core/MCP_CONFIG_TEMPLATE.json` (Version Control section,
  default-enabled), documented in `docs/MCP_CONFIGURATIONS.md` (per-server guide +
  SWEBOK v4 Construction map), and surfaced as an essential server in `README.md`,
  `docs/README_FULL.md`, `docs/QUICK_GUIDE.md`, `docs/POST_INSTALL.md`, and
  `gabbe doctor` post-install next-steps. Setup: `npx githits@latest init`
  (auto-detect) — docs at <https://docs.githits.com/>.

---

## [1.1.1] — 2026-06-19 — Capability-layer content audit (consistency, accuracy, honesty)

Patch release. A deep semantic/structural audit of the Markdown capability layer
(skills, guides, templates, brain/loki docs) was run and its findings fixed.
Content-only and strictly additive — no public API / CLI / config / DB change;
all six backward-compat gates pass and the emitter golden vault was recaptured.

### Fixed — consistency
- **Unified the SDLC phase model** across skills, guides, templates and `AGENTS.md`:
  the lifecycle is consistently described as **S00–S13 (14 phases = 10-phase core
  build loop S01–S10 + Day-0 S00 + Day-2 S11–S13)**; resume-guards, checkpoint
  tables and `[X]/10` counters now cover S00–S13 so Day-0/Day-2 work is never
  treated as "not a real phase".
- **Unified the human-in-the-loop hard-gate set** to **S00 (GO/NO-GO), S01, S02,
  S07, S08** everywhere (S00 was previously dropped from several "canonical" lists).
- **Coverage gate** stated as `>= 99%` consistently; example logs that showed a
  sub-99% run as `PASS` were corrected.
- **`AGENTS_TEMPLATE.md` re-synced to the live operating spine** (Step 0 Preflight,
  the CRITICAL MANDATES, RESUME_POINTER continuity, Self-Evolving policy, Loki/Brain
  orchestration), honouring `AGENTS.md`'s "both modes share the same spine" invariant.
- **De-duplicated overlapping guides** (`design-patterns`↔`software-design-patterns`,
  `agentic-patterns`↔`agentic-design-patterns`) to a single source of truth + pointers.

### Fixed — accuracy & honesty
- **Brain/Active-Inference honesty**: `ADR-0002`, `beyond-llms.md`,
  `agent-only-cognition.md` and the `cost-benefit-router` skill now describe the
  **actual** mechanism (epsilon-greedy bandit + single-parent LLM rewrite; no
  crossover/culling; `gabbe route` is a separate one-shot decision) and label
  Active-Inference/Free-Energy framing as *framing, not implemented math*; removed
  "guarantees correctness"/"mathematically guarantees" superlatives.
- **Security/crypto**: corrected an inverted allow-list instruction; replaced a
  non-existent tool name (`Rebertha` → **Presidio**); down-ranked known-weak prompt
  defenses; fixed Ed25519/X25519 conflation, `RFC 7807`→`RFC 9457`, CRYSTALS-Kyber→
  **ML-KEM (FIPS 203)**, added a post-quantum/crypto-agility note; pseudonymization vs
  anonymization; keyed-HMAC blind indexing.
- **Restored a corrupted architecture diagram + step list** in `ai-agentic.md`.
- Fixed broken capability references, the "Lethal Trifecta" misuse in
  `critical-systems-arch.md`, conflicting monolith→microservices thresholds, stale
  frontier-model names, several typos, and markdownlint blank-line compliance.

> Lower-severity stylistic items remain tracked; this release clears every blocker
> and major finding from the audit.

---

## [1.1.0] — 2026-06-19 — Install safety, brownfield mode, fuller population, broader tests

Minor release. New features and a hardened install/uninstall contract. Backward
compatible: the public API / CLI / config / DB / emit schema remain additive
(all six backward-compat gates pass); the only intentional emitted-artifact
change is a richer `agents/AGENTS.md` (more fields populated), with the Gate 4 /
golden baseline recaptured to match.

### Fixed (pre-release content audit)
- **Markdown compliance** in `agents/AGENTS.md` and `AGENTS_TEMPLATE.md` — headings,
  fenced code blocks, and lists are now surrounded by blank lines (markdownlint
  MD022/MD031/MD032); whitespace-only.
- **Restored a corrupted diagram + step list** in `guides/ai/ai-agentic.md` (stray
  skill-table fragments had been spliced into the architecture diagram and the SDD
  Phase-3 numbered list).
- **Corrected an inverted security instruction** in `secure-coding.skill.md`
  (allow-list now reads "accept known **good** characters", not "bad").
- **Replaced a non-existent tool name** (`Rebertha` → **Presidio**) in
  `ai-safety-guardrails.skill.md`.
- **Fixed broken capability references**: `backend-coder` → `eng-backend`,
  `arch-architect` → `prod-architect`, `architecture-design` → `arch-design`.
- **Corrected a quality-gate example** that showed `84% coverage | PASS` against a
  ≥99% coverage gate (now `99%`).

### Added
- **Never-clobber install.** Both install paths (the Python wizard
  `scripts/init.py` and the Node installer `bin/install.js`) now back up any
  differing pre-existing file to `<name>.gabbe-bak` before refreshing it, so a
  project's existing `docs/`, agent rule files, etc. can never be silently lost.
  A new `--force` flag opts into re-templating preserve-set files (still backed
  up first).
- **Reversible wizard installs.** The wizard now records everything it creates
  under the project (copied kit files, wiring symlinks, generated skill trees,
  config files) into `.gabbe/manifest.json`, so `gabbe uninstall` fully reverses
  a wizard install and restores any backed-up user file.
- **Brownfield autodetect + refactor mode.** `gabbe/detect.py` sniffs the target
  for an existing codebase (language/framework/package-manager/git). When one is
  found the wizard asks a greenfield-vs-refactor Mode question, prefills detected
  defaults, and in refactor mode scaffolds a `BROWNFIELD_ONBOARDING.md` discovery
  brief instead of greenfield mission docs.
- **Fuller placeholder population.** Derivable `[PLACEHOLDER:]` fields in
  `AGENTS.md` (dev/test/lint/format/typecheck/coverage commands, `repo_url`,
  `ci_cd`, `deployment_target`) are filled from your answers and detection.
  Genuinely project-specific fields are kept but tagged `<!-- OPTIONAL -->` and
  reported in an end-of-install warning — never shipped as silent blanks.

### Fixed
- **Uninstall no longer follows symlinks.** `_resolve_within` resolves the parent
  only, so wired entries (e.g. `.cursorrules`, root `AGENTS.md`) are removed
  directly instead of being dereferenced and left behind.
- **Uninstall preserves user edits.** A user-modified installed file is backed up
  to `<name>.gabbe-bak` (with a warning) instead of being silently deleted, and
  now-empty wiring directories (`.claude/`, etc.) are pruned.

### Tests
- New end-to-end coverage: never-clobber/backup (Python + a zero-dependency Node
  e2e), wizard manifest round-trip, brownfield detection + wizard flow, placeholder
  population, MCP-over-stdio (handshake/auth/`serverInfo.version`), markdown-plane
  emission, a slow wheel-build-and-install sandbox, a wizard-flow snapshot, and
  mermaid diagram validation.

---

## [1.0.3] — 2026-06-18 — Kit-version stamps refreshed; emitter golden vault recaptured

Patch release. Supersedes 1.0.2 (whose `GABBE CI` run was red — the kit-version
stamp bump below changed byte-frozen emitter artifacts without recapturing the
golden baseline). Strictly additive to the public API / CLI / config / DB / emit
schema; the kit-version-stamp change is an intentional, reviewed content update
to emitted artifacts, with the Gate 4 / golden baseline recaptured to match.

### Changed
- **Kit-version stamps now read 1.0.3** in `agents/AGENTS.md`,
  `agents/CONSTITUTION.md`, and `agents/templates/coordination/AGENTS_TEMPLATE.md`
  (they had drifted to 0.9.6 / 0.8.0). `scripts/registry_export.py` and
  `agents/scripts/state_export.sh` read this stamp, so exports now report 1.0.3.
- Recaptured the emitter golden baseline (`scripts/tests/golden/baseline_v0.8.0`)
  so the golden-emitter tests and **Gate 4 (emitter fixture vault)** stay green
  with the refreshed stamps.

### Fixed
- Carries forward the 1.0.2 fix: MCP `serverInfo.version` reads
  `gabbe.__version__` dynamically (no drift from the package version).

---

## [1.0.2] — 2026-06-18 — MCP server version no longer drifts from the package

Patch release. Strictly additive — no public API / CLI / config / DB / emit
change; the backward-compat gates stay green.

### Fixed
- **MCP `serverInfo.version` reported `1.0.0` on the published `gabbe` 1.0.1.**
  The version string in `gabbe/mcp_server.py` was hardcoded and was not bumped at
  release time, so an MCP client calling `initialize` saw `1.0.0` even though
  `gabbe --version` reported `1.0.1`. The server now reads `gabbe.__version__`
  dynamically, so `serverInfo.version` always tracks the package version and
  cannot drift again.

---

## [1.0.1] — 2026-06-17 — Registry publish (`gabbe-kit` on npm) + install-doc accuracy

Patch release. Registry publishing is now live and all install channels were
audited end-to-end. Strictly additive — no public API / CLI / config / DB / emit
change; the 6 backward-compat gates stay green.

### Changed
- **npm package is now `gabbe-kit`** — `npx gabbe-kit init`. npm's name-similarity
  policy refuses the unscoped `gabbe`, so the npm channel ships as `gabbe-kit`. The
  **PyPI package and the installed command stay `gabbe`**; the package exposes both
  `gabbe` and `gabbe-kit` bins, so the `gabbe` command is unchanged.

### Fixed
- **Shell / PowerShell bootstrap** (`install.sh`, `install.ps1`) `exec`'d
  `npx --yes gabbe init` (404) — corrected to `gabbe-kit`, restoring the
  `curl … | sh` install channel.
- CLI hints in `gabbe/main.py` (and the `MANIFEST.in` / `pyproject.toml` comments)
  now point to `npx gabbe-kit init`.

### Docs
- README documents all four install channels explicitly (npm / PyPI / shell / git).
- Corrected install-channel claims to match audited behavior: manifest-backed
  `update` / `uninstall` is scoped to the Python `gabbe` CLI path — the
  `npx` / `curl` / `scripts/init.py` installs are not manifest-tracked (remove
  manually); `pip install gabbe` installs the **CLI only** (the kit lands via
  `npx gabbe-kit init` / `curl … | sh` / a checkout, and `gabbe setup` wires the
  kit only from a checkout).

---

## [1.0.0] — 2026-06-17 — Cradle-to-grave ADLC, evals & guardrails, advanced testing, reversible multi-OS install

The v1.0 release. Strictly **additive and backward-compatible**: all 6 CI gates
(api-surface, cli-help, config-schema, db-schema, emitter-vault, cve-delta) and
the additive-only emit pipeline stay green — no public API/CLI/config/DB/emit key
is removed or retyped, so existing agents, prior-version projects, and existing
procedures keep working unchanged. v1.0 broadens the methodology layer to the
**entire** lifecycle (S00–S13), adds an evaluation + standards-grounded guardrails
layer, deterministic property/fuzz/chaos/mutation testing, hardened self-*
capabilities, and a fully reversible, autodetecting, multi-OS install/update/
uninstall path.

> **Honesty note (carried into the skills themselves):** PBT/metamorphic tests and
> evals **sample** an input space and **raise confidence** — they do **not** prove
> correctness. LLM-as-judge is biased-but-useful and is calibrated against human
> labels, never treated as ground truth (`pass^k`/`pass@k` reliability is reported,
> never "proof"). The AI-risk standards map documents **coverage, not
> certification**. v1.0 claims best-in-class coverage, not mathematically guaranteed
> 100% correctness.

> **Distribution note:** the npm package ships as **`gabbe-kit`** (`npx gabbe-kit init`)
> because npm's name-similarity policy refuses the unscoped `gabbe`. The installed
> command and the PyPI package remain **`gabbe`** (`pip install gabbe`, then `gabbe …`).

### Added — Methodology layer
- **Cradle-to-grave ADLC.** New **Day-0 phase S00 — Strategy & Discovery** (opportunity
  framing, ideation, Wardley mapping, market scan, North-Star/HEART, RICE; go/no-go
  human gate before S01) and **Day-2 phases S11–S13** (S11 Operate & Maintain, S12
  Evolve & Continuously Improve, S13 Decommission & Sunset) extend the existing
  S01–S10 SDLC end to end.
- **~19 new skills** grounded in named industry methods — **ADD 3.0** (`attribute-driven-design`),
  **ATAM** (explicit in `arch-review`), **Wardley/JTBD/RICE/North-Star** (`opportunity-assessment`,
  `user-research-synthesis`, `ideation-facilitation`), **DORA/SPACE** (`product-analytics`),
  **ADKAR** (`change-management`), plus `estimation-sizing`, `financial-governance`,
  `fitness-functions`, `spec-driven-development`, `retrospective`, and the Day-2 ops
  set (`observability-stack-setup`, `feature-flag-management`, `runbook-authoring`,
  `dependency-lifecycle`, `decommission-sunset`). Self-contained prose, no inline
  citation URLs.
- **New mid-phase quality gates:** **S02.5** Cost & Feasibility, **S04.5** Parallelism/
  Dependency feasibility, **S06.5** Performance-regression, **S07.5** Sustainability
  (green-software) — documented in `loki-sdlc-phases.md` and `orch-judge`.
- **2 new personas:** `prod-product-ops` (Day-2 metrics/analytics/experimentation owner;
  wired into S11/S12) and `prod-integration` (third-party integration / vendor-SLA
  architect; wired into S02/S03/S05).
- **~13 new templates** (estimation, ADD workbook, fitness function, retrospective,
  runbook, dependency graph, experiment plan, change-management plan, decommission
  plan, property-test checklist, eval plan/golden-dataset/rubric), each registered in
  `agents/templates/00-index.md` and wired to the phase/skill that produces it.

### Added — MCP ecosystem (SWEBOK v4 priority map)
- **8 new opt-in MCP servers** in `MCP_CONFIG_TEMPLATE.json` (now 65 total): `knowledge-graph-memory`
  (Anthropic persistent memory), `mcp-evals` (↔ `eval-driven-development.skill`), `mcp-chaos-rig`
  (↔ `chaos-fault-injection.skill` + `gabbe verify --chaos`), `supabase`, `pagerduty` (Day-2 S11),
  `cloudflare`, `obsidian`, `discord`, plus `google-genai-toolbox`.
- **SWEBOK v4 priority map** in `docs/MCP_CONFIGURATIONS.md` — best self-hostable servers mapped to
  the software-engineering knowledge areas, each tied to a GABBE phase/skill.
- `time-complexity` documented as a **local-GitHub** MCP server (build from source); `semgrep` and
  `google-genai-toolbox` annotated with local-install steps.

### Added — SWEBOK v4 alignment, agentic-AI patterns & AI assurance
- **SWEBOK v4 foundations** — full coverage of all knowledge areas via skills `professional-practice`
  (ACM/IEEE-CS ethics), `empirical-methods` (measurement/experiment design), `configuration-management`
  (SCM discipline), and guides `mathematical-foundations`, `computing-foundations`, `modeling-methods`.
- **Agentic-AI skills** — `context-engineering` (Write/Select/Compress/Isolate, prompt caching),
  `ai-red-teaming` (offensive testing, ASR gating, PyRIT/Garak/Promptfoo), `agent-sandboxing`
  (four-domain intrinsic isolation, locked at creation), `reasoning-patterns` (CoT/ToT/ReAct/Reflexion
  selection), `agent-workflow-patterns` (chaining/routing/parallelization/orchestrator-workers/
  evaluator-optimizer; workflow-vs-agent decision).
- **Agentic-AI guides** — `agent-identity-trust` (KYA, OAuth-for-agents, signed mandates, A2A/AGNTCY),
  `model-customization-decisions` (prompt vs RAG vs fine-tune, SLMs, routing/cascades), plus two
  catalogs: `agentic-design-patterns` (full agentic taxonomy) and `software-design-patterns`
  (classical GoF / architectural / DDD / enterprise-integration patterns).
- **AI-assurance templates** — `MODEL_CARD`, `DATASHEET`, and `SYSTEM_CARD` to make governance concrete.
- **Standards map expanded** — ISO/IEC 5338 (AI lifecycle), 23894 (AI risk), 25059 (AI quality), 22989,
  IEEE 7000-series, NIST AI 600-1 (GenAI Profile), EU AI Act GPAI Code of Practice, Google SAIF→CoSAI;
  `agent-communication` refreshed for the converged protocol stack (A2A→Linux Foundation, AGNTCY /
  Internet-of-Agents, MCP OAuth authorization).
- **Post-install workflow** — `gabbe doctor` prints which MCP servers to enable + how; new
  `docs/POST_INSTALL.md` full environment-setup guide.
- **Methodology upgrades** — predictive cost admission control (reserve→reconcile), multi-agent
  topology-selection matrix + named swarm failure modes, and a grounded-self-critique rule (reflection
  loops require an external anchor) folded into the existing orchestration/patterns skills.
- **Security hardening** — installer agent-name validation + path-containment (the isolation invariant
  holds even against a tampered manifest), with regression tests.

### Added — Evaluation & guardrails (Track E)
- **Eval methodology skills:** `coding/eval-driven-development` (offline eval suites,
  golden datasets, 3-tier assertions deterministic→semantic→LLM-judge, `pass@k`/`pass^k`
  statistical gating), `ai/llm-as-judge` (rubric scoring + known-bias mitigations),
  `ai/rag-evaluation` (Ragas-grounded faithfulness/relevance/context precision-recall),
  `coding/agent-trajectory-eval` (tool-selection precision/recall/F1, trajectory
  in-order match; τ-bench / SWE-bench Verified grounding).
- **Self-eval harness** `agents/scripts/eval_skills.py` (no new core dep; assertions-only
  per-commit, optional LLM-judge under `live_llm`/nightly; emits a JSON scorecard) +
  promptfoo-compatible `agents/skills/<cat>/evals/*.eval.yaml` golden datasets; optional
  **`gabbe eval`** subcommand (new public `run_evals()`).
- **Standards-grounded guardrails:** `security/prompt-injection-defense` (direct vs.
  indirect injection, lethal trifecta, dual-LLM/quarantine, spotlighting; OWASP
  **LLM01:2025**) and `coding/output-validation` (schema-validated output, constrained
  decoding, PII masking; OWASP **LLM05/LLM02**); `ai-safety-guardrails` upgraded with the
  input/output/dialog/retrieval/execution rails taxonomy.
- **`agents/guides/security/ai-risk-standards-map.md`** — coverage map of every GABBE
  skill/gate/persona to **OWASP LLM Top 10 (2025)**, **NIST AI RMF (+ GenAI Profile)**,
  **MITRE ATLAS**, **ISO/IEC 42001**, and the **EU AI Act** (documents coverage, not
  certification).
- **MCP contract hardening:** every string tool input bounded by charset + length
  (`pattern` + `maxLength`); `test_mcp_contract.py` proves schemas valid + adversarial
  payloads fail-closed.
- **Cognitive-mode tests:** `test_brain_invariants.py` and `test_loki_shadow.py`
  (mutually-exclusive states, toy convergence, resume-pointer integrity, loop/resource
  guards, confidence-threshold escalation, self-heal→restore) + new
  `brain/cognitive-testing` skill.
- **`agents/scripts/validate_methodology_graph.py`** — lifecycle state-machine DAG +
  persona-handoff graph + memory state model + skill-shape validator, joining the
  `validate_*`/`verify_*` suite.

### Added — Advanced testing (Track B)
- **Hypothesis property-based test suites** for `budget`/`sync`/`route`/`replay`
  invariants (budget cap never exceeded, sync idempotency/convergence, route
  PII→LOCAL + complexity threshold, replay round-trip).
- **MCP fuzzing** (`hypothesis-jsonschema` against the validated `run_command` handler +
  malformed JSON-RPC envelope fuzzing).
- **Chaos / fault injection** (subprocess timeout, sqlite `OperationalError` mid-txn,
  LLM failure → assert escalation/hardstop/rollback).
- **Mutation testing** (`mutmut`, nightly/non-blocking) and `slow`/`live_llm`/`mutation`
  pytest markers.
- **`gabbe verify --chaos`** — new public `run_chaos_checks()` runs the fault-injection
  self-checks (additive flag; only `cli_help/verify.txt` baseline regenerated).

### Added — Distribution (Track D)
- **`.gabbe/manifest.json` install manifest** recording exactly what each installer
  created (path/kind/points_to/agent/hash/backup_of/versions) — the backbone of
  reversibility.
- **Multi-target install:** project (default), `--global`
  (`$XDG_DATA_HOME/gabbe`, refcounted), and `--dir <abs-path>` custom scope, with a
  tested isolation invariant (nothing written outside the chosen target unless
  `--global`).
- **`uninstall` / `update`** (`npx gabbe-kit …`, `gabbe …`, plus `uninstall.sh`/`uninstall.ps1`):
  manifest-driven, idempotent, restores `.bak` backups, never touches preserve files
  (`memory/*`, `project/*`, `policies.yml`, `AGENTS.md`/`CONSTITUTION.md` edits);
  `--dry-run`, `--purge`, `--remove-agents <list>` deselection.
- **`gabbe doctor`** — single read-only environment + install report that autodetects
  OS/arch, runtimes, installed agent clients, chosen scope, and manifest integrity, with
  a PASS/FAIL per check; multi-OS install verification (`{ubuntu, macos, windows}` ×
  `{npx / pip|pipx / curl|sh | install.ps1}`) plus post-publish `release-verify` of the
  real published artifact.

### Added — Self-* hardening (Track C)
- **Honest self-* guides:** `agents/guides/ai/self-evolving-skills.md`,
  `agents/guides/ai/dynamic-capability-loading.md` (load-or-ask-the-user flow), and
  `agents/guides/processes/extension-protocol.md` (the canonical additive way to add a
  skill/template/persona/guide/agent-client/MCP/model without a breaking change).
- Each self-* capability (self-evolving, self-adaptive, self-healing, dynamic capability
  loading) is paired with an executable proof scenario, and the **"brain inference via
  skills" / self-evolving genes** framing is stated honestly: the production
  `gabbe/brain.py` is epsilon-greedy with a monotonic success-rate, and the free-energy /
  Active-Inference framing is conceptual, not literal math.

## [0.9.6] — 2026-06-12 — Operating spine, universal install, more agents, registry interop

Strictly backward-compatible with the last released tag, v0.8.0-beta (6 gates +
golden + validators green). All new behavior is additive; the only removals are
pre-release internals that never shipped in any tagged release (see Removed).

### Added — operating spine (markdown, runtime-agnostic)
- **`core/preflight`** (mandated Step 0): auto-check + load index summaries + memory
  headers + cost posture + recommend the optimal capability set, then clarify.
- **`core/clarify`**: uncertainty-aware clarifying questions at every step + a
  reasoning-pattern menu.
- **`core/state-preserve` + `core/state-portability`** (+ `state_export.sh` /
  `state_import.sh`): continuous + pre-cutoff checkpointing (RESUME_POINTER) so a
  token/time/crash cutoff never loses progress; portable, agent-agnostic state
  export/import to continue in any other coding agent/LLM.
- **`core/update-scan`**: discover + adopt the best skills/tools/MCPs/models, gated
  by `GABBE_AUTONOMY` + budget; A2-only evolution + misaligned-replay guard;
  protected files; policy-as-code self-enforcement.
- **`coordination/persona-selector`** (selection/tiering/delegation/voting) +
  **`coordination/self-optimize`** (autonomy levels L0–L3 + macro/meso/micro alignment).
- **`core/skills-registry`** + **`core/final-review`** skills.

### Added — first-class concerns
- **Observability**: AGENTS.md/CONSTITUTION mandates + OTel GenAI semantic
  conventions in `gabbe/audit.py` (`genai_usage_attributes`, `record_genai_usage`,
  content-redaction toggle).
- **Spec-Driven**: spec → evals → test → code; EARS; golden-thread traceability.
- **Human–Agent Collaboration**: manager-not-operator; Purpose/Transparency/Control
  (`guides/principles/human-agent-collaboration.md`, `guides/ai/agent-operating-ergonomics.md`).

### Added — agents, install, registry, CLI
- **Six more coding agents**: Antigravity, OpenCode, Zed, Continue, Roo Code,
  Kilo Code (Gemini split out, backward-compatible); universal `.agents/skills/`
  emitter; new golden platforms `antigravity` + `opencode`.
- **Universal install**: `npx gabbe-kit init` (`bin/install.js`), `install.sh` /
  `install.ps1`, `MANIFEST.in` (kit in sdist), `release.yml` (wheel + npm + tarball).
- **Skills-registry interop**: `scripts/registry_export.py` / `registry_import.py`;
  `gabbe registry publish|add` + `gabbe setup` CLI verbs.
- **Per-project policy**: `GABBE_AUTONOMY` + `project/gabbe.config.json`
  (`gabbe/config.py`); pre-step cost reservation `budget.reserve()`/`can_afford()`.
- **`scripts/verify_all.sh` + `TESTING.md`**: one-stop verification + how-to-test.

### Security — release-hardening sweeps (PRs #13–15)
- **Policy engine fail-closed**: a present `policies.yml` with no/empty/null
  `tools` section now denies all (was allow-all / crashed on `tools:` null).
- **Audit redaction closure**: OTel `gabbe.input`/`gabbe.output` span attributes
  are redacted like the JSONL path; non-JSON-serializable objects are
  stringified-then-redacted so `__str__` output can't smuggle PII/secrets past
  `json.dumps(default=str)`.
- **`state_import.sh` hardening**: fatal portable `mktemp` template (no
  predictable temp dir), `pipefail`, `--no-same-owner --no-same-permissions`
  extraction; symlink/hardlink + traversal members already rejected.
- **`setup-context.ps1`**: link detection by `LinkType` (SymbolicLink / Junction /
  HardLink) — never moves a real file/dir mistaken for a link.
- **Consistency gate** grown to 8 invariants (dangling concrete-path scan with
  `agents/` prefix handling, guides-count parity, fence balance, persona
  resolution, gate-label drift, …).

### Changed — typing + hardening pass (Gemini/Antigravity audit + follow-ups)
- **`gabbe/` core fully typed**: `mypy --strict` clean across all 23 core modules.
- **`brain.py`**: gene selection now implements the documented epsilon-greedy
  policy (20% exploration of the newest generation) instead of pure greedy.
- **`sync.py`**: Windows-safe atomic writes (`os.replace` PermissionError retry).
- **`gateway.py`**: tool-argument validation is fail-closed — a parameterized
  tool refuses to execute when `jsonschema` is unavailable (and `jsonschema>=4`
  is now a required dependency, so it always is available on a normal install).
- **`llm.py`**: opt-in `GABBE_LLM_CACHE` (cache identical deterministic LLM
  calls locally; 0 tokens on a hit; off by default) + malformed-JSON handling.
- **New checks**: `scripts/tests/test_capability_layer.py` (kit-wide link +
  frontmatter CI test); `scripts/fill_placeholders.py` interactive setup utility.
- **`update-scan.skill.md`**: self-evolution git-branching workflow (never
  mutate `main`; `evolve/{feature}` branch + tests + human review before merge).
- New regression tests: `GABBE_AUTONOMY` precedence (env > project config >
  `hybrid`), `budget.reserve()` semantics, real-jsonschema gateway validation.

### Removed — pre-release internals (never shipped in a tagged release)
- `gabbe.audit.traced` decorator, `gabbe.config.SKILLS_DIR`,
  `gabbe.config.UNDERLINE` (unused internals; the public span API is
  `start_span`/`end_span`).

## [0.9.0] — 2026-06-10 — Audit Hardening (strict backward-compatible)

### Security
- **MCP server fail-closed by default** (was unauthenticated + allow-all): `gabbe serve-mcp` now blocks commands unless `GABBE_MCP_ALLOWED_COMMANDS` is set and requires a token; `GABBE_MCP_INSECURE=1` restores legacy behavior. Added a subprocess timeout and MCP `protocolVersion` (2025-11-25).
- Skill-name slug sanitization blocks path traversal in the emitter.
- Audit logs (`project/logs/*.jsonl`) now redact emails/keys/tokens.

### Added
- **Dual license**: Apache-2.0 (`LICENSE-CODE`) for code + CC-BY-SA-4.0 for content; SPDX headers on all `.py`.
- `docs/SCHEMA.md` (emitted-format contract), `SECURITY.md`, `CODE_OF_CONDUCT.md`, `docs/adr/` (3 ADRs).
- Golden emitter tests + `scripts/gates/` backward-compat gate harness.
- `requirements-lock.txt` (hashed); ruff/black/mypy tooling; `init.py --bench`.
- CI: docs-lint, security-baseline (osv/pip-audit/trivy), scorecard, SBOM release, dependabot; Python matrix 3.8–3.13.
- Root `AGENTS.md` + `GEMINI.md` emitters; `gabbe-schema-version` in all emitted artifacts.
- Cross-process advisory lock for `gabbe sync`.

### Changed
- **Claude Code skills now emit `.claude/skills/<name>/SKILL.md` directories** (agent-skills standard) — previously symlinked `*.skill.md` files that Claude Code could not discover. Cursor rules are now agent-requested (no `globs: *`).
- `docs/MCP_CONFIGURATIONS.md`: corrected package names verified against npm/PyPI (2026-06-10).

### Fixed
- Installer no longer clobbers user files on the symlink-fallback path.
- `compile_skills.py` backup `.bak` no longer drops file extensions.

---

## [0.8.0] — 2026-03-05

### Changed
- Refactored directories, filenames, and structure
- Updated README.md and fixed inaccuracies in QUICK_GUIDE.md
- Fixed full docs links

### Added
- **Kit Installation Safeguards**: Upgraded `init.py` with `safe_merge_directory()` to natively block overarching uninstalls and safeguard all files in `project/`, `memory/`, `TASKS.md`, `policies.yml`, and `config.json` when pulling GABBE ecosystem upgrades across Local, Global, and Custom architectures.
- **Time Complexity MCP Integration**: Added `time-complexity-mcp` (Big-O static analysis via tree-sitter) as a first-class capability:
  - New skill: `agents/skills/coding/time-complexity.skill.md`
  - New guide: `agents/guides/patterns/time-complexity-analysis.md`
  - New template: `agents/templates/coding/TIME_COMPLEXITY_REPORT_TEMPLATE.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Security & Code Quality section)
  - Updated all index files, `README.md`, and `README_FULL.md`
- **MCP Configurations Guide**: Created `docs/MCP_CONFIGURATIONS.md` — comprehensive per-server installation, API key setup, and usage guides for all 42+ MCP servers in the template. Cross-referenced from `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`, and `MCP_CONFIG_TEMPLATE.json`.
- **Excalidraw MCP Integration**: Added `@cmd8/excalidraw-mcp` for programmatic Excalidraw diagram creation:
  - New skill: `agents/skills/coding/excalidraw.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
- **Sketch-to-Diagram Pipeline**: Added `mcp-image-recognition` + Excalidraw for converting hand-drawn sketches to formal diagrams:
  - New skill: `agents/skills/coding/sketch-to-diagram.skill.md`
  - New template: `agents/templates/coding/SKETCH_TO_DIAGRAM_TEMPLATE.md`
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Sections 4-5)
  - MCP config entry for `image-recognition` in `MCP_CONFIG_TEMPLATE.json`
- **tldraw MCP Integration**: Added `@talhaorak/tldraw-mcp` for persistent visual canvas (9 tools):
  - New skill: `agents/skills/coding/tldraw-canvas.skill.md`
  - MCP config entry in `MCP_CONFIG_TEMPLATE.json` (Design & Visual section)
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 5)
- **Visual Product Design Phase**: End-to-end pipeline for processing visual inputs into structured specs before implementation:
  - New guide: `agents/guides/planning/visual-product-specs.md` (input catalogue, recognition pipeline, output mapping, design readiness gate)
  - New skill: `agents/skills/product/visual-specs.skill.md` (5-phase workflow: collect → recognize → structure → generate → assemble)
  - New template: `agents/templates/product/VISUAL_SPEC_PACKAGE_TEMPLATE.md` (7-section package with design readiness checklist)
  - Updated PRD template: Section 6.1 Visual Data Model + Section 8 tldraw/Visual Spec Package refs
  - Updated guide: `agents/guides/ai/visual-mcp-integration.md` (Section 7 cross-ref)

### Added (Phase 13: Specialized Systems & Standards)
- **Industry Category**: Added specialized software engineering support for:
  - **Telecom & Networks**: TMF ODA, CAMARA APIs, GSMA eSIM (skill, guide, template).
  - **Healthcare**: HL7 FHIR clinical data exchange (skill, guide, template).
  - **Industrial IoT**: OPC UA, MQTT, Purdue Model (skill, guide, template).
  - **Global Standards**: UN SDGs, ITU-T, OSI/OpenSSF compliance (skill, guide, template).
  - **Engineering Standards**: IEEE, ACM Ethics, ISO/IEC 12207 audits (skill, guide, template).
- **Core Specialized Systems**:
  - **FinOps**: Cloud cost optimization auditing (guide, skill).
  - **Scalability**: Horizontal and Vertical scaling architecture audit (skill, guide, template).
  - **Green Tech & Sustainability**: ESG checks, Carbon intensity (SCI) reporting (skills, guides, template).
  - **Blockchain & DLT**: Smart contract and distributed ledger design (skill, guide, template).
  - **Semantic Web**: RDF/OWL Ontology design for meta-knowledge (skill, guide, template).


### Fixed
- Quote Mermaid node labels with parentheses
- Fixed diagrams
- General CLI, format, and Windows compatibility fixes

### Removed
- Removed Android/iOS installation instructions
- Removed loki leftovers from tests

### Audited & Verified
- Conducted a full GABBE deep-audit to guarantee stability across workflows, codebase, and documentation.
- **Workflows & Logic Verification**: `init.py` handles step 0 / step 1 initialization perfectly. The `gabbe` CLI tool `sync`, `router`, and `status` modes execute accurately.
- **Test Suite Execution**: Checked the baseline test health using `pytest`. **`251 / 251` tests passed** natively with zero regressions.
- **Documentation Parity**: `agents/skills/00-index.md` matches exactly 126 backend `.skill.md` files. `agents/templates/00-index.md` categorizes all 60+ template definitions. Markdown structure tree diagrams (`README.md`, `README_FULL.md`) correctly reflect the recent refactoring.
- **Codebase Cleanliness**: Swept the repository for `TODO`, `FIXME`, and `HACK`. No loose tech-debt markers exist in the source code; they correctly only exist inside rules or testing string assertions.
- **Architectural Purity**: Clean workspace with zero stranded, orphaned, or unused script files left behind.
- **Scripts Validation**: Validated that all 126 skills and 60+ templates exist exactly as advertised with zero broken internal links using `agents/scripts/comprehensive_checker.py` and `validate_skills.py`.
- **CLI Reference Fixed**: Replaced outdated `0.3.0` CLI references across the docs with the actual `0.7.0` version to perfectly reflect the release state.

---

## [0.7.1] — 2026-02-25

### Added — MVA Platform Control Layer
- **`gabbe/budget.py`**: `Budget` and `BudgetEnforcer` — token, cost, tool call, wall-time, and iteration limits per run; pricing loaded from `pricing_registry` table; `BudgetExceeded` exception.
- **`gabbe/hardstop.py`**: `HardStop` — absolute iteration/depth/timeout guards with `tick()`, `remaining_steps()`, and `should_wrap_up()`.
- **`gabbe/policy.py`**: `PolicyEngine` with YAML-driven `ToolAllowlistPolicy`, `RolePolicy`, `ContentSafetyPolicy`, `ParameterRangePolicy`; deny-all secure default when policy file is absent.
- **`gabbe/gateway.py`**: `ToolGateway` — single mediated execution point with rate limiting, circuit breaker, JSON Schema validation, and audit integration.
- **`gabbe/audit.py`**: `AuditTracer` — structured spans to SQLite `audit_spans` + JSONL + optional OTel; `snapshot_budget()`.
- **`gabbe/escalation.py`**: `EscalationHandler` — three modes (`cli`, `file`, `silent`); `EscalationPaused` exception for `file` mode; `[e]dit context` option in CLI mode.
- **`gabbe/replay.py`**: `CheckpointStore` + `ReplayRunner` — deterministic replay from `checkpoints` table; `diff()` to compare two runs.
- **`gabbe/context.py`**: `RunContext` context manager wiring all platform controls together; `from_checkpoint()` for replay.
- **`gabbe/forecast.py`**: `run_forecast()` — project remaining work cost/token estimates; writes to `forecast_snapshots`.
- **New CLI commands**: `gabbe runs`, `gabbe audit`, `gabbe replay`, `gabbe resume`.
- **Schema v3**: 7 new tables — `pricing_registry`, `runs`, `audit_spans`, `budget_snapshots`, `checkpoints`, `pending_escalations`, `forecast_snapshots`.
- **New env vars**: `GABBE_MAX_COST_USD`, `GABBE_MAX_TOKENS_PER_RUN`, `GABBE_MAX_TOOL_CALLS_PER_RUN`, `GABBE_MAX_ITERATIONS`, `GABBE_MAX_WALL_TIME`, `GABBE_MAX_RECURSION_DEPTH`, `GABBE_MAX_RETRIES_PER_TOOL`, `GABBE_POLICY_FILE`, `GABBE_ESCALATION_MODE`, `GABBE_OTEL_ENABLED`, `GABBE_SUBPROCESS_TIMEOUT`, `GABBE_MCP_TOKEN`, `GABBE_MCP_ALLOWED_COMMANDS`.
- MCP server: `GABBE_MCP_TOKEN` authentication and `GABBE_MCP_ALLOWED_COMMANDS` allowlist for `run_command`.
- 251-test suite covering all platform control modules (`test_budget`, `test_hardstop`, `test_gateway`, `test_policy`, `test_audit`, `test_replay`, `test_escalation`, `test_context`, `test_brain_integration`).
- `docs/PLATFORM_CONTROLS.md` and `docs/CLI_REFERENCE.md` documenting the full control layer.

### Fixed
- Reasoning token cost calculation for o1/o3-class models (`budget.py`).
- Audit span timestamps now reflect span start time, not end time (`audit.py`).
- Exception detection uses `isinstance()` instead of string matching (`context.py`).
- `EscalationPaused` correctly propagates without double-escalation (`brain.py`).
- Deny-all default when `project/policies.yml` is absent (`policy.py`).
- Forecast zero-tasks division-by-zero and DB connection leak (`forecast.py`).
- Checkpoint replay lookup uses per-node occurrence index (`replay.py`).
- Hash delimiter added in sync state hash (`sync.py`).
- LIMIT query parameterized in `gabbe runs` (`main.py`).

---

## [0.7.0] — 2026-02-19

### Added
- GABBE CLI 0.7.0 (Stable) with Zero-Dependency architecture.
- Full Antigravity / Gemini support.
- Comprehensive Troubleshooting Guide.
- AI-Native Engineering Scenarios guide.
- Self-Healing loop with 5-attempt limit and human escalation.
- Multi-agent swarm (Loki Mode) with 30+ personas.
- 4-layer memory architecture (Working, Episodic, Semantic, Procedural).
- Comprehensive checker scripts for kit integrity.
- GABBE CLI 0.7.0: `gabbe init`, `gabbe sync`, `gabbe status`, `gabbe verify`, `gabbe route`, `gabbe brain`
- Bidirectional `TASKS.md ↔ SQLite` sync with timestamp arbitration (`gabbe sync`)
- Brain Mode with Active Inference loop and Evolutionary Prompt Optimization (`gabbe brain`)
- Cost-Effective LLM Router (`gabbe route`) — LOCAL vs REMOTE decision based on complexity + PII detection
- Self-Healing Watchdog (`gabbe brain heal`) — checks DB connectivity and required project files
- Schema migration system (`schema_version` table) for forward-compatible DB upgrades
- `UNIQUE(title)` constraint on `tasks` table to prevent silent duplicate corruption
- Atomic file writes in `export_to_md` (temp-file + `os.replace`)
- Expanded PII detection patterns (email, phone, SSN, credit card, credential keywords)
- All configurable values exposed via environment variables:
  `GABBE_API_URL`, `GABBE_API_KEY`, `GABBE_API_MODEL`, `GABBE_LLM_TEMPERATURE`,
  `GABBE_LLM_TIMEOUT`, `GABBE_ROUTE_THRESHOLD`
- `[project.optional-dependencies] dev` in `pyproject.toml` for `pytest`
- `[tool.pytest.ini_options]` in `pyproject.toml`
- `scripts/tests/conftest.py` with shared `tmp_project` and `db_conn` fixtures
- Unit test files: `test_config.py`, `test_database.py`, `test_llm.py`, `test_route.py`,
  `test_sync.py`, `test_verify.py`
- CI pipeline now installs the package and runs `pytest scripts/tests/`

### Changed
- `gabbe/verify.py`: `parse_agents_config()` now only reads the `## Commands` section
  of `AGENTS.md`; commands outside that section are silently ignored
- `gabbe/verify.py`: `run_command()` uses `shell=False` with `shlex.split()` — eliminates
  shell injection risk
- `gabbe/llm.py`: raises `EnvironmentError` when `GABBE_API_KEY` is unset (was silently
  returning a mock string)
- `gabbe/llm.py`: default model updated from `gpt-4-turbo-preview` → `gpt-4o`
- `gabbe/status.py`: reads `current_phase` from `project_state` table (was hardcoded)
- `gabbe/brain.py`: `run_healer()` performs real checks (was a stub returning 100% Nominal)
- `gabbe/brain.py`, `gabbe/status.py`: DB connections closed with `try/finally`
- `gabbe/sync.py`: handles "both empty" edge case explicitly; multi-format timestamp
  parsing; atomic file export
- `gabbe/config.py`: removed `MAGENTA = '\033[95m'` duplicate of `HEADER`; added
  `LLM_TEMPERATURE`, `LLM_TIMEOUT`, `ROUTE_COMPLEXITY_THRESHOLD`, `PROGRESS_BAR_LEN`
- `gabbe/__init__.py`: removed eager imports to prevent side effects on import
- `gabbe/main.py`: all command dispatches wrapped in `try/except` for user-friendly errors

### Fixed
- Shell injection vulnerability in `verify.py`
- Silent mock LLM responses masking missing API key
- Unclosed SQLite connections in `brain.py` and `status.py`
- Non-atomic TASKS.md writes causing potential corruption on crash
- Duplicate `MAGENTA`/`HEADER` ANSI code in `Colors` class
- Dead code `if ... : pass` branch in `init.py`

---

## [0.1.0] — 2026-02-01

### Added
- Initial release of the GABBE Agentic Engineering Kit
- `init.py` Universal Skill Compiler (Cursor, VS Code, Claude Code, Gemini)
- Skill, Template, Guide, and Persona framework (`.agents/` directory)
- `AGENTS.md` + `CONSTITUTION.md` for agent governance
- Multi-platform skill distribution
- Initial documentation: `README.md`, `README_FULL.md`, `QUICK_GUIDE.md`
- Research whitepapers in `docs/`
