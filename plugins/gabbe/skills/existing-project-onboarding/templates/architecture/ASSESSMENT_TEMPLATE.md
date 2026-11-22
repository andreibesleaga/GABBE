# Assessment: [Project Name]

**Date:** [YYYY-MM-DD]
**Author:** [agent or person]
**Commit assessed:** [git SHA]
**Status:** Draft | Approved by [human] on [date]

<!-- Produced by existing-project-onboarding.skill during stage B0
     (guides/processes/brownfield-lifecycle.md). Facts first, each with the command or file
     that shows it. Technical debt items go to templates/ops/TECH_DEBT_TEMPLATE.md, legacy
     mainframe detail to templates/architecture/LEGACY_AUDIT_TEMPLATE.md. -->

---

## 1. Starting Point

| Item | Value |
|---|---|
| Branch | [ ] |
| Uncommitted changes at start | [none / list] |
| Last commit date | [ ] |
| Map | `CODEBASE_MAP.md` |

## 2. Build, Tests, CI

| Item | State | Evidence |
|---|---|---|
| Install | [works / fails / unknown] | [command, output file] |
| Build | [ ] | [ ] |
| Tests | [pass N / fail N / skipped N / none exist] | [`agents/memory/episodic/baseline-<date>.txt`] |
| Line coverage | [x% / no tool] | [command] |
| CI | [green / red / none] | [file or run link] |
| Run time of the suite | [ ] | [ ] |

## 3. Documentation and People

| Item | State |
|---|---|
| README and setup notes | [accurate / outdated / none] |
| Architecture notes, ADRs | [ ] |
| Known owners or maintainers | [roles, or "unknown"] |

## 4. Quick Checks

| Check | Result | Evidence |
|---|---|---|
| Secrets in the tree (file and line only, never the value) | [ ] | [ ] |
| Dependencies with known advisories | [count or "no audit command"] | [ ] |
| Unsupported runtime or framework versions | [ ] | [ ] |

## 5. Risks and Debt

| # | Area | Risk or debt | Impact | Effort | Evidence |
|---|---|---|---|---|---|
| R1 | [ ] | [ ] | [H/M/L] | [S/M/L] | [ ] |

## 6. Unknowns for the Human

| # | Question | Recommended answer |
|---|---|---|
| Q1 | [ ] | [ ] |

## 7. Proposal (the human decides)

- Next stage: [B1 Characterise / B2 Make it safe / other]
- First areas to characterise and why: [ ]
- Out of scope: [ ]
- Needs the human's yes before it starts: [dependency changes, seams in source, deletions]
- Question: Approve this proposal? [yes / no / changes: ____ ]  Date: [ ]  Recorded in `AUDIT_LOG.md`: [row]
