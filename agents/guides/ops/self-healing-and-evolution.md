# Self-Healing and Self-Evolution

> Read this when a check fails and you want to fix it yourself, or when you scan for new skills, tools or
> models. The rules that bind every session are in `AGENTS.md` §8. This guide holds the detail.
> The step-by-step procedures are in `core/self-heal.skill` and `core/update-scan.skill`.

## Self-healing

You may fix a failure yourself, up to 5 attempts, as long as the fix stays in the allowed list.

Allowed without asking:

- Type errors and lint errors.
- Test assertions that must change because the spec changed.
- Deprecated API calls, found in the library's official documentation.
- Patch and minor dependency bumps.
- Import paths and formatting.

Needs a human decision:

- Architecture or library changes.
- Breaking API changes (any consumer affected).
- Changes to authentication, permissions or encryption, and anything that removes or weakens a security control.
- Major dependency bumps.
- Any change to `CONSTITUTION.md` or to CI/CD pipelines.

Each attempt changes something. Repeating the same fix is not an attempt. Before the first attempt, read
`agents/memory/CONTINUITY.md` for the same failure.

### After 5 failed attempts

1. Stop all autonomous action.
2. Write an escalation report: the error, all 5 attempts and what each did, what you found in research,
   and the decision you recommend.
3. Append it to `agents/memory/AUDIT_LOG.md`.
4. Wait for the human.

Format for the report:

```text
ESCALATION REQUIRED
Issue:          what fails, with the exact error
Attempts:       1..5, one line each, with the result
Options:        A and B, with pros and cons
Recommendation: one option and why
Awaiting:       the decision you need
```

## Self-evolution

The kit may be extended with better skills, tools, MCP servers or models. This goes through
`core/update-scan.skill`, inside these bounds.

Allowed, subject to `GABBE_AUTONOMY` and the budget:

- Adopt a cheaper or better tool or model when the change is reversible and passes validation.
- Import an external skill after it has been validated (`agents/scripts/validate_skills.py`, path checks).
- Refine a prompt or persona from runs that succeeded. Never learn from failed runs.

Always needs the human, even under `auto`:

- Anything expensive, irreversible or on the top model tier.
- Runnable code that comes from outside the repository.
- A change to a protected file: build files, infrastructure as code, CI configuration, dependency manifests,
  `CONSTITUTION.md`. The self-healing list above is the only exception.

Every adoption and every rejection is one row in `AUDIT_LOG.md`. Prefer a trial first and keep a way back:
version what you change so it can be reverted.

## Autonomy posture

`GABBE_AUTONOMY` is `ask`, `auto` or `hybrid` (default `hybrid`). Order of precedence: the environment
variable, then `autonomy` in `project/gabbe.config.json`, then `hybrid`.

| Posture | Behaviour |
|---|---|
| `ask` | Ask before each choice that has an option. |
| `hybrid` | Choose the best option within budget. Ask for expensive, top-tier or irreversible choices. |
| `auto` | Same as hybrid for cheap and reversible work. Still ask for the always-ask cases in `AGENTS.md` §9. |

## Per-project policy file

`project/gabbe.config.json` is optional. It sets the autonomy posture, budgets, model tiers, enabled MCP
servers, skill registries and protected files. Copy `gabbe.config.example.json` from the kit's
`docs/` folder (https://github.com/andreibesleaga/GABBE/tree/main/docs) and edit it. The agent applies it
through `coordination/self-optimize.skill`; the optional `gabbe` CLI reads it through `gabbe/config.py`.
The schema is in `docs/SCHEMA.md`, section "Project policy config".
