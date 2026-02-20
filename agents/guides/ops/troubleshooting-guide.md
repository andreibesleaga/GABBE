# GABBE Kit Troubleshooting Guide

This guide provides solutions to common issues encountered when initializing, configuring, or running the GABBE Agentic Engineering Kit.

## 1. Setup & Installation Issues

### `init.py` fails with "ModuleNotFoundError"
**Symptoms:** Running `python3 scripts/init.py` throws an error about missing modules.
**Cause:** Python dependencies might be missing or you're using an older Python version.
**Solution:**
1. Ensure you have Python 3.8+ installed (`python3 --version`).
2. Run standard installation procedures: `pip install -r requirements.txt` (if applicable) or use the interactive `python3 scripts/init.py` prompt.

### "File exists" error during setup
**Symptoms:** `init.py` stops with `mkdir: cannot create directory ‘agents’: File exists`.
**Cause:** You previously installed the kit in this directory.
**Solution:** Run `python3 scripts/init.py` and input `y` when asked to "Overwrite/Update it?".

### Symlinks not working (Windows)
**Symptoms:** `agents/skills` are not visible to the IDE or AI Agent.
**Cause:** Windows requires Administrator privileges to create symlinks by default.
**Solution:**
1. Open PowerShell **as Administrator**.
2. Run `.\agents\setup-context.ps1`.
3. Alternatively, enable Developer Mode in Windows Settings (which allows standard users to create symlinks).

## 2. Agent Configuration Issues

### Agent ignores AGENTS.md
**Symptoms:** The agent generates code in the wrong framework or ignores layer boundaries.
**Cause:** The symlink from `.cursorrules` or `.claude/CLAUDE.md` to `AGENTS.md` is broken, or the file lacks rules.
**Solution:**
1. Re-run `./agents/setup-context.sh`.
2. Check `AGENTS.md` to ensure `[PLACEHOLDER]` fields are filled correctly.

### Skills not triggering
**Symptoms:** Typing `/tdd-cycle` or asking the agent to use a skill results in generic web search behavior.
**Cause:** The skill directory is not mounted or the AI tool is misconfigured.
**Solution:**
- **Cursor:** Ensure `.mdc` files exist in `.cursor/rules/`.
- **Claude:** Ensure `.claude/skills` is symlinked to `agents/skills`.
- **Gemini:** Check `.gemini/settings.json` for the `skills` path.

## 3. Loki orchestration issues

### Self-Heal loop stuck in infinite recursion
**Symptoms:** Agent continuously tries to fix the same error without escalating.
**Cause:** Bug in `self-heal.skill.md` constraint evaluation.
**Solution:** Tell the agent: "Stop. Escalate issue. Read self-heal limit constraints." You can also manually add the failure to `agents/memory/CONTINUITY.md` so the agent skips it next time.

### Tasks getting lost or corrupted
**Symptoms:** `project/TASKS.md` is out of sync or tasks disappear.
**Cause:** Concurrent edits by human and agent, or an interrupted session.
**Solution:**
1. Run `gabbe sync` (if using GABBE CLI 2.0).
2. Manually review `agents/memory/PROJECT_STATE.md` and edit `project/TASKS.md` to match reality.

## 4. GABBE CLI 2.0 Issues

### `gabbe route` or `gabbe brain` fails with "API Key Missing"
**Symptoms:** Commands that require remote LLM models throw an authentication error.
**Cause:** `GABBE_API_KEY` environment variable is not set.
**Solution:** Export your OpenAI-compatible API key:
`export GABBE_API_KEY='your-key-here'`

### SQLite Database locked
**Symptoms:** Running `gabbe sync` throws a `database is locked` error.
**Cause:** Multiple terminal windows or an active agent are trying to access `project/state.db` simultaneously.
**Solution:** Ensure no background processes are running `gabbe` commands. If necessary, delete the `project/state.db-journal` file.
