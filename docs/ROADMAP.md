# GABBE roadmap

What is planned after 1.1.1, in the order it should be built. Nothing here ships until it is written, tested and released; the [CHANGELOG](../CHANGELOG.md) records what did.

## 1. Agent hooks

### The decision

GABBE stays a context kit that works with any agent, so hooks are **not required** to use it. It will ship one small, **off-by-default** hook set for the agents that support hooks, because four of its rules are broken in practice when they rest on the agent's reading alone, and a hook can enforce each of those four at the tool-call boundary.

### What enforces each rule today, and what a hook could add

Today almost every gate and rule in the kit is enforced only by the agent reading Markdown. The Python CLI's controls (budget, hard stop, policy, tool gateway, escalation) wrap `gabbe brain activate` and `gabbe serve-mcp`, so they never see a coding agent's file edits, git commands or phase changes.

| Rule | Enforced today by | A hook can add |
|---|---|---|
| The agent never commits, pushes, tags, publishes or deploys unless told to in that request | prose (AGENTS.md, CONSTITUTION Article XIII) | a block on the git and publish commands before they run |
| Protected files (the constitution, AGENTS.md, golden baselines, lockfiles, CI) are not edited | prose; `protected_files` in `project/gabbe.config.json` is read by no code | a block on edits to the configured globs |
| Checks run on the final tree before work is reported as done | prose (Step 7 of the operating spine) | a refusal to end the turn when files changed after the last green run |
| The session is recorded in memory before it ends | prose (AGENTS.md section 13) | a refusal to end the turn after edits when no memory file was updated; the resume pointer injected at session start |
| S00–S13 gates, human approvals, the orch-judge veto | prose; `gabbe status` reads a phase that no command writes | nothing reliable: a hook sees tool calls, not whether a gate was earned |
| Ask before deciding, additive edits to authored prose, research before claims, numbers re-run before quoting | prose | nothing: these are judgements, not tool calls |
| The project's tests, lint and security scan pass | the project's CI and `gabbe verify` (human-run) | the Stop check above runs the same commands |

### The planned hook set

One zero-dependency Node script, `agents/hooks/gabbe-hooks.js`, with templates the installer merges into a project when asked with `npx gabbe-kit init --hooks`. Without that flag nothing is written. Node is used because the installer already needs it and hooks must also run on Windows.

| Event | Matcher | Command | Purpose | When it fails or is absent |
|---|---|---|---|---|
| `PreToolUse` | `Bash` | `node agents/hooks/gabbe-hooks.js guard-bash` | denies git writes (`commit`, `push`, `tag`, `merge`, `rebase`, `reset --hard`, `clean -f`, `--no-verify`, `config core.hooksPath`), `gh pr merge`/`release`/`repo create`, package publishes and deploy commands, including `git -C <dir>` and `cd x && git …` forms; denies shell writes that name a protected path | fails closed on unreadable input; a timeout is treated by the host as non-blocking |
| `PreToolUse` | `Edit\|Write\|MultiEdit\|NotebookEdit` | `… guard-edit` | denies edits to `protected_files` (or the kit defaults) and to the hook files and their state | fails closed |
| `PostToolUse` | `Edit\|Write\|MultiEdit\|NotebookEdit\|Bash` | `… ledger` | records that this session changed files, so read-only sessions never meet the Stop check | never blocks |
| `Stop` | every stop | `… stop` | after edits, refuses to end the turn when the tree differs from the tree the last green `gate` run saw, or when no memory file was updated since the first edit; tells the agent what to run | fails open; at most three refusals per session, then a warning, so a session whose tests cannot pass is never trapped |
| `SessionStart` | `startup\|resume\|clear` | `… session-start` | prints the first lines of the resume pointer and the date of the last green gate into the session | cannot block |
| (a command) | — | `… gate` | the only writer of the green stamp: runs `hooks.gate_command`, or the test, lint and security-scan commands of the AGENTS.md Commands section, and records the tree hash on success | exit 1 and no stamp when a command fails |

Escape hatches live where the agent's shell cannot reach them: environment variables of the host process (`GABBE_HOOKS_OFF=1`, `GABBE_ALLOW_GIT_WRITE=1`, `GABBE_UNLOCK=<globs>`), and a one-shot written authorization of one exact command line, consumed when used.

A second, script-free layer ships in the same Claude Code template: `permissions.deny` entries for `Bash(git commit *)`, `Bash(git push *)` and edits of the constitution, which Claude Code enforces without running any hook.

**Claude Code** (`.claude/settings.json`, merged, never overwritten):

```json
{
  "permissions": { "deny": ["Bash(git commit *)", "Bash(git push *)", "Bash(git tag *)", "Edit(agents/CONSTITUTION.md)"] },
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "hooks": [{ "type": "command", "command": "node agents/hooks/gabbe-hooks.js guard-bash", "timeout": 10 }] },
      { "matcher": "Edit|Write|MultiEdit|NotebookEdit", "hooks": [{ "type": "command", "command": "node agents/hooks/gabbe-hooks.js guard-edit", "timeout": 10 }] }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash", "hooks": [{ "type": "command", "command": "node agents/hooks/gabbe-hooks.js ledger", "timeout": 10 }] }
    ],
    "Stop": [{ "hooks": [{ "type": "command", "command": "node agents/hooks/gabbe-hooks.js stop", "timeout": 30 }] }],
    "SessionStart": [{ "matcher": "startup|resume|clear", "hooks": [{ "type": "command", "command": "node agents/hooks/gabbe-hooks.js session-start", "timeout": 10 }] }]
  }
}
```

**Other agents.** Check each against its current documentation when the work starts, because these surfaces change often.

| Agent | What it gets |
|---|---|
| Cursor | `.cursor/hooks.json`: `beforeShellExecution` runs the shell guard; `afterFileEdit` records edits and reports a protected-file edit after the fact. Cursor has no pre-edit block and no blocking stop, so the last two rules are warnings there. |
| Gemini CLI, GitHub Copilot (CLI and coding agent), OpenCode, Windsurf | each has a hook or plugin surface; the installer prints a note naming it, and wiring follows once verified |
| Codex, Aider, Cline, Roo Code, Kilo Code, Zed, Continue, Devin, Antigravity | prose, plus the git-side guard below; for Aider the installer also sets `auto-commits: false` |
| every agent | `.githooks/pre-commit` and `pre-push` (POSIX sh), copied but not activated: a commit or push passes only from a shell that carries `GABBE_HUMAN_COMMIT=1`, staged protected files are refused, and the staged tree must match the green stamp when one exists. Activating them (`git config core.hooksPath .githooks`) is the project owner's choice. |

The forge stays the final layer for every agent: a required CI check on the default branch blocks an unchecked change whichever agent produced it.

### Honest limits

- A hook sees tool calls, not intent. Gates earned, judgements, claims and additive editing stay prose.
- A determined agent can write a script and run it. The set closes the mistakes agents actually make, such as misreading an authorization, skipping a re-run of the checks or forgetting the memory update, and leaves every evasion visible in the transcript and the hook log.
- The Stop check also fires after a clarifying question that follows edits; the three-refusal cap keeps that from trapping a session.

### Files and changes

- Add `agents/hooks/gabbe-hooks.js`, `agents/hooks/claude-settings.template.json`, `agents/hooks/cursor-hooks.template.json`, `agents/hooks/githooks/pre-commit`, `agents/hooks/githooks/pre-push` and `agents/hooks/README.md` (one table: rule, hook, enforced, still prose).
- `bin/install.js`: a `--hooks` flag that merges the templates (union of `permissions.deny`; a hook group added per event only when its command is not already there).
- `scripts/init.py`: a wizard question, default No, so the emitter vault of Gate 4 is unchanged.
- `project/gabbe.config.json` schema: `hooks.gate_command`, `hooks.memory_files`, `hooks.resume_lines` (documented in `docs/SCHEMA.md`, additive only, Gate 3).
- Correct the two lines that promise enforcement that does not exist today: AGENTS.md section 10 ("Hooks: Check .claude/settings.json…") and the git-workflow skill ("The workflow script MUST intercept…"). Both become true only with `--hooks`; say so. Editing AGENTS.md needs a golden-baseline recapture for Gate 4.

### Tests

- `scripts/tests/test_hooks.js` (zero dependencies, throwaway git repositories): read-only git allowed; every denied write and publish form denied; protected and hook-state writes denied while reads pass; the one-shot authorization consumed; the environment escape hatches; fail-closed on empty and malformed input; the Stop sequence (silent without edits, blocks, `gate`, blocks on memory, passes, blocks again after a later edit, stops blocking after three); `gate` refuses a failing command and placeholders; `session-start` resets the ledger; a kit installed under a subfolder.
- Three installer tests for `--hooks` in `scripts/tests/test_node_install.js`, run on all three operating systems in CI.

### Considered and not chosen

- **No hooks at all.** One enforcement story for every agent and nothing to maintain against changing hook formats, but the four rules above would stay unenforced inside the session and be caught only afterwards by CI, if at all. It also leaves the two lines that promise enforcement untrue.
- **A full hook layer.** Every S00–S13 gate and every policy enforced through hooks and the Python gateway, with a phase ledger. It cannot enforce what matters most in a gate, which is whether the work earned it, and it would bind the kit to the hook formats of many agents. The cost in size and portability is out of proportion to what it adds over the planned set.

## 2. `gabbe verify` exit code

`gabbe verify` prints "Verification FAILED" and still exits 0 (`gabbe/main.py` ignores the result of `run_verification()`; only `--chaos` exits 1). Anyone who runs it in CI, as the full guide suggests, gets a green job on a failed check. Fix: exit 1 when the verification fails, with a test. This is independent of the hooks and comes first.
