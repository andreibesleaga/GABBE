# Codebase Map: [Project Name]

**Date:** [YYYY-MM-DD]
**Author:** [agent or person]
**Commit mapped:** [git SHA from `git rev-parse --short HEAD`]
**Status:** Draft | Verified (5 of 5 spot checks)

<!-- Produced by code-archaeology.skill during stage B0 (guides/processes/brownfield-lifecycle.md).
     Every row has a location (path:line) or the command that produced it. A guess is marked "guess".
     Keep under 300 lines; link to detail files. For a dependency and parallelism worksheet use
     templates/core/DEPENDENCY_GRAPH_TEMPLATE.md; for causes and structures use
     templates/core/SYSTEM_ANALYSIS_TEMPLATE.md. -->

---

## 1. Size and Stack

| Item | Value | Found by |
|---|---|---|
| Languages and lines | [e.g. Python 12k, JS 3k] | [command] |
| Frameworks and runtime versions | [ ] | [manifest file] |
| Excluded (vendored, generated) | [paths] | [reason] |
| Commands (install, build, test, lint, run) | [ ] | [file where found / guessed] |

## 2. Entry Points

| Kind (route, CLI, job, consumer, main) | Name | Location (path:line) |
|---|---|---|
| [ ] | [ ] | [ ] |

## 3. Modules

| Module (directory or package) | Purpose (one sentence) | Main files | Imported by | Tests present? |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [yes / no / partial] |

## 4. Main Data Flows

### Flow 1: [name]
`[entry point path:line]` -> `[step path:line]` -> `[storage or external call]`

## 5. External Systems

| System (database, queue, API, file system) | Used by | Configured in | Credentials source (name only) |
|---|---|---|---|
| [ ] | [ ] | [ ] | [env var name, never the value] |

## 6. Hot Spots (history x size)

| File | Changes in 12 months | Lines or complexity | People touching it | Note |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [count] | [ ] |

History limits (shallow clone, squashed commits): [say so or "none"]

## 7. Dead-Code Candidates

| Symbol or file | Why it looks unused | Could be used by (reflection, plug-in, external caller) |
|---|---|---|
| [ ] | [ ] | [ ] |

## 8. Unknowns

| # | Question | Where (path:line) | Who might know | Status |
|---|---|---|---|---|
| U1 | [ ] | [ ] | [role, or "owner unknown"] | Open |

## 9. Verification Record

| Entry checked (section and row) | Result |
|---|---|
| [ ] | [matches / fixed] |
