---
name: dependency-upgrade
description: Use to upgrade one dependency in an existing project, safely. Inventory, read the changelog for breaking changes, change one package, keep the lockfile in step, run tests before and after, and know how to roll back. Policy and cadence live in dependency-lifecycle.skill.
triggers: [upgrade dependency, bump package, update library, breaking change upgrade, major version, lockfile, outdated packages, upgrade one dependency]
tags: [ops, dependencies, brownfield]
core: true
context_cost: medium
---
# Dependency Upgrade Skill

## Goal
Move one dependency to a newer version with proof that nothing broke, and a way back. `dependency-lifecycle.skill` sets the policy (cadence, SBOM, EOL); this skill is the procedure for a single upgrade. `dependency-security.skill` owns scanning.

## Steps
1. **Inventory.** List outdated and vulnerable packages with the project's tool (`npm outdated`, `npm audit`, `pip list --outdated`, `pip-audit`, `composer outdated`, `go list -u -m all`, `cargo outdated`, whichever is installed). Save the output to `agents/memory/episodic/deps-<date>.txt`.
2. **Pick one package.** Order: security fixes first, then same-major updates, then majors. A major needs the human's yes (record it in `AUDIT_LOG.md`); the default is same-major only.
3. **Record the baseline.** Check the working tree is clean for the manifest and lockfile (`git status --short`). Run the full tests and write the pass count. If tests are red or missing, stop: run `characterization-tests.skill` first.
4. **Read what changed.** Open the changelog or release notes between the current and target version (the package registry page or the repository's CHANGELOG). List breaking changes, removed APIs, changed defaults, new minimum runtime. Search the project for every use of the affected APIs (`grep -rn`). Check transitive changes: compare the lockfile diff after step 4.
5. **Change one package.** Use the package manager's own command (for example `npm install pkg@x.y.z`, `pip install pkg==x.y.z` then update the lock, `composer update vendor/pkg`) so the lockfile changes with the manifest. Never edit the lockfile by hand.
6. **Review the lockfile diff.** Only the target and its needed transitive packages changed. A new unrelated package, a changed registry URL or a missing integrity hash: stop and ask.
7. **Fix the callers.** Apply the changelog's migration steps to each use found in step 4, as small edits. Run build, lint, types.
8. **Test after.** Full test suite and the dependency scan. Compare to the baseline: pass count not lower; no new advisories.
9. **Write the note.** From version, to version, why, breaking changes handled, tests before and after, rollback. Append it to `project/DEPENDENCY_UPGRADES.md`. Edit `CHANGELOG.md` only if the human asked for that.
10. **Next package.** Repeat from step 2, one package per change.

## Constraints
- One dependency per change, with its manifest and lockfile in the same change.
- Same-major first. A major bump, a package replacement or a new package needs the human's yes.
- Tests green before and after; never skip or edit a test to get green.
- The upgrade is not mixed with refactoring or a feature.

## Output Format
`project/DEPENDENCY_UPGRADES.md`, one entry per upgrade: version change, breaking-change list with what was done, test counts before and after, scan result, rollback command.

## Limits and safety
- Rollback is: restore the manifest and lockfile from version control (`git checkout -- <files>` run by the human, or the agent only if asked) and reinstall; write the exact commands in the note.
- Install scripts of new versions run code on this machine; for an unfamiliar package or a new maintainer, read the install script or ask before installing.
- Do not publish, tag or deploy the upgraded build unless the human asks in that request.
