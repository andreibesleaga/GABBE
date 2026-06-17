---
name: configuration-management
description: Establish a unified software configuration management discipline covering branching, baselines, change control, reproducible builds, versioning, SBOM, and config audit.
triggers: [define a software configuration management plan, choose branching strategy trunk vs gitflow, set baseline and release versioning, establish change control process, ensure reproducible builds, generate sbom and artifact identification, run a configuration audit]
tags: [ops, scm, versioning, release]
core: false
context_cost: medium
---
# Configuration Management

## Goal
Establish a single, coherent software configuration management (SCM) discipline so that every released
artifact is identifiable, reproducible, traceable to its sources, and changed only through a controlled
process. This skill operationalizes the SWEBOK v4 "Software Configuration Management" knowledge area:
selecting a branching strategy, identifying baselines and releases, controlling change, producing
reproducible builds, identifying artifacts and versions, generating a software bill of materials (SBOM), and
auditing configuration. It unifies practices that live in adjacent skills — `git-workflow.skill` for the
mechanics of branching and commits, `release-management.skill` for cutting and shipping releases, and
`dependency-lifecycle.skill` for managing third-party components — and binds them into one SCM plan.

## Steps
1. **Identify configuration items.**
   - Enumerate what is under configuration control: source, build scripts, infrastructure-as-code,
     environment definitions, dependency manifests and lockfiles, documentation, and the release artifacts
     themselves. Anything that affects the built product is a configuration item.
2. **Choose a branching strategy.**
   - Select **trunk-based development** (short-lived branches, frequent integration to main, feature flags
     for incomplete work) for teams optimizing for continuous delivery and small batch sizes, or **git-flow**
     (long-lived develop/release/hotfix branches) for products with explicit, infrequent, versioned releases
     or regulatory release gates. State the trade-off: trunk-based minimizes merge debt and speeds
     integration but demands strong CI and flags; git-flow gives heavyweight release structure at the cost of
     merge complexity. Defer mechanics to `git-workflow.skill`.
3. **Define baselines and versioning.**
   - A **baseline** is a formally reviewed, named snapshot that changes only through change control. Identify
     which milestones become baselines (e.g., each release candidate). Adopt **Semantic Versioning**
     (MAJOR.MINOR.PATCH): MAJOR for breaking changes, MINOR for backward-compatible features, PATCH for
     backward-compatible fixes; pre-release and build metadata as needed. Tie release cutting to
     `release-management.skill`.
4. **Set up change control.**
   - Define how a change to a baselined item is proposed, reviewed, approved, and recorded: who can authorize
     what, the review gate, and the link from change request to commit to release. Track configuration
     status so anyone can answer "what is in this build, and why."
5. **Make builds reproducible.**
   - Pin dependencies via lockfiles, pin toolchain and base-image versions, eliminate nondeterminism (fixed
     timestamps, sorted ordering, no network during build where possible), and build from a clean, recorded
     environment so the same sources yield a bit-for-bit or functionally identical artifact. Coordinate
     dependency pinning and updates with `dependency-lifecycle.skill`.
6. **Identify artifacts and emit an SBOM.**
   - Give every artifact an immutable, unique identifier (version + content hash) and record the exact
     sources and dependencies that produced it. Generate an **SBOM** (e.g., SPDX or CycloneDX) listing every
     component and version so vulnerabilities and licenses can be traced to shipped releases.
7. **Audit the configuration.**
   - Run periodic configuration audits: a **functional** audit (does the built artifact meet its
     requirements?) and a **physical** audit (does the artifact's recorded contents — versions, SBOM, hashes
     — match what is actually shipped?). Flag drift between intended and actual configuration.

## Constraints
- Every released artifact MUST carry a unique, immutable identifier (version plus content hash) traceable to
  its exact sources and dependencies; the agent does not bless an unidentifiable build.
- Baselines change only through the recorded change-control process; the agent refuses to treat an
  ad-hoc/untracked modification of a baselined item as part of a release.
- The branching strategy is chosen deliberately with its trade-off stated, not by default; the agent does
  not silently assume trunk-based or git-flow.
- Reproducibility is required: dependencies and toolchain are pinned and the build environment recorded; a
  build that cannot be reproduced from the record is flagged as a risk.
- An SBOM accompanies releases; the agent does not certify a release as supply-chain-clean without one.
- Mechanics that belong to `git-workflow.skill`, `release-management.skill`, and `dependency-lifecycle.skill`
  are referenced, not re-derived; this skill owns the SCM plan that coordinates them.

## Output Format
Produce an **SCM plan** containing:
- A configuration-item inventory.
- The chosen **branching model** with its trade-off justification (and pointer to `git-workflow.skill`).
- **Baseline and versioning** rules: which milestones are baselined and the SemVer policy (with pointer to
  `release-management.skill`).
- The **change-control** procedure: proposal, authorization, review gate, and request-to-commit-to-release
  traceability.
- **Reproducibility** measures: pinning, toolchain control, and recorded build environment (with pointer to
  `dependency-lifecycle.skill`).
- **Artifact identification and SBOM** approach.
- A **configuration-audit** checklist (functional + physical) and how drift is reported.

## Security & Guardrails

### 1. Skill Security
- **Risk**: Unidentifiable or untracked release — an artifact ships without a traceable version/hash, making
  rollback and forensics impossible; mitigation: the agent requires an immutable identifier and
  source-to-artifact traceability before treating a build as releasable.
- **Risk**: Change-control bypass — a baselined item is edited outside the process to "save time";
  mitigation: the agent records every change against its authorization and flags any baseline modification
  lacking an approved change request.

### 2. System Integration Security
- **Risk**: Supply-chain tampering — a dependency or build step is compromised between source and artifact;
  mitigation: the agent pins dependencies with lockfiles, generates and verifies an SBOM, and prefers
  hermetic, recorded build environments so injected components are detectable.
- **Risk**: Build/CI credential or environment leakage — secrets or signing keys exposed through the build
  pipeline; mitigation: the agent keeps secrets out of configuration items and version control and confines
  signing to controlled, access-restricted infrastructure.

### 3. LLM & Agent Guardrails
- **Risk**: Overstated reproducibility — the model claims a build is reproducible without verifying pinning
  or determinism; mitigation: the agent only marks a build reproducible when pinning and a recorded
  environment are present, and otherwise states it as a known gap.
- **Risk**: Stale or hallucinated version/SBOM data — the model invents component versions or a clean SBOM;
  mitigation: the agent derives identifiers and SBOM entries from actual manifests and lockfiles and refuses
  to fabricate supply-chain attestations.
