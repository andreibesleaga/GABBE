---
name: security-audit
description: OWASP Top 10 security audit, SAST/DAST/SCA scanning, secrets detection, and dependency vulnerability check
triggers: [security, vulnerability, OWASP, secrets, CVE, security audit, security scan, penetration]
tags: [security]
context_cost: high
---
# Security Audit Skill

## Goal
Identify security vulnerabilities in code, dependencies, and configuration using OWASP Top 10 as the primary framework. Produce an actionable report with severity ratings and specific remediation steps.

## Steps

1. **Run automated scanning tools**

   **Dependency vulnerabilities (SCA):**
   ```bash
   npm audit --audit-level=moderate    # Node.js
   composer audit                       # PHP
   uv pip audit                         # Python (or pip-audit)
   bandit -r src/                       # Python SAST
   pip-audit                            # Python
   snyk test                            # Cross-platform (if Snyk configured)
   ```

   **Static analysis (SAST):**
   ```bash
   npx semgrep --config=p/security-audit src/          # Cross-platform
   npx eslint --plugin security src/                   # JS/TS
   vendor/bin/enlightn                                  # Laravel
   bandit -r src/                                       # Python
   ```

   **Secret detection:**
   ```bash
   gitleaks detect --source=. --verbose
   # Or: truffleHog --regex --entropy=False .
   ```

2. **OWASP Top 10 manual review**

   **A01 — Broken Access Control**
   - Check: are authorization checks performed server-side for every protected resource?
   - Check: IDOR vulnerabilities (can user A access user B's resources by changing an ID?)
   - Check: privilege escalation paths (can a regular user trigger admin actions?)

   **A02 — Cryptographic Failures**
   - Check: passwords hashed with bcrypt/argon2 (never MD5, SHA1, SHA256 for passwords)
   - Check: sensitive data encrypted at rest (PII, financial data, health data)
   - Check: TLS enforced for all connections (no HTTP endpoints for sensitive data)
   - Check: no weak ciphers (TLS < 1.2, RC4, DES)

   **A03 — Injection**
   - Check: SQL injection — are all queries parameterized? (no string concatenation in SQL)
   - Check: Command injection — any `exec()`, `shell_exec()`, `child_process.exec()` with user input?
   - Check: LDAP injection, XPath injection in relevant use cases
   - Check: Template injection in server-side template rendering

   **A04 — Insecure Design**
   - Check: is there a threat model for security-sensitive features?
   - Check: are rate limits in place for auth endpoints, password reset, OTP?
   - Check: are business logic constraints enforced server-side?

   **A05 — Security Misconfiguration**
   - Check: are default credentials changed?
   - Check: are error responses sanitized (no stack traces in production)?
   - Check: are security headers set? (Content-Security-Policy, X-Frame-Options, HSTS)
   - Check: is directory listing disabled on web servers?

   **A06 — Vulnerable and Outdated Components**
   - Check: output of dependency audit (step 1)
   - Check: are there EOL (end of life) dependencies?

   **A07 — Authentication Failures**
   - Check: brute force protection on login (rate limiting, lockout)
   - Check: secure session management (HTTPOnly, Secure, SameSite cookies)
   - Check: are JWT tokens validated server-side (signature, expiry, audience)?
   - Check: password reset flow (single-use tokens, expiry)

   **A08 — Software and Data Integrity**
   - Check: are file uploads validated (type, size, content scanning)?
   - Check: are third-party scripts loaded from CDN with SRI hashes?
   - Check: is CI/CD pipeline secured (no arbitrary code execution from PRs)?

   **A09 — Security Logging and Monitoring**
   - Check: are security events logged? (failed logins, access denied, input validation failures)
   - Check: are logs sent to a SIEM or centralized logging?
   - Check: no sensitive data (PII, passwords) in logs?

   **A10 — SSRF (Server-Side Request Forgery)**
   - Check: any functionality that fetches remote URLs based on user input?
   - Check: are allowlists used for external URL fetching?
   - Check: are internal network resources protected from SSRF?

3. **Check for secrets in codebase**
   - Search for: API keys, tokens, passwords, connection strings in code
   - Common patterns: `api_key =`, `password =`, `token =`, `secret =`, `connectionString =`
   - Check git history for secrets that were committed and removed

4. **Container/infrastructure security** (if applicable)
   ```bash
   trivy image [image-name]          # Container vulnerability scan
   trivy fs .                        # Filesystem scan
   checkov -d infra/                 # IaC security (Terraform, Dockerfile)
   ```

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
   - [PASS] Password hashing uses bcrypt (cost factor 12)

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
- High findings must be fixed within 7 days of discovery
- Never dismiss a finding without documented justification
- If a finding requires disabling a feature: escalate to human first

## Output Format
Security audit report with CRITICAL/HIGH/MEDIUM/LOW findings + completed SECURITY_CHECKLIST.md.

## Security & Guardrails

### 1. Skill Security (Security Audit)
- **Audit Tool Supply Chain**: The agent must verify the cryptographic signatures or checksums of the automated scanning tools (`semgrep`, `gitleaks`, `trivy`) before executing them. This prevents a supply-chain attack where the scanning tools themselves are replaced with malicious binaries designed to exfiltrate code or whitelist specific vulnerabilities.
- **Finding Down-Scoring Veto**: The agent is strictly prohibited from autonomously downgrading the severity of a finding (e.g., changing a `CRITICAL` SQL Injection to a `LOW`) based on speculative mitigating factors. All severity downgrades require a formalized, peer-reviewed Risk Acceptance procedure.

### 2. System Integration Security
- **Audit Execution Privilege**: The agent must execute the dynamic portions of the security audit (if any) under an explicit "Security Auditor" service account. It must NOT use the primary CI/CD deployment credential, enforcing the Principle of Least Privilege and preventing the audit process from accidentally or maliciously modifying production infrastructure.
- **Isolation of Audit Artifacts**: The raw outputs of the security scans (especially DAST/SAST reports that may contain snippets of sensitive code or API keys) must be stored in a highly secured, access-controlled artifact repository. The agent must not inadvertently publish these detailed reports to public or broadly accessible wikis.

### 3. LLM & Agent Guardrails
- **Automated Dismissal Block**: Users might prompt the agent: "Ignore all Medium and Low vulnerabilities in this report to speed up the release." The agent must refuse this command. It can filter the display view for the user, but it must mandate that the final generated report represents the unfiltered, ground-truth vulnerability state of the application.
- **Remediation Hallucination**: When proposing remediation steps for complex vulnerabilities (e.g., A02 Cryptographic Failures), the LLM must consistently recommend tested, established, high-level cryptographic libraries (e.g., libsodium, Tink). It is explicitly forbidden from generating novel, custom cryptographic algorithms or "rolling its own crypto" in the proposed fix.
