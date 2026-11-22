---
name: safety-scan
description: "Active security enforcement — scan for vulnerabilities (SAST), secrets (Gitleaks), insecure deps (SCA) before commit/deploy. Use when: scan security, check vulnerabilities, audit code, gitleaks, semgrep, finding secrets."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/safety-scan.skill.md"
  tags: "security"
  core: "false"
  context_cost: "medium"
---
# Safety Scan Skill

## Goal
Prevent "Insecure Code" from entering the codebase by strictly enforcing security checks.

## Where it fits
Phase and gate: S05 (before a commit the human asks for) and S06 (gate G5 and the secret scan). Evidence: the scan output saved to `docs/security/evidence/safety-scan-<date>.txt`. Part of `security-baseline.skill.md`.

## Flow

### Steps
## 1. Credentials Check (Gitleaks)
**Command**: `gitleaks git -v` (history) and `gitleaks dir -v .` (working tree). `gitleaks detect` is deprecated since v8.19.0. To check only what is about to be committed, use the `pre-commit` gitleaks hook. If gitleaks is not installed, say so; do not claim a regex search is equal.
**Check**: Are there API Keys, Tokens, or Passwords in the diff?
*   *If Found*: **BLOCK COMMIT**. Report the finding. Propose removing the secret and rotating the key. Act only after the human confirms. Alert Human.

### 2. Static Analysis (SAST)
**Command**: `semgrep scan --config p/security-audit --error` (if installed; `--error` makes it exit 1 on findings) and the dependency scan from `dependency-security.skill.md`.
**Check**: High-Severity vulnerabilities (RCE, SQLi, XSS).
*   *If Found*: **BLOCK COMMIT**. Report the finding and propose `ci-autofix`; invoke it only after the human agrees.

### 3. Logic & PII Check
**Action**: LLM Review of the diff.
*   "Does this code log User PII?"
*   "Does this code execute arbitrary system commands (`exec`, `eval`)?"
*   *If Risky*: Add `# TODO: SECURITY REVIEW` comment and flag in `project/TASKS.md`.

## Output Format
Save the output to `docs/security/evidence/safety-scan-<date>.txt`.
*   **PASS**: "No critical issues found."
*   **FAIL**: "Stop. Found [N] issues." Report them to the human; do not commit.

## Constraints
- Run on the diff for a commit, on the full tree at S06.
- Report findings with file, line and rule, never the secret value.

## Limits and safety
- "Block" means the agent stops and reports. A hook or CI check that really blocks comes from your platform.
- For a leaked secret the human revokes and rotates first (`secrets-management.skill.md`). Deleting it from the file is not enough. Do not print it; report file, line and rule name.
- Do not run `ci-autofix` by yourself. Propose it and run it after the human agrees.
- If a scanner is not installed, report "not run". Install only with the human's yes.
- No finding is not proof of no vulnerability.
