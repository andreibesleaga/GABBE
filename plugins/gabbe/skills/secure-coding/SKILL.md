---
name: secure-coding
description: "Apply OWASP Proactive Controls while writing code: validation, output encoding, authN/authZ, crypto choices. Use when code handles untrusted input, sessions, secrets or encryption."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/secure-coding.skill.md"
  tags: "coding"
  core: "true"
  context_cost: "low"
---
# secure-coding Skill

## Goal
This skill guides the implementation of security controls *during* development (Shift Left).

## Steps
## 1. Input Validation (Defense)
> "Never trust input."

- **Syntactic Validation**: Is it an email? Is it a number? (Use Zod/Pydantic).
- **Semantic Validation**: Is `start_date` before `end_date`? Is `transfer_amount` > 0?
- **Allow-list**: Only accept known good characters (e.g., `[a-zA-Z0-9]`). Block everything else.

## 2. Output Encoding (Defense)
> "Context matters."

- **HTML Context**: Escape `<` -> `&lt;`. (Prevent XSS).
- **SQL Context**: Use Parameterized Queries. (Prevent SQLi).
- **JSON Context**: Ensure valid JSON structure.

## 3. Authentication & Authorization
- **NIST Guidelines**:
  - Passwords: Min 12 chars, no complexity rules, check against pwned passwords.
  - MFA: Required for admin/privileged actions.
  - Sessions: Absolute timeout (e.g., 12 hours) + Idle timeout (e.g., 30 mins).
- **Authorization**:
  - **Broken**: `if (user.isAdmin)` (Client-side check).
  - **Fixed**: `if (ctx.user.hasPermission('delete:user'))` (Server-side check).

## 4. Cryptography
- **At Rest**: Use AES-256-GCM (Authenticated Encryption).
- **In Transit**: TLS version rule: `security/cryptography-standards.skill.md`.
- **Hashing**: Argon2id; parameters and legacy options: `security/cryptography-standards.skill.md`.
- **Secrets**: Never hardcode. Read them from the environment or the project's secret store.

Part of the path in `security/security-baseline.skill.md`; evidence goes in project/SECURITY_BASELINE.md.

## Constraints
- Validate input with strict schemas and convert types before range checks.
- Allow-list known good input; reject the rest.
- Check permissions on the server, never only on the client.

## Output Format
Code changes with, for each boundary touched, a short note of the controls applied: validation, output encoding, authentication and authorisation, cryptography.

## Limits and safety
- A secret found in code is removed from the code and the human is told to rotate it; moving it into a constant does not fix it. Removing it from git history needs the human's yes.
- Use maintained standard libraries for cryptography, authentication and sanitising (for example `DOMPurify`, an Argon2id or bcrypt library, the platform's crypto); never write your own, and check a new package's name and maintenance before adding it.
- Do not add a fallback to weaker protocols or algorithms for old clients; fail instead.
- Encode for the destination context (HTML body, attribute, script, URL, SQL); a value encoded for one context is not safe in another.
- Every handler that changes data checks permission on the server; being logged in is not permission.
