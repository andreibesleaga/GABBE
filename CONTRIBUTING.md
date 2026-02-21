# Contributing to GABBE

Thank you for your interest in contributing to the GABBE Agentic Engineering Kit!

---

## Development Setup

```bash
git clone https://github.com/andreibesleaga/GABBE
cd GABBE
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest scripts/tests/ -v
```

---

## Adding a Custom Skill

1. Create a new `.skill.md` file in `agents/skills/<category>/`:

```markdown
---
name: my-skill
description: What this skill does in one sentence
tags: [python, testing]
---
# My Skill

## Goal
Concise statement of what the agent should accomplish.

## Steps
1. Step one
2. Step two
3. Verify with tests

## Constraints
- Keep changes focused
- Run tests after every change
```

2. Re-run `init.py` to distribute the skill to all configured AI tools:

```bash
python3 scripts/init.py
```

3. Add a row to the skills table in `README_FULL.md` and an entry in `README.md`.

---

## Adding a Custom Template

1. Create a `.md` file in `agents/templates/<category>/`.
2. Use existing templates as reference (e.g., `agents/templates/core/TASKS_TEMPLATE.md`).
3. Update the templates table in `README.md` and `README_FULL.md`.

---

## Adding a Custom Guide

1. Create a `.md` file in `agents/guides/`.
2. Update the guides table in `README.md` (Guides by Stack section) and `README_FULL.md`.

---

## Code Changes to `gabbe/`

- All changes must pass `pytest scripts/tests/ -v`.
- If you add a feature, add or extend unit tests in `scripts/tests/`.
- Follow the existing code style (PEP 8, no type annotations required but welcomed).
- Add new configurable constants to `config.py` rather than hardcoding them.

### Key architectural rules
- `config.py` is the single source of truth for all configurable values.
- Never use `shell=True` in `subprocess.run` — use `shlex.split()`.
- Always close DB connections with `try/finally` or a context manager.
- Use `_atomic_write()` from `sync.py` for any file writes that must be crash-safe.

---

## Pull Request Checklist

- [ ] Tests pass: `pytest scripts/tests/ -v`
- [ ] New behaviour is covered by tests
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] `README.md` counts/tables updated if skills/templates/guides were added
- [ ] No `shell=True` introduced
- [ ] No hardcoded credentials or API keys

---

## Reporting Issues

Open an issue at https://github.com/andreibesleaga/GABBE/issues with:
- GABBE version (`gabbe --version` or check `pyproject.toml`)
- Python version
- OS / AI tool being used
- Steps to reproduce
