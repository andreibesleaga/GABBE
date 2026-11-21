# Support, stability and maintenance

What you can rely on, which versions are supported, and what happens after 1.2.0.

## What is stable

These do not change in a way that breaks an installed project. They are checked in CI on every change
(`scripts/gates/run_gates.sh`, see [TESTING.md](../TESTING.md)).

| Surface | Promise |
|---|---|
| Kit files (`agents/`) | Plain Markdown in open formats: `AGENTS.md` and Agent Skills (`<name>/SKILL.md`). No file depends on one vendor. |
| Installed projects | An update never removes or overwrites a file you wrote without a backup ([INSTALL.md](INSTALL.md)). |
| Install record (`.gabbe/manifest.json`) | Schema version 1; new kinds of entry are added, existing ones keep their meaning. |
| `gabbe` command line | Options shown by `--help` are a contract: additions only. |
| Configuration and database | Additions only (new keys, new columns). |
| Python package | Public names are additions only. |

## What is experimental

- The Python command-line tool as a whole (`pyproject.toml` marks it alpha): budgets, policy, audit trail,
  the tool server.
- Brain mode. Its description says what it is and is not.
- Hooks, where a release ships them: they are optional and off by default.

## Supported versions

| Part | Supported |
|---|---|
| Kit and installers | the latest release |
| Python (for the `gabbe` command line) | 3.9 to 3.13, tested in CI on each |
| Node (for `npx gabbe-kit`) | 16 or later |
| Operating systems | Linux, macOS and Windows: the install is tested in CI on all three |

Security fixes go into the latest release. See [SECURITY.md](../SECURITY.md) for how to report a problem.

## After 1.2.0: maintenance

1.2.0 is planned as the last release that adds features. After it the project is maintained:

- fixes for security problems and for defects;
- dependency updates within the same major version;
- corrections to documents and to the kit's text when a tool or a standard changes.

A new feature is not planned. If one is needed, it starts as an issue.

## Where to ask

- A defect or a question: <https://github.com/andreibesleaga/GABBE/issues>
- A security problem: follow [SECURITY.md](../SECURITY.md); do not open a public issue.
- How to cite the project: [`CITATION.cff`](../CITATION.cff).
