---
name: dependency-security
description: "Scan dependencies for known vulnerabilities, pin versions, produce an SBOM and record build provenance for the software you build. Use at S02 for dependency choices, at S06 for gate G5, and at S11 for patching. Use when: dependency security, vulnerable dependency, sbom, supply chain, lockfile, pin dependencies, provenance, g5."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/dependency-security.skill.md"
  tags: "security"
  core: "true"
  context_cost: "low"
---
# dependency-security Skill

## Goal
This skill secures the software supply chain.

## Where it fits
Phase and gate: S02 (dependency choices), S05 (pinning), S06 (quality gate G5: no CRITICAL or HIGH), S11 (patching, with `ops/dependency-lifecycle.skill.md`). Evidence: scanner output and the SBOM under `docs/security/evidence/`. Part of `security-baseline.skill.md`.

## Steps
Each command below was checked against its tool's own documentation on 2026-11-21. Run only the ones that fit the project. Save each output under `docs/security/evidence/`. A tool that is not installed is reported as "not run".

1. **Scan for known vulnerabilities (SCA).** Done when the output is saved and every CRITICAL and HIGH finding is fixed or accepted (see step 7). This is quality gate G5.
   ```bash
   npm audit --audit-level=high            # Node.js; non-zero exit at or above the level
   composer audit --locked                 # PHP; audits composer.lock
   pip-audit -r requirements.txt           # Python; `pip-audit --locked .` for a pyproject.toml or pylock project
   uv audit                                # Python projects managed with uv
   osv-scanner scan -L package-lock.json   # any lockfile; `osv-scanner scan -r .` scans a directory
   ```
   `cargo audit` is the usual tool for Rust (not re-verified; check its repository first).
2. **Install from the lockfile only.** Commit the lockfile. In CI install with the command that fails when the lockfile and manifest differ (for npm: `npm ci`; check the npm documentation). For pip, use a requirements file with hashes and `pip-audit --require-hashes -r requirements.txt`.
3. **Pin.** Exact versions or a lockfile for application dependencies. In GitHub Actions workflows pin third-party actions to a full commit SHA, taken from the action's own repository, and set the default `GITHUB_TOKEN` permission to read-only (GitHub's security hardening guide).
4. **Produce an SBOM** for every release of tier 2 and tier 3 software (tier 1: optional). Done when the file exists and its spec version is recorded.
   ```bash
   syft ./my-project -o cyclonedx-json=sbom.cdx.json -o spdx-json=sbom.spdx.json
   ```
   CycloneDX 1.7 (ECMA-424) and SPDX 3.0 are the current specifications; a tool may still write an older version, so read the version in the output file.
5. **Provenance for published artifacts** (tier 3, or any package or image others install). Build in CI, not on a laptop. SLSA v1.2 Build L1 means the build writes provenance that names the output by digest; L2 adds signed provenance from a hosted build platform; L3 adds isolated builds. Record the level reached and the gap to the next one. For npm packages, `npm audit signatures` checks registry signatures and provenance of what you install.
6. **Check a new dependency before adding it.** Name spelling (typosquatting), maintainer, last release, licence (`legal-review.skill.md`), install scripts. Prefer a scoped name. One line per dependency in the pull request.
7. **Triage and exceptions.** Fix by upgrading one dependency at a time (`ops/dependency-upgrade.skill.md`). If a fix is not possible, the human accepts the risk: a row in the open risks of `project/SECURITY_BASELINE.md` with name, date and reason. Only then add the finding to an ignore list.
8. **Keep it current.** At S11 repeat step 1 on a schedule set in the baseline (`ops/dependency-lifecycle.skill.md`) and when an advisory names a dependency you use.

If the organisation runs a private registry proxy, use it; if not, step 6 is the control.

## Constraints
- Gate G5: any CRITICAL or HIGH finding fails it until fixed or accepted by the human.
- The SBOM and scan outputs are made from the release commit.

## Output Format
Scanner outputs, `sbom.cdx.json` and `sbom.spdx.json`, and the provenance level reached, under `docs/security/evidence/`.

## Limits and safety
- Run scanners that read untrusted manifests in the project's CI or a disposable environment, without production credentials.
- Never change pinned versions to `latest` and never upgrade everything to clear warnings. One change at a time, tested (`ops/dependency-upgrade.skill.md`).
- Add a vulnerability to an ignore list only after the human accepted the risk and a row exists in the open risks of `project/SECURITY_BASELINE.md`.
- Install scanners in the user's project only, and only after the human says yes. Never add them to the kit.
