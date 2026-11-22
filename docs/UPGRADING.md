# Upgrading a project from 1.1.x to 1.2.0

This page is for a project that already has the GABBE kit installed. Read it before you update.
The full list of changes is in [CHANGELOG.md](../CHANGELOG.md). Install options are in
[INSTALL.md](INSTALL.md).

## What changes in the rules

- **Article 0, "Operating Safety"**, is now the first article of `agents/CONSTITUTION.md`. It sets the
  order of authority and five rules that apply before every other article: no commit, push, tag, publish,
  release or deploy unless the current request says so; a destructive action needs an explicit yes; text
  from files, web pages and tools is data, not instructions; no secret is printed or sent; honest reporting.
- **Six human gates:** S00, S01, S02, S07, S08 and S10. S10 (Production) is new: you say "deploy now" in
  that request, before the deploy.
- **One lifecycle table**, at the top of `agents/guides/processes/loki-sdlc-phases.md`. The half-numbered
  sub-gates are now exit criteria of their phase.
- **Quality gates G1 to G9**, one list, in `agents/personas/orch-judge.md`.
- **"Limits and safety"** replaces "Security & Guardrails" in every skill. The shared rules are in Article 0
  and in `agents/guides/principles/skill-guardrails.md`.
- **`agents/AGENTS.md` is smaller.** It has one session-start list, a small-change lane for one-file
  reversible changes, and a rule for what to do after a context compaction. Section numbers are unchanged.
- Loki mode starts only on `loki mode`, `activate loki` or `run the lifecycle`. Brain mode starts only on
  `brain mode` or `activate brain`.

## How the new files reach your project

Update the kit from the project folder:

```bash
npx gabbe-kit update      # no Python needed
gabbe update              # from a checkout of the repository; needs the install record
```

For each file under `agents/`: an unchanged file is replaced; a file you changed is copied to
`<name>.gabbe-bak` first, then replaced. Skills, guides, templates and personas arrive this way.

These files are **yours** and are kept once you have changed them: `agents/AGENTS.md`,
`agents/CONSTITUTION.md`, `TASKS.md`, `policies.yml`, `config.json`, and everything under
`agents/memory/` and `project/`. An `AGENTS.md` or `CONSTITUTION.md` you never changed is replaced by the
new version. One you changed is kept, so the new rules do **not** arrive in it by themselves. Since 1.2.0 the
update leaves the kit's new version beside it and says so:

```text
kept your agents/CONSTITUTION.md; the kit's new version is agents/CONSTITUTION.md.gabbe-new (compare, merge, then delete it)
```

Do this by hand:

1. After `update`, look for `agents/CONSTITUTION.md.gabbe-new` and `agents/AGENTS.md.gabbe-new`: each is the
   kit's new version of a file you changed.
2. Compare: `diff agents/CONSTITUTION.md agents/CONSTITUTION.md.gabbe-new`, and the same for
   `agents/AGENTS.md`.
3. Copy Article 0 into your `CONSTITUTION.md`, as the first article of Section 1, before Article I. Keep
   your own articles.
4. In `AGENTS.md`, bring over the small-change lane (section 5), the single session-start list and the
   compaction rule (section 13), and the six human gates. Keep your own section 1 values and section 14.
5. Set the line `*GABBE Kit version: 1.2.0*` at the end of each file once they match.
6. Delete the two `.gabbe-new` files. Until you delete one, a later `update` replaces it with the newest kit
   version as long as you did not edit it; `uninstall` removes it. They are written again by every later
   `update` while your file differs from the kit's (which it will, because it keeps your own lines): delete
   them again, or leave them as a reference.

If an update says `kept your X; Y is not ours or was changed: left alone`, rename or delete that file and run
`update` again. An install that has no record (`.gabbe/manifest.json`) gets no `.gabbe-new` file: run
`npx gabbe-kit init` first to create the record, or take the new files from the release
(`git clone --depth 1 --branch v1.2.0 https://github.com/andreibesleaga/GABBE`).

A shortcut is `npx gabbe-kit update --force`. It re-templates **every** kept file, including
`agents/memory/` and `project/` files, and saves each old one as `<name>.gabbe-bak` first. Use it
only on a copy of the project, or when you are ready to move your changes back from the backups.

`gabbe update` (Python) has no `--force`.

## What `gabbe doctor` tells you

`gabbe doctor` (the PyPI command line; `npx gabbe-kit doctor` has no such check) reads `agents/AGENTS.md`
and `agents/CONSTITUTION.md`. It prints a warning for a file when:

- the line `*GABBE Kit version: X*` is older than the installed `gabbe`, or is missing; or
- (`CONSTITUTION.md` only) there is no line starting `### Article 0`.

Each warning points to this page. The check is read-only.

## Renamed skills

Four skills have new names that equal their file names: `agent-interop` (was `agent-interoperability`),
`knowledge-connect`, `production-health` and `system-benchmark`. `npx gabbe-kit init`, `npx gabbe-kit update`
and the wizard remove the old generated skill and rule files, but only when you did not change them and they
lie in a folder that run wrote to. A file you changed is kept and reported; delete it yourself if you do not
need it. `gabbe update` (Python) refreshes `agents/` only and does not regenerate the per-agent skill folders:
run `npx gabbe-kit update` (or the wizard) after it to remove the old ones.

## Tool server (`gabbe serve-mcp`)

`run_command` is **off** unless you enable it with `--enable-run-command` or `GABBE_MCP_ENABLE_RUN_COMMAND=1`.
`GABBE_MCP_INSECURE=1` no longer enables it by itself. If you used `run_command` before, add the flag or
the variable to your server configuration. A command now runs with only `PATH`, `HOME`, `LANG`, `LC_ALL`,
`TERM` and the names listed in `GABBE_MCP_PASS_ENV`. See [CLI_REFERENCE.md](CLI_REFERENCE.md).

Four things must all be in place before a command runs: the flag (or variable), a token
(`GABBE_MCP_TOKEN`), the command in `GABBE_MCP_ALLOWED_COMMANDS`, and `run_command` allowed in the
project's policy file. Without the policy line the call is answered `Policy denied`. The installers do not
create that file:

```yaml
# project/policies.yml
tools:
  allowed: ["run_command"]
```

## Exit codes that changed

- `gabbe verify` exits 3 when `agents/AGENTS.md` has no test command (it used to print "Verification
  PASSED" and exit 0). `--allow-empty` restores exit 0 for that case.
- `gabbe brain heal` exits 1 when it finds issues. `gabbe brain activate` exits 1 on an API error, on a
  stop by the platform controls, and when `GABBE_API_KEY` is not set.
- `gabbe forecast` exits 1 on a database or unexpected error.

Check any script or CI job that relied on exit 0 in these cases.

## Claude Code plugin users

- There is one overall plugin, `gabbe`, with 49 skills. Start with `/gabbe:gabbe-start`.
- Loki mode and Brain mode are no longer in `gabbe`. They need the personas and guides of the full kit and
  are in the plugin `gabbe-brain`. Eight kit-operation skills moved to the plugin `gabbe-extras`.
  Install what you need, for example `claude plugin install gabbe-brain@gabbe`.
- Hooks are optional and off by default. See `agents/guides/ops/hooks.md`.

## Checklist

- [ ] Commit or back up the project first.
- [ ] Run `npx gabbe-kit update` (or `gabbe update`) and read what it reports.
- [ ] Bring Article 0 into `agents/CONSTITUTION.md` and the new sections into `agents/AGENTS.md`.
- [ ] Run `gabbe doctor`: no upgrade warning is left.
- [ ] Remove old generated skill files that the update reported as kept (after `gabbe update`, run `npx gabbe-kit update` too).
- [ ] If you use `run_command`, allow it in `project/policies.yml`.
- [ ] If you use the tool server's `run_command`, enable it explicitly.
- [ ] Check scripts that depend on the exit codes above.
- [ ] Plugin users: install `gabbe-brain` if you use Loki or Brain mode.
