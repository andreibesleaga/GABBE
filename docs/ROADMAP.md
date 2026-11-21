# GABBE roadmap

What is planned after 1.1.4, in the order it should be built. Nothing here ships until it is written, tested and released; the [CHANGELOG](../CHANGELOG.md) records what did.

## 1. Agent hooks

### What 1.2.0 ships, and what it does not

Shipped in 1.2.0, all off by default (guide: [`agents/guides/ops/hooks.md`](../agents/guides/ops/hooks.md), files in `agents/hooks/`):

| Part | What it does |
|---|---|
| `agents/hooks/git/pre-commit`, `pre-push`, `install.sh` | every agent: refuses a commit that adds a secret-store file or a credential-like line, a push to `main`, `master` or a configured branch, and a force push; one-time override set by the human |
| `agents/hooks/claude-code/` (Node, standard library only) | Claude Code: asks the human before a git commit, push or tag, a package publish or a deploy command; asks before an edit of a protected path; prints `RESUME_POINTER.md` at session start and after compaction |
| `agents/hooks/cursor/` | Cursor: asks the human before the same shell commands (`beforeShellExecution`) |
| `agents/hooks/merge-hooks.js` | merges a fragment into the user's hooks file without replacing anything, and removes exactly those entries again |
| `--hooks` of `npx gabbe-kit init` and of the wizard (`python scripts/init.py --hooks`) | installs the parts above for the agents you chose; off unless you pass it; `gabbe uninstall` reverses it. No wizard question is added |

Not in 1.2.0:

- The Stop check (green run and memory update before the turn ends), the green stamp, the ledger and the `hooks.*` keys of `project/gabbe.config.json`. They are not built.
- GitHub Copilot: its page does not say that a command hook receives the payload on stdin, so the hook is not shipped.
- Codex: `permissionDecision: "ask"` is documented as not supported yet, so a hook could only deny, not ask. Not shipped.
- Gemini CLI (being replaced by Antigravity CLI), OpenCode, Windsurf, Devin: not verified; Devin reads the Claude Code settings file, which was not tested.
- Edits through the shell (`sed -i`, `echo > .env`) and edits by `NotebookEdit` are not seen by the edit guard.

## 2. `gabbe verify` exit code

`gabbe verify` prints "Verification FAILED" and still exits 0 (`gabbe/main.py` ignores the result of `run_verification()`; only `--chaos` exits 1). Anyone who runs it in CI, as the full guide suggests, gets a green job on a failed check. Fix: exit 1 when the verification fails, with a test. This is independent of the hooks and comes first.

Done in 1.1.2: `gabbe verify` now exits 1 when verification fails (see the [CHANGELOG](../CHANGELOG.md)).
