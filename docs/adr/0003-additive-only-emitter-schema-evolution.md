# 3. Emitted client formats evolve additive-only

- Status: Accepted
- Date: 2026-06-10

## Context

The files GABBE writes into a consumer project (`.cursor/rules/*.mdc`,
`.claude/skills/<name>/SKILL.md`, `.github/skills/`, `.gemini/settings.json`,
root `AGENTS.md`) are the system's real public API. Downstream projects and other
agents depend on their exact shape. Uncontrolled changes silently break consumers.

## Decision

The emitted formats are governed by an **additive-only** compatibility policy,
documented in [docs/SCHEMA.md](../SCHEMA.md) and enforced by:

- `scripts/tests/test_golden_emitters.py` — per-platform sha256 manifest; a
  removed or byte-changed artifact fails, additions pass.
- `scripts/gates/run_gates.sh` gate 4 — the same check in the CI gate runner.

Allowed: new emitted files, new optional frontmatter keys (e.g.
`gabbe-schema-version`), new target clients. Not allowed without a major version
bump: removing an emitted file, removing/retyping a key, or changing the bytes of
an existing artifact a consumer could depend on. Intentional baseline updates are
reviewed against this rule and recorded.

## Consequences

- Every emitter change is provable-safe or explicitly a breaking (major) change.
- The 0.9 standard-alignment changes (Claude `SKILL.md` directories, etc.) were
  shipped as a reviewed, recorded baseline update because the prior Claude output
  was non-functional (undiscoverable), not a contract consumers could rely on.
