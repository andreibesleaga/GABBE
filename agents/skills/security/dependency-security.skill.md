---
name: dependency-security
description: Managing Supply Chain Security, SBOM generation, and vulnerability patching (SCA).
triggers: [dependency security]
tags: [security]
role: ops-security, ops-devops
---
# dependency-security Skill

## Goal
This skill secures the software supply chain.

## Steps
## 1. Software Composition Analysis (SCA)
> "You are what you import."

- **Audit**: Run `npm audit` / `pip-audit` / `cargo audit` in CI.
- **Block**: Fail the build on `CRITICAL` or `HIGH` vulnerabilities.
- **Lock**: Always verify lockfiles (`package-lock.json`) match `package.json`.

## 2. SBOM (Software Bill of Materials)
- Generate a list of all ingredients in your software.
- Tools: `syft`, `cyclonedx-cli`.
- Why? Rapid response when the next Log4Shell happens.

## 3. Dependency Pinning
- **Pin Exact Versions**: Avoid `^1.2.3` in critical apps. Use `1.2.3` to prevent "works on my machine" drift.
- **Private Registry**: For enterprise, proxy public registries to prevent "Left-Pad" incidents.

## 4. Typosquatting Defense
- **Scope**: Use `@myorg/package` scopes.
- **Verify**: Check download counts and maintainer reputation before adding new deps.

## Security & Guardrails

### 1. Skill Security (Dependency Security)
- **Scanner Sandbox Isolation**: Software Composition Analysis (SCA) tools (`npm audit`, `syft`) actively download and parse untrusted third-party manifest files. The agent must execute these scans within an ephemeral, strictly sandboxed container lacking network access to internal company resources, preventing a malicious `package.json` (e.g., via a post-install hook) from compromising the CI/CD pipeline.
- **Lockfile Immutability Enforcement**: The agent is strictly prohibited from bypassing the `package-lock.json` or `yarn.lock` during a build process. It must actively halt any deployment if it detects a divergence between the hashed lockfile and the stated dependencies, effectively blocking dynamic, unvetted code injection at runtime.

### 2. System Integration Security
- **Vulnerability Remediation Prioritization**: The agent must integrate with the overarching threat model. If the SCA tool flags a `CRITICAL` vulnerability in a library (e.g., an image parsing library), but that library is only deployed in a segmented, internal-only, unauthenticated reporting tool, the fix priority is high, but not an immediate block. However, if the vulnerable library touches the public internet, the build MUST fail.
- **Private Registry Mirroring**: To mitigate "Left-Pad" incidents and upstream registry compromises, the architecture must route all dependency pulls through a controlled, internal proxy registry (e.g., Artifactory, Nexus). The agent must flag any configuration that attempts to fetch dependencies directly from the public internet bypassing this proxy.

### 3. LLM & Agent Guardrails
- **Blind Upgrade Traps**: The agent must refuse user prompts that instruct it to blindly "Upgrade all dependencies to `latest` to fix the security warnings." Automated mass upgrades frequently introduce breaking changes or unintentionally pull in typosquatted/poisoned packages. Upgrades must be atomic, tested, and individually verified.
- **Ignoring Critical CVEs**: If a developer prompts the agent to "Add this specific CVE ID to the ignore list so the build passes," the agent must mandate an explicit, documented, and approved risk acceptance justification. It cannot unilaterally suppress critical security warnings based on a casual command.
