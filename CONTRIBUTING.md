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
`--help`, config schema, DB schema, emitter output, CVE delta):

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

4. Regenerate the Claude Code plugins (`plugins/` and `.claude-plugin/marketplace.json`)
   and commit the result; `scripts/tests/test_claude_plugin.py` fails in CI when the
   tree is stale. Do the same after editing a skill, or a template or guide a skill names:

```bash
python3 scripts/build_claude_plugin.py
```

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
- [ ] Lint and types pass (CI `lint` job): `ruff check gabbe scripts agents/scripts`, `black --check gabbe scripts agents/scripts`, `mypy gabbe`
- [ ] Verifiers pass: `python3 agents/scripts/verify_use_cases.py` and `verify_triggers_and_mcps.py`
- [ ] New behaviour is covered by tests
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] `README.md` counts/tables updated if skills/templates/guides were added
- [ ] `python3 scripts/build_claude_plugin.py` re-run if skills/templates/guides changed (plugin tree in sync)
- [ ] No `shell=True` introduced
- [ ] No hardcoded credentials or API keys

---

## Releasing

A release is cut from `main` by pushing a version tag; the workflows publish.

1. In `CHANGELOG.md`, move the `## [Unreleased]` entries under a new
   `## [X.Y.Z] — YYYY-MM-DD` heading.
2. Set the version to `X.Y.Z` in `pyproject.toml`, `package.json` and
   `gabbe/__init__.py`, in the "Versioned X.Y.Z" sentence of `llms.txt`, and in
   `site/index.html`. `scripts/build_claude_plugin.py` stops with an error when
   `pyproject.toml` and `package.json` disagree.
3. The kit stamp `*GABBE Kit version: …*` at the end of `agents/AGENTS.md`,
   `agents/CONSTITUTION.md` and `agents/templates/coordination/AGENTS_TEMPLATE.md`
   is what `agents/scripts/state_export.sh` and `scripts/registry_export.py` report.
   These files are in the emitter golden vault: after changing them, recapture it
   (`python scripts/gates/capture_emitter_baseline.py scripts/tests/golden/baseline_v0.8.0`)
   and review the diff.
4. Run `python3 scripts/build_claude_plugin.py` (it writes the version into
   `.claude-plugin/marketplace.json`), then `bash scripts/verify_all.sh` on the final tree.
5. Merge to `main`, then tag the merge commit and push the tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

   The tag starts three workflows (see [TESTING.md](TESTING.md#ci)):
   `publish-npm.yml` publishes `gabbe-kit` with npm trusted publishing (it fails when the
   tag is not `v` + the `package.json` version; tags with a `-` are not published);
   `release.yml` builds the GitHub release assets and, when the `PYPI_API_TOKEN` secret is
   set, publishes to PyPI and verifies the published package on three OSes;
   `publish-github-packages.yml` mirrors the npm package to GitHub Packages.
6. If only the npm publish failed, run `publish-npm.yml` by hand (Actions → Publish npm →
   Run workflow, optional `dist_tag`): it publishes without a new tag and without
   re-running the PyPI publish.

---

## Reporting Issues

Open an issue at https://github.com/andreibesleaga/GABBE/issues with:
- GABBE version (`gabbe --version` or check `pyproject.toml`)
- Python version
- OS / AI tool being used
- Steps to reproduce
