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
pytest gabbe/tests/ scripts/tests/ -v
python3 agents/scripts/verify_use_cases.py
python3 agents/scripts/verify_triggers_and_mcps.py
```

For a reproducible install, use the pinned, hashed lockfile:

```bash
pip install -r requirements-lock.txt
```

### Refreshing the lockfile

`requirements-lock.txt` is generated from `pyproject.toml` with
[pip-tools](https://github.com/jazzband/pip-tools). Regenerate it whenever
dependencies change:

```bash
pip install pip-tools
pip-compile --extra dev --generate-hashes --output-file requirements-lock.txt pyproject.toml
```

### Backward-compatibility gates

Code changes must keep the six verification gates green (API surface, CLI
`--help`, config schema, emitter output, benchmarks, CVE delta):

```bash
./scripts/gates/run_gates.sh
```

The emitted client formats (`.cursor/rules/*.mdc`, `.claude/skills/`,
`.github/skills/`, `.gemini/settings.json`) are a public contract documented in
[docs/SCHEMA.md](docs/SCHEMA.md) and locked by
`scripts/tests/test_golden_emitters.py`. They evolve additive-only.

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

## Security & Guardrails
- Keep changes focused and secure
- Run tests after every change to prevent regressions
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

- All changes must pass `pytest gabbe/tests/ scripts/tests/ -v`.
- If you add a CLI feature, add or extend unit tests in `gabbe/tests/`.
- If you change `scripts/init.py`, add or extend tests in `scripts/tests/`.
- Run `python3 agents/scripts/verify_use_cases.py` and `verify_triggers_and_mcps.py` after skill/guide/template changes.
- Follow the existing code style (PEP 8, no type annotations required but welcomed).
- Add new configurable constants to `config.py` rather than hardcoding them.

### Key architectural rules
- `config.py` is the single source of truth for all configurable values.
- Never use `shell=True` in `subprocess.run` — use `shlex.split()`.
- Always close DB connections with `try/finally` or a context manager.
- Use `_atomic_write()` from `sync.py` for any file writes that must be crash-safe.

---

## Pull Request Checklist

- [ ] Tests pass: `pytest gabbe/tests/ scripts/tests/ -v`
- [ ] Verifiers pass: `python3 agents/scripts/verify_use_cases.py` and `verify_triggers_and_mcps.py`
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
