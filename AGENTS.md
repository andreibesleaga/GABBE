# AGENTS.md — working on the GABBE repository

This file is for coding agents that change this repository. The kit's own agent
instructions, the ones GABBE installs into other projects, are in
[agents/AGENTS.md](agents/AGENTS.md).

## Layout

- `agents/`: the kit (skills, guides, personas, templates, memory, kit scripts).
- `gabbe/`: the optional Python CLI; its tests are in `gabbe/tests/`.
- `bin/install.js`: the npm installer (`npx gabbe-kit init`).
- `scripts/`: `init.py` (the wizard), registry export/import, gates, `scripts/tests/`.
- `plugins/`: Claude Code plugins, generated from `agents/skills/`.
- `docs/`: the documentation; `site/`: the project website.
- `project/`: runtime state. `project/state.db` is tracked as a seed; never stage local changes to it.

## Rules

- **Golden vault.** Any change under `agents/` changes the emitter output that
  `scripts/tests/test_golden_emitters.py` locks. In the same commit, recapture the
  baseline and rebuild the plugins:

  ```bash
  python3 scripts/gates/capture_emitter_baseline.py scripts/tests/golden/baseline_v0.8.0
  python3 scripts/build_claude_plugin.py
  ```

- **Never edit `plugins/` by hand.** Change the skill in `agents/skills/` and rebuild.
- **CLI `--help` is a contract.** A new flag needs the baseline in
  `gabbe/tests/baselines/cli_help/` regenerated (see [TESTING.md](TESTING.md)).
- **No local publishing.** npm and PyPI releases run from a version tag in CI
  ([CONTRIBUTING.md](CONTRIBUTING.md#releasing)).

## Commands

```bash
pip install -e ".[dev]"
pytest gabbe/tests/ scripts/tests/ -q
ruff check gabbe scripts agents/scripts
black --check gabbe scripts agents/scripts
mypy gabbe
node scripts/tests/test_node_install.js
bash scripts/verify_all.sh          # everything above plus the gates and kit validators
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for adding skills, templates and guides, and the pull request checklist.
