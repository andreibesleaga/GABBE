---
name: security-audit
description: OWASP Top 10 security audit, SAST/DAST/SCA scanning, secrets detection, and dependency vulnerability check
triggers: [security, vulnerability, OWASP, secrets, CVE, security audit, security scan, penetration]
tags: [security]
core: true
context_cost: high
---
# Security Audit Skill

## Goal
Identify security vulnerabilities in code, dependencies, and configuration using OWASP Top 10 as the primary framework. Produce an actionable report with severity ratings and specific remediation steps.

## Where it fits
Phase and gate: S07 (security review, human sign-off). Lead: ops-security. Evidence: `docs/security/SECURITY_REVIEW.md` and the filled `SECURITY_CHECKLIST.md`, with scanner outputs under `docs/security/evidence/`. Checks the evidence listed in `project/SECURITY_BASELINE.md` (`security-baseline.skill.md`).

## Steps

1. **Run automated scanning tools.** Each command was checked against its tool's documentation on 2026-11-21. Run those that fit the project, save each output under `docs/security/evidence/`, and report a tool that is not installed as "not run".

   **Dependency vulnerabilities (SCA):** see `dependency-security.skill.md` for the commands and for gate G5.

   **Static analysis (SAST):**
   ```bash
   semgrep scan --config p/security-audit --error src/   # --error: exit 1 when there are findings
   bandit -r src/                                         # Python (not re-verified)
   ```
   For JS/TS use ESLint with `eslint-plugin-security` if the project has it configured; for Laravel use the project's Enlightn setup (neither re-verified).

   **Secret detection:**
   ```bash
   gitleaks git -v        # git history
   gitleaks dir -v .      # working tree
   ```
   (`gitleaks detect` is deprecated since v8.19.0.)

2. **OWASP Top 10:2025 review** (edition checked on top10.owasp.org on 2026-11-21). For each item, write PASS, FAIL or N/A with the file or command as evidence.

   **A01 Broken Access Control** (also check SSRF here: the 2025 list has no separate SSRF item)
   - Are authorisation checks done server-side for every protected resource?
   - IDOR: can user A reach user B's resources by changing an ID?
   - Can a regular user trigger admin actions?
   - Any function that fetches a URL from user input? Allowlist for outbound hosts? Internal networks protected?

   **A02 Security Misconfiguration**
   - Default credentials changed? Debug endpoints off in production?
   - Error responses without stack traces? Security headers set (Content-Security-Policy, HSTS, frame protection)?
   - Directory listing off? CORS not wider than needed?

   **A03 Software Supply Chain Failures**
   - Output of the dependency scan and the SBOM (`dependency-security.skill.md`)? Lockfile committed?
   - Any end-of-life dependency? CI actions pinned? CI cannot run arbitrary code from pull requests?

   **A04 Cryptographic Failures**
   - Passwords hashed with Argon2id (bcrypt only on legacy systems), never MD5, SHA1 or plain SHA256 (`cryptography-standards.skill.md`).
   - Sensitive data encrypted at rest; TLS enforced with the version rule of `cryptography-standards.skill.md`; no weak ciphers.

   **A05 Injection**
   - SQL: all queries parameterised? Commands: any `exec()` or `child_process.exec()` with user input?
   - Template, LDAP and XPath injection where relevant. Output encoded for its context.

   **A06 Insecure Design**
   - Is there a threat model for security-sensitive features (`threat-model.skill.md`)?
   - Rate limits on login, password reset and OTP? Business rules enforced server-side?

   **A07 Authentication Failures**
   - Brute-force protection? Cookies HttpOnly, Secure, SameSite? Session renewed after login?
   - Tokens validated server-side (signature, expiry, audience)? Reset tokens single-use and expiring?

   **A08 Software or Data Integrity Failures**
   - Uploads validated (type, size, content)? Third-party scripts loaded with integrity hashes?
   - Updates and artifacts verified before use? Deserialisation of untrusted data avoided?

   **A09 Security Logging and Alerting Failures**
   - Failed logins, access denied and validation failures logged? Someone alerted? No secrets or personal data in logs?

   **A10 Mishandling of Exceptional Conditions**
   - Do errors fail closed (deny on error, not allow)? Resources released on failure?
   - No unhandled exception shows internals to the user? Behaviour on timeouts and partial failures tested?

3. **Check for secrets in codebase**
   - Search for: API keys, tokens, passwords, connection strings in code
   - Common patterns: `api_key =`, `password =`, `token =`, `secret =`, `connectionString =`
   - Check git history for secrets that were committed and removed

4. **Container and infrastructure security** (if applicable)
   ```bash
   trivy image [image-name]          # container image scan
   trivy fs .                        # filesystem scan
   trivy config .                    # misconfiguration scan of IaC files
   checkov -d infra/                 # IaC security (Terraform, Dockerfile, Kubernetes ...)
   ```
   Command names and flags checked against the Trivy and Checkov documentation on 2026-11-21.

5. **Generate security report**
   ```markdown
   ## Security Audit Report
   Date: [date]
   Scope: [what was audited]

   ### Critical Findings (must fix before release)
   - [CRITICAL] file.ts:42 — SQL injection via unsanitized input in search endpoint

   ### High Findings
   - [HIGH] CVE-2024-XXXXX — lodash 4.17.20 has prototype pollution vulnerability

   ### Medium Findings
   - [MEDIUM] Missing rate limiting on /auth/login endpoint

   ### Low / Informational
   - [INFO] X-Frame-Options header not set

   ### Passed Checks
   - [PASS] No secrets detected in codebase
   - [PASS] All SQL queries use parameterized statements
   - [PASS] Password hashing uses Argon2id with the recorded parameters

   ### Remediation Priority
   1. Fix Critical first (blocking for release)
   2. Fix High within 7 days
   3. Fix Medium within 30 days
   4. Fix Low in next sprint
   ```

6. **Check SECURITY_CHECKLIST.md**
   - Go through templates/security/SECURITY_CHECKLIST.md line by line
   - Mark each item as PASS / FAIL / N/A with evidence

## Constraints
- Critical security findings are always blocking — no release without remediation
- High findings must be fixed within 7 days of discovery (the default; the project may set another period in the baseline)
- Never dismiss a finding without documented justification
- If a finding requires disabling a feature: escalate to human first
- For authorisation, money or other critical cores, check the chosen assurance level and its evidence: `assurance-ladder.skill.md`

## Output Format
Security audit report with CRITICAL/HIGH/MEDIUM/LOW findings, saved as `docs/security/SECURITY_REVIEW.md`, plus the completed `SECURITY_CHECKLIST.md` and the scanner outputs under `docs/security/evidence/`.

## Limits and safety
- Report all findings unfiltered. You may sort the view. Do not drop a finding or lower its severity without a risk acceptance by the human, recorded in the open risks of `project/SECURITY_BASELINE.md`.
- Run dynamic tests only against a test environment with test credentials, never the deploy credential.
- Reports can hold code snippets and key fragments. Keep them in `docs/security/` of a private repository and mask secrets.
- Install scanners in the user's project only, after the human says yes.
- A clean scan is a sample. State what was not scanned.
