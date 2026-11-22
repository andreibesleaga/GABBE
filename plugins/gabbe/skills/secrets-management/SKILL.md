---
name: secrets-management
description: "Handle API keys and credentials safely: storage levels, runtime injection, rotation, and the steps to take when a secret leaks. Use when code needs a credential, when adding a secret to config or CI, or after a secret was committed."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/secrets-management.skill.md"
  tags: "security"
  core: "true"
  context_cost: "low"
---
# secrets-management Skill

## Goal
This skill enforces the zero-trust handling of credentials.

## Where it fits
Phase and gate: S02 (where secrets live), S05 (never in code), S06 (secret scan), S11 (rotation and leak response). Evidence: secret-scan output, the rotation log in `docs/security/evidence/`, and an `AUDIT_LOG.md` row for each leak. Part of `security-baseline.skill.md`.

## 1. The Core Commandments
1.  **NEVER** commit secrets to Git. (Not even encrypted, if possible).
2.  **NEVER** log secrets to stdout/files.
3.  **LEAST PRIVILEGE**: An App's DB user should not be `postgres` (superuser).

## Steps
### Storage Patterns

### Level 1: Environment Variables (.env)
- **Dev**: `.env` file (gitignored).
- **Prod**: Injected by platform (Vercel/Heroku env vars).
- *Risk*: Shell history exposure, accidental printenv.

### Level 2: Secret Ops (SOPS / Encrypted Git)
- Secrets stored in git but encrypted with KMS/PGP.
- Decrypted only at build/deploy time.
- *Tool*: Mozilla SOPS, git-crypt.

### Level 3: Secret Manager (The Standard)
- AWS Secrets Manager, Google Secret Manager, HashiCorp Vault.
- App fetches secret at runtime via SDK or Sidecar.
- *Pros*: Rotation, Audit trails.

## 3. Secret Rotation
- **Static Secrets** (API Keys): Rotate on a schedule the project sets (90 days is a common default; write the chosen period in `project/SECURITY_BASELINE.md`) and at once after any leak.
- **Dynamic Secrets** (Db Creds): Vault creates a credential *per session* that expires in 1h.

## 4. Detection
- Scan history and tree: `gitleaks git -v` and `gitleaks dir -v .` (`gitleaks detect` is deprecated since v8.19.0). To stop a secret before the commit, install `pre-commit` and add the `gitleaks` hook from the gitleaks repository README (set `rev` to the current release tag).
- Platform control: on GitHub, push protection blocks pushes that contain secrets. A repository administrator or organisation owner turns it on; it needs GitHub Secret Protection (checked 2026-11-21).

## 4a. Leak response (a secret was committed, logged or sent)
Done when every line has a result in the incident note. The human runs or confirms each action marked (H).
1. Stop: do not add more commits that contain it. Do not print the value.
2. (H) Revoke or rotate the secret at the provider. Revoking comes first; cleaning history does not make the secret safe, because clones and forks keep it.
3. Find where it was used: the provider's access log for the key, from the commit date to now. List anything unexpected for the human.
4. Replace it in the current tree with a reference (environment variable or secret manager entry) and deploy the new value through the platform's secret store (H).
5. (H, optional) Rewrite history only if the human asks. Propose the exact command and the list of branches and clones affected, and warn that open pull requests and forks keep the old commits.
6. Record: an `AUDIT_LOG.md` row (date, what, who revoked, when) and, for tier 2 and 3, an entry in the incident log (`ops/incident-response.skill.md`).
7. Add the rule or path that was missed to the scanner configuration, and re-run the scan. Done when it is clean.

## 5. Kubernetes Secrets
- Default K8s Secrets are base64 encoded (NOT encrypted).
- **Requirement**: Enable Encryption-at-Rest for etcd.
- **Better**: Use "External Secrets Operator" to sync from AWS/Vault.

## Constraints
- No secret in code, config files in git, logs, chat or reports.
- Each secret has an owner, a store and a rotation period.

## Output Format
Secret-scan output, the rotation log, and the leak-response note when a leak happened, under `docs/security/evidence/`.

## Limits and safety
- Never print, log or commit a secret value. Reports show the variable name, file and line.
- Do not rotate, revoke or rewrite history yourself. Propose the exact commands and run them after the human confirms. Revoke first, clean up second.
- `.env` stays in `.gitignore`; check with `git check-ignore .env`.
- Do not create real secrets. Use placeholders in examples and tests.
- If your platform provides secret scanning or push protection, turn it on.
