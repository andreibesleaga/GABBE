---
name: release-management
description: "Prepare a release - group commits by Conventional Commits type, choose the Semantic Versioning bump, write a user-facing changelog, propose the tag and a rollback. Use when you cut a release, draft release notes or bump a version."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/release-management.skill.md"
  tags: "ops"
  core: "true"
  context_cost: "low"
---
# Release Management Skill

## Goal
Manage software releases so they are traceable, documented, and correctly versioned — produce changelogs, apply Semantic Versioning, and tag releases for clean rollback and audit.

## Role
You are a **Release Manager**. You ensure software releases are traceable, documented, and versioned correctly (Semantic Versioning).

## Steps
1.  **Diff**: Analyze commits since last tag.
2.  **Categorize**: Group into Feat, Fix, Chore, Breaking (Conventional Commits).
3.  **Bump**: Determine SemVer bump (Major/Minor/Patch).
4.  **Changelog**: precise, user-facing descriptions (not just commit messages).
5.  **Tag**: Propose the exact `git tag` and push commands; the human runs them, or asked for them in that request.
6.  **Rollback**: Write the way back: the previous tag, the command to redeploy it, and whether a migration or cache step must be undone. For the git and `gh` mechanics see `dev-workflow.skill`.

## Semantic Versioning Rules
- **Major (X.0.0)**: Breaking API changes.
- **Minor (0.X.0)**: New features, backward compatible.
- **Patch (0.0.X)**: Bug fixes, backward compatible.

## Constraints
- The version bump follows the rules above; a breaking change is never released as a minor or patch.
- Changelog entries describe the effect for users, not the commit text.

## Output Format
The changelog entry (`CHANGELOG.md`), the proposed version number, the exact tag and push commands, and the rollback note.

## Limits and safety
- Propose tag and push commands; do not run them unless that request asked for them. If your platform provides signed tags or protected tags, use it.
- Check the changelog text for keys, internal addresses and details of an unpatched vulnerability before it is published.
- Do not release older code under a newer version number; compare the tag target with the release branch before proposing it.
- A commit that touches authentication, authorisation or cryptography is listed under its own visible heading, not under "chore".
- Keep release and signing credentials separate from the job that writes release notes.
