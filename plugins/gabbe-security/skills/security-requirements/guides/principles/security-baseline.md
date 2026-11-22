# Security Baseline for Software Built with the Kit
<!-- One-page path from S01 to S13, a standards map checked on 2026-11-21, and what the project must set up outside the model. Skill: skills/security/security-baseline.skill.md -->

> Applies to the software you build, not to the kit itself. Rules every agent follows are in
> `CONSTITUTION.md` Article 0 and `guides/principles/skill-guardrails.md`. This guide does not repeat them.

## 1. The path on one page
1. At S01 pick the tier (1, 2 or 3) from the requirements. The human confirms it. It is written in
   `project/SECURITY_BASELINE.md` (template: `templates/security/SECURITY_BASELINE_TEMPLATE.md`).
2. At each phase do the minimum for all tiers and the additions for the tier (table in the skill).
3. Each control leaves a file under `docs/security/` or `docs/ops/`. The row names the path.
4. At S07 the reviewer (ops-security) follows each path. No file, no pass. The human signs off.
5. The baseline adds evidence to quality gates G1-G9. G5 (dependency security: no CRITICAL or HIGH) stays
   with orch-judge. A security-critical core also gets an assurance level (`principles/assurance-ladder.md`).

| Tier | Matches when | In short |
|---|---|---|
| 1 | Internal, no personal data, no money, not on the internet, no AI agent with tools | requirements, pinned dependencies, G5, secret scan, review |
| 2 | On the internet, or personal data, or user accounts | tier 1 plus threat model, data map, SBOM, hardening, incident plan |
| 3 | Money, health, harm to people, login provider, AI agent with tools, regulated data | tier 2 plus assurance level, red-team run, provenance, drills |

## 2. Kit controls and the standards they map to
Every row names the standard, its version and the item. A row appears only when it was read in the source on
2026-11-21. This is coverage, not certification.

| Kit control | Standard, version | Item |
|---|---|---|
| `security-audit` step 2 | OWASP Top 10:2025 | A01 Broken Access Control; A02 Security Misconfiguration; A03 Software Supply Chain Failures; A04 Cryptographic Failures; A05 Injection; A06 Insecure Design; A07 Authentication Failures; A08 Software or Data Integrity Failures; A09 Security Logging and Alerting Failures; A10 Mishandling of Exceptional Conditions |
| `api-security` | OWASP API Security Top 10, 2023 | API1 Broken Object Level Authorization to API10 Unsafe Consumption of APIs |
| `security-requirements`, spec | OWASP ASVS 5.0.0 (30 May 2025) | chapters V1 Encoding and Sanitization, V2 Validation and Business Logic, V4 API and Web Service, V6 Authentication, V7 Session Management, V8 Authorization, V11 Cryptography, V12 Secure Communication, V13 Configuration, V14 Data Protection, V15 Secure Coding and Architecture, V16 Security Logging and Error Handling |
| tier choice | ASVS 5.0.0 levels L1, L2, L3 | Kit suggestion, not defined by ASVS: tier 1 aims at L1; tier 2 at L1 and L2 for sensitive parts; tier 3 at L2, L3 for the critical core |
| `secure-coding`, `access-control`, `api-security`, `fuzz-differential-testing` | CWE Top 25, 2025 | CWE-79, CWE-89, CWE-352, CWE-862, CWE-787, CWE-22, CWE-416, CWE-125, CWE-78, CWE-94 are ranks 1 to 10 |
| `cryptography-standards` | OWASP Password Storage Cheat Sheet | Argon2id (m=19456 KiB, t=2, p=1) first; bcrypt legacy only, work factor at least 10 |
| `cryptography-standards`, `secure-coding` | NIST SP 800-63B-4 (26 Aug 2025) | single-factor password minimum 15 characters; 8 when only part of multi-factor; accept at least 64; no composition rules; check against a blocklist |
| `cryptography-standards` | OWASP Transport Layer Security Cheat Sheet | default TLS 1.3, TLS 1.2 for compatibility, TLS 1.0 and 1.1 disabled (RFC 8996) |
| `dependency-security` step 4 | CycloneDX 1.7 (ECMA-424); SPDX 3.0 | the two SBOM formats the skill produces |
| `dependency-security` step 5 | SLSA v1.2, Build track | L1 provenance exists; L2 signed, hosted build; L3 hardened, isolated build |
| project settings (section 4) | OpenSSF Scorecard (checks list) | Branch-Protection, Code-Review, Dangerous-Workflow, Dependency-Update-Tool, Pinned-Dependencies, SAST, SBOM, Security-Policy, Signed-Releases, Token-Permissions, Vulnerabilities |
| AI software | OWASP Top 10 for LLM Applications, 2025 | LLM01 Prompt Injection to LLM10 Unbounded Consumption (`prompt-injection-defense`, `ai-safety-guardrails`, `agent-tool-review`) |
| AI agents | OWASP Top 10 for Agentic Applications (released 9 Dec 2025) | ASI01 Agent Goal Hijack to ASI10 Rogue Agents |
| S11 incident plan | GDPR Article 33 | notify the authority within 72 hours where feasible |
| S11 incident plan | HIPAA, 45 CFR 164.404 | notify individuals without unreasonable delay, within 60 days |
| S01 regulation check | EU Cyber Resilience Act | in force 10 Dec 2024; reporting duties apply from 11 Sep 2026; main duties from 11 Dec 2027 |
| whole path | NIST SSDF, SP 800-218 v1.1 (Feb 2022); SP 800-218A for AI model development | no item-level mapping done; practice names were not re-read |

Notes. The CRA row is a date list, not advice: whether your product is in scope is for the human and counsel.
The ASVS requirement numbers are not quoted here; open the chapter and pick the requirements that apply.
SOC 2 criteria ids and PCI DSS requirement numbers in `compliance-review` were not re-verified (see that skill).

## 3. What the kit cannot enforce by text
The kit is Markdown. An agent that ignores it, or a person with write access, is not stopped by it. These
controls exist only if you set them up. The baseline lists them so the S07 reviewer can ask for each one.

| Control | What it gives | Where |
|---|---|---|
| Branch protection and required reviews | no direct push to `main`; a review before merge | Git host settings |
| Required status checks | tests, G5 scan and secret scan must pass | Git host and CI |
| Secret scanning and push protection | blocks pushes that contain secrets | Git host (GitHub: repository setting, needs GitHub Secret Protection) |
| Least-privilege tokens | CI and the agent cannot reach more than the task needs | CI settings (GitHub: default `GITHUB_TOKEN` read-only, raise per job); cloud IAM |
| Pinned CI actions | a moved tag cannot change your build | workflow files (full commit SHA, from the action's own repository) |
| Signed releases and provenance | users can verify who built an artifact | release workflow; SLSA, signing tool of your registry |
| Dependency update service | advisories become pull requests | Git host or a bot, with `dependency-upgrade` rules |
| Backups and restore test | a way back | infrastructure; `backup-recovery` |
| Agent permissions, hooks, sandbox | what an agent can run | the agent tool's settings; `agent-sandboxing` |

## 4. Rules for tools named in the skills
- Tools run in the user's project, never inside the kit. Install only after the human says yes.
- Pin each tool's version in the baseline table (section 4 of the template). Re-check commands against the
  tool's own documentation when you change the version.
- A tool that is not installed is reported "not run". A regex search is not a substitute for a scanner.

## 5. References (each fetched on 2026-11-21)
- OWASP Top 10:2025 — https://top10.owasp.org/2025 (checked 2026-11-21)
- OWASP API Security Top 10, 2023 — https://api-security.owasp.org/ (checked 2026-11-21)
- OWASP ASVS 5.0.0 — https://asvs.owasp.org/ and https://github.com/OWASP/ASVS/tree/master/5.0/en (checked 2026-11-21)
- OWASP Top 10 for LLM Applications 2025 — https://genai.owasp.org/llm-top-10/ (checked 2026-11-21)
- OWASP Top 10 for Agentic Applications — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ (checked 2026-11-21)
- OWASP Password Storage Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html (checked 2026-11-21)
- OWASP Transport Layer Security Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html (checked 2026-11-21)
- CWE Top 25, 2025 — https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html (checked 2026-11-21)
- NIST SP 800-63B-4 — https://pages.nist.gov/800-63-4/sp800-63b.html (checked 2026-11-21)
- NIST SP 800-218 (SSDF 1.1) — https://csrc.nist.gov/pubs/sp/800/218/final (checked 2026-11-21)
- NIST SSDF project page — https://csrc.nist.gov/projects/ssdf (checked 2026-11-21)
- SLSA v1.2 — https://slsa.dev/spec/v1.2/build-requirements (checked 2026-11-21)
- OpenSSF Scorecard checks — https://github.com/ossf/scorecard/blob/main/docs/checks.md (checked 2026-11-21)
- CycloneDX — https://cyclonedx.org/specification/overview/ (checked 2026-11-21)
- SPDX — https://spdx.dev/use/specifications/ (checked 2026-11-21)
- EU Cyber Resilience Act — https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act (checked 2026-11-21)
- GDPR Article 33 (unofficial text) — https://gdpr-info.eu/art-33-gdpr/ (checked 2026-11-21)
- HIPAA 45 CFR 164.404 — https://www.ecfr.gov/current/title-45/part-164/section-164.404 (checked 2026-11-21)
- RFC 8996 — https://www.rfc-editor.org/rfc/rfc8996 (checked 2026-11-21)
- GitHub Actions security hardening — https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions (checked 2026-11-21)
- GitHub push protection — https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection (checked 2026-11-21)
- Tool: gitleaks — https://github.com/gitleaks/gitleaks (checked 2026-11-21)
- Tool: pip-audit — https://github.com/pypa/pip-audit (checked 2026-11-21)
- Tool: uv audit — https://docs.astral.sh/uv/reference/cli/ (checked 2026-11-21)
- Tool: npm audit — https://docs.npmjs.com/cli/v10/commands/npm-audit (checked 2026-11-21)
- Tool: composer audit — https://getcomposer.org/doc/03-cli.md#audit (checked 2026-11-21)
- Tool: osv-scanner — https://google.github.io/osv-scanner/usage/ (checked 2026-11-21)
- Tool: trivy — https://trivy.dev/latest/docs/ (checked 2026-11-21)
- Tool: syft — https://github.com/anchore/syft (checked 2026-11-21)
- Tool: checkov — https://www.checkov.io/2.Basics/CLI%20Command%20Reference.html (checked 2026-11-21)
- Tool: semgrep — https://docs.semgrep.dev/getting-started/cli (checked 2026-11-21)

Not verified today and left out of the table: the exact NIST SSDF practice names, PCI DSS 4.0.1 requirement
text, AICPA SOC 2 criteria ids, cosign command flags, `cargo audit`, bandit, ESLint security plugin, Enlightn.
Check them before relying on them.
