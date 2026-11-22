---
name: code-archaeology
description: Use to recover the structure and intent of code you did not write. Maps entry points, modules, dependencies and data flow, finds hot spots from version history, lists dead-code candidates and unknowns.
triggers: [code archaeology, map the codebase, understand the code, entry points, hot spots, churn, dead code, module map, architecture recovery]
tags: [architecture, brownfield, analysis]
core: true
context_cost: medium
---
# Code Archaeology Skill

## Goal
Produce a map that a new developer can read in ten minutes and check against the code. Fills `CODEBASE_MAP.md` (`templates/architecture/CODEBASE_MAP_TEMPLATE.md`). Read-only: no source is changed.

## Steps
1. **Size the tree.** Run `git ls-files | wc -l` and list lines per language (`git ls-files | xargs wc -l | sort -n | tail -20`; use `cloc` or `tokei` only if already installed). Exclude vendored and generated directories and name them in the map.
2. **Find entry points.** Search for `main`, server start, route tables, CLI parsers, job schedulers, message consumers, and the manifest `scripts` / `bin` / `entry_points`. List each with file and line.
3. **Draw the module map.** One row per top-level directory or package: purpose in one sentence, main files, who imports it. Get imports with the language's own tool where one exists (for example `go list -deps`, `pipdeptree`, `npm ls`, `madge` if installed) or `grep -rn "import\|require"`. For the project dependency table and cycles, point to `templates/core/DEPENDENCY_GRAPH_TEMPLATE.md` and `arch-debt.skill`; do not copy them.
4. **Trace the data flow.** Pick the two or three main user or system journeys. For each, list the call path from entry point to storage or external call, with file and line. Mark every external system (database, queue, HTTP API, file system) found.
5. **Find hot spots from history.** Run:
   `git log --since="12 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20` (change count per file).
   Combine with size or complexity (`radon cc -s`, `npx complexity-report`, or line count if no tool). A file in both lists is a hot spot. Add `git shortlog -sn -- <path>` per hot spot to see how many people touch it. History is shallow or squashed? Say so.
6. **List dead-code candidates.** Use the language's own tools if present (`vulture`, `knip`, `ts-prune`, `deadcode`) or search for symbols with no callers. Mark each "candidate": reflection, plug-ins and external callers can hide uses. Never delete here.
7. **Find the tests.** Where they live, how they run, which modules have none (`git ls-files | grep -i test`). Do not judge quality yet; `characterization-tests.skill` does that.
8. **Write the unknowns list.** Every thing you could not explain: file, question, who might know (use `git log --format=%an -- <path> | sort | uniq -c | sort -rn | head -3`). Unknown owner is a valid entry.
9. **Check the map.** Pick five entries at random and re-verify each against the code. Record "5 of 5 verified" or fix the entry.

## Constraints
- Read-only. Output files are `CODEBASE_MAP.md` and notes under `agents/memory/semantic/`.
- Each fact has a location (path:line) or the command that produced it.
- Do not describe intent as fact. Write "appears to" and record the evidence, or put it in the unknowns list.
- Keep the map under 300 lines; link to detail files instead of pasting.

## Output Format
A filled `CODEBASE_MAP.md`: size, entry points, module table, data flows, external systems, hot spots, dead-code candidates, test locations, unknowns, verification record.

## Limits and safety
- Do not run code that writes to a database or calls a live service just to see what happens; read it instead.
- Authorship from `git log` is a pointer for questions, not a judgement; do not put personal names in the public output if the repository is public.
- Never delete a dead-code candidate in this skill; removal is a later, separate, human-approved step with tests.
