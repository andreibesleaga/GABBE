# GABBE Emitted-Format Schema

> **Audience:** maintainers & downstream consumers. **Scope:** the contract of every emitted client format and its evolution policy.

**Audience:** maintainers and downstream consumers who depend on the files
GABBE writes into a project. **Scope:** the public contract of every artifact
`scripts/init.py` (and `agents/scripts/compile_skills.py`) emit per AI client.

These emitted files — not the Python API — are GABBE's real public surface. A
project that ran `init.py` consumes these bytes directly, so they evolve under a
strict **additive-only** policy (see *Compatibility policy* below).

> This document describes the emitted format. Items marked **[0.9+]** are the
> agent-skills standard alignment shipped in 0.9 (Claude `<name>/SKILL.md`
> directories, Cursor agent-requested rules, `GEMINI.md`, root `AGENTS.md`,
> and the `gabbe-schema-version` key).

## Source format: `agents/skills/**/*.skill.md`

Every skill is a Markdown file with YAML frontmatter:

```yaml
---
name: tdd-cycle                 # string, required. Human label; slugified for output paths.
description: Red-green-refactor… # string, required. Used for client-side discovery.
triggers: [tdd, test-first]     # list[str], optional. Activation hints.
tags: [python, testing]         # list[str], optional. Feeds the init.py tech-map.
context_cost: medium            # enum(low|medium|high), optional.
---
<markdown body — the skill instructions>
```

`name` and `description` are required and validated by
`agents/scripts/validate_skills.py`. Additional keys are tolerated by all
consumers. **[0.9+]** the slug derived from `name` is sanitized to
`[a-z0-9-]+` (path separators, `..`, and control characters are rejected).

## Emitted per-client formats

### Cursor — `.cursor/rules/<slug>.mdc`

One rule file per skill. Frontmatter:

```yaml
---
description: <skill description>   # string
globs:                            # see note
alwaysApply: false                # boolean
---
<skill body>
```

- Rule type is **Agent-Requested**: `description` present, `alwaysApply: false`.
- **0.8.x** emitted `globs: *`, which makes the rule auto-attach to every file.
  **[0.9+]** `globs` is omitted so Cursor selects the rule intelligently by
  description (per docs.cursor.com/context/rules).
- `.cursorrules` (legacy, repo root) is also linked to `agents/AGENTS.md`.

### Claude Code — `.claude/skills/<slug>/SKILL.md` **[0.9+]**

- **0.8.x** symlinked `.claude/skills` → `agents/skills` (a tree of
  `<category>/<name>.skill.md` files). Claude Code discovers skills only as
  `<name>/SKILL.md` **directories**, so 0.8.x skills did not load.
- **[0.9+]** GABBE emits a proper `.claude/skills/<slug>/SKILL.md` directory per
  skill (the agentskills.io open standard, shared with Copilot). `.claude/CLAUDE.md`
  remains linked to `agents/AGENTS.md`.

### GitHub Copilot / VS Code — `.github/skills/<slug>/SKILL.md`

- `<slug>/SKILL.md` (the skill body with `name` + `description` frontmatter) —
  conforms to the GitHub agent-skills standard.
- `<slug>/config.json` (non-standard GABBE metadata; ignored by Copilot):

  ```json
  { "name": "<slug>", "description": "<desc>", "version": "1.0.0",
    "slashCommands": [ { "name": "<slug>", "description": "<desc>" } ] }
  ```

- `.github/copilot-instructions.md` is linked to `agents/AGENTS.md`.

### Gemini CLI — `.gemini/settings.json`

```json
{
  "agent_instructions_file": "<rel path to agents/AGENTS.md>",
  "skills_directory": "<rel path to agents/skills>",
  "notes": "Managed by init.py"
}
```

- `agent_instructions_file`/`skills_directory` are GABBE metadata keys (not part
  of the official Gemini settings schema; harmless). **[0.9+]** a `GEMINI.md`
  context file pointing at `agents/AGENTS.md` is also emitted, which Gemini CLI
  reads natively.

### Codex — `.codex/AGENTS.md`

Symlink to `agents/AGENTS.md`. **[0.9+]** a root `AGENTS.md` is also emitted (the
agents.md open standard, read by Codex, Cursor, Gemini CLI, and Copilot coding
agent).

### Other clients

`.windsurfrules`, `.clinerules`, `.devinrules` (→ `agents/AGENTS.md`),
`.windsurf/skills`, `.cline/skills`, `.devin/skills` (→ `agents/skills`), and
`.aider.conf.yml` (`read:` list) are linked/written best-effort.

## Schema versioning — `gabbe-schema-version` **[0.9+]**

Every emitted frontmatter block carries `gabbe-schema-version: 1` (and
`.gemini/settings.json` carries `"gabbe-schema-version": 1`). Consumers that
ignore the key are unaffected; the key lets future tooling detect the emitted
schema generation.

## Compatibility policy

The emitted contract evolves **additive-only**:

- **Allowed:** new emitted files, new optional frontmatter keys, new clients.
- **Not allowed without a major version bump:** removing an emitted file,
  removing/retyping an existing key, or changing the bytes of an existing
  artifact in a way a consumer could depend on.

This is enforced by `scripts/tests/test_golden_emitters.py` (per-platform
sha256 manifest, additive-only diff) and the gate runner
`scripts/gates/run_gates.sh` (gate 4). The 0.9 changes marked **[0.9+]** above
are additive: new directories/files alongside the existing ones, reviewed
against the golden baseline.
