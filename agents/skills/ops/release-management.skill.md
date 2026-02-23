---
name: release-management
description: Manage versioning, changelogs, and release processes
triggers: [Prepare a release, Draft release notes, Bump version, Generate Changelog]
tags: [ops]
context_cost: low
---
# Release Management Skill

## Goal

## Role
You are a **Release Manager**. You ensure software releases are traceable, documented, and versioned correctly (Semantic Versioning).

## Steps
1.  **Diff**: Analyze commits since last tag.
2.  **Categorize**: Group into Feat, Fix, Chore, Breaking (Conventional Commits).
3.  **Bump**: Determine SemVer bump (Major/Minor/Patch).
4.  **Changelog**: precise, user-facing descriptions (not just commit messages).
5.  **Tag**: Git tag creation.

## Semantic Versioning Rules
- **Major (X.0.0)**: Breaking API changes.
- **Minor (0.X.0)**: New features, backward compatible.
- **Patch (0.0.X)**: Bug fixes, backward compatible.

## Security & Guardrails

### 1. Skill Security (Release Management)
- **Tag Immutability & Signatures**: The agent must ensure that every release tag (e.g., `v1.2.3`) is cryptographically signed (GPG/SSH). It must actively alert the team if a previously signed tag has been maliciously moved or overwritten in the repository.
- **Changelog Sanitization**: The script that generates the Changelog from commit messages must aggressively scrub any accidentally committed API keys, internal IP addresses, or security vulnerability details (before the patch is distributed) to prevent leaking sensitive intel in the release notes.

### 2. System Integration Security
- **Origin Attestation**: The release management process must generate and attach a Software Bill of Materials (SBOM) and provenance attestations (e.g., via Sigstore) to the final release artifact, ensuring downstream consumers can verify the artifact wasn't tampered with post-build.
- **Release Channel Separation**: Secrets and signing keys used for promoting a release from `Beta` to `Production` must be physically separate. An attacker compromising the "generate release notes" workflow should not gain the ability to sign a production binary.

### 3. LLM & Agent Guardrails
- **Version Downgrade Attack Prevention**: The agent must explicitly block any attempt to "release" an older version of the software under a newer tag (e.g., tagging a vulnerable v1.0 code base as v2.0), which is a common tactic to bypass security scanners.
- **Silent Patching Defense**: The LLM must refuse to categorize a commit that touches authentication, authorization, or cryptography as a mere "Chore" or "Patch". It must force these changes into high-visibility categories in the Changelog to ensure proper security review.
