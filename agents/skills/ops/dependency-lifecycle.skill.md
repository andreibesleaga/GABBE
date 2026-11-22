---
name: dependency-lifecycle
description: Set the policy for keeping dependencies current - patch, minor and major cadence, SBOM refresh, CVE triage, EOL tracking, automated update PRs, lockfiles and pinning. Use when you define or review how a project handles updates and advisories.
triggers: [define our dependency upgrade cadence, set up a dependency lifecycle policy, triage these cve advisories, refresh the sbom for the next release, track end-of-life dependencies, enforce lockfile and pinning hygiene]
tags: [ops, dependencies, supply-chain, maintenance]
core: false
context_cost: medium
---
# Dependency Lifecycle Skill

## Goal
Produce a dependency lifecycle policy that keeps a project's third-party dependencies current, supported, and free of known vulnerabilities without churn-driven breakage. It sets the cadence for absorbing patch, minor, and major updates, keeps the SBOM and CVE posture fresh, tracks end-of-life (EOL) before it bites, and enforces lockfile and pinning hygiene. This complements `dependency-security.skill` (which owns SBOM generation and SCA scanning mechanics) by defining the ongoing *operational rhythm* around it.

## Steps
1. **Inventory and classify.** Enumerate direct and transitive dependencies and classify each by blast radius (runtime-critical, build-only, dev-only) and update risk. Distinguish **patch** (bug/security, low risk — adopt fast), **minor** (backward-compatible features, moderate risk — batched), and **major** (breaking, high risk — planned with migration work).
2. **Set the cadence.** Define the rhythm per class: patch/security as soon as CI passes; minor on a regular batched window (e.g., weekly/biweekly); major as scheduled, owned migration tasks. State who reviews and merges each class.
3. **Refresh the SBOM.** Tie SBOM regeneration to the release pipeline so every shipped artifact has a current bill of materials. Diff the SBOM between releases to surface newly introduced or removed components. Defer generation mechanics to `dependency-security.skill`.
4. **Triage CVEs.** When an advisory lands, assess: is the vulnerable package actually used, is the vulnerable code path reachable, and what is the severity/exploitability in context. Prioritize remediation (upgrade, patch, or compensating control) by real risk, not raw CVSS alone. Record decisions in the audit trail.
5. **Track EOL.** Maintain a list of dependencies (and runtimes/base images) approaching end-of-support, with the EOL date and the planned migration target. EOL software stops receiving security fixes — schedule the move before the date, not after.
6. **Automate dependency PRs.** Configure automated update PRs (grouped by class to reduce noise), with CI gates that must pass before merge. Auto-merge is permissible only for patch/dev updates with green CI and human review reserved for minor/major.
7. **Enforce lockfile hygiene.** Require committed, deterministic lockfiles; every dependency change updates the lockfile in the same PR. Reject PRs that change manifests without the corresponding lockfile update. Verify resolved versions match the lockfile in CI.
8. **Pin the supply chain.** Pin dependencies (and CI actions/base images) to exact versions or integrity hashes/digests rather than floating ranges or mutable tags, so builds are reproducible and a hijacked upstream tag cannot silently change resolved code.
9. **Assign ownership and write the policy.** Name owners for each class and for EOL tracking, then assemble the Output Format below. For the procedure of one single upgrade, see `dependency-upgrade.skill`.

## Constraints
- Patch/security updates are adopted promptly; majors are always planned migration work, never auto-merged.
- The SBOM is regenerated for every release artifact, not occasionally.
- CVE triage prioritizes by reachability and exploitability in context, not CVSS score alone, and records the decision.
- Lockfiles are committed, deterministic, and updated atomically with manifest changes.
- Dependencies, CI actions, and base images are pinned to exact versions or digests; mutable tags are not acceptable for reproducible builds.
- This skill defines policy and proposes PRs; it does not auto-merge minor/major changes or override CI gates without human approval.

## Output Format
A dependency lifecycle policy in Markdown:
- **Inventory & classification** — dependency classes (runtime/build/dev) and update-risk tiers.
- **Cadence** — table of patch/minor/major rhythm, reviewer, merge rule.
- **SBOM** — regeneration trigger and diff process (cross-link `dependency-security.skill`).
- **CVE triage** — assessment criteria and prioritization rule.
- **EOL tracking** — table of dependency, EOL date, migration target, owner.
- **Automation** — PR grouping, CI gates, auto-merge boundaries.
- **Lockfile & pinning** — hygiene rules and pinning policy (versions/digests).
- **Owners** — named owners per class and for EOL.

## Limits and safety
- Accept a CVE as not exploitable only with a written reachability reason in `AUDIT_LOG.md`; the agent does not lower an advisory's severity.
- Major upgrades are separate tasks reviewed by the human; never loosen or delete tests to make an upgrade pass.
- Check new transitive packages in an update PR against the approved registry before accepting it.
- If your platform provides branch protection and required checks, restrict auto-merge to patch and dev updates with green CI and a scan.
- Pin CI actions and base images to exact versions or digests.
