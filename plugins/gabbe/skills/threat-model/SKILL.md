---
name: threat-model
description: "STRIDE threat modeling before implementing security-sensitive features. Use when: threat, STRIDE, attack surface, security design, new API, new feature security, threat model."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/threat-model.skill.md"
  tags: "security"
  core: "true"
  context_cost: "medium"
---
# Threat Model Skill

## Goal
Create a STRIDE threat model BEFORE implementing any security-sensitive feature. Prevents security issues at design time (cheapest point to fix) rather than after implementation (expensive) or in production (catastrophic).

## Where it fits
Phase and gate: S02 (system threat model, human gate) and before any security-sensitive feature. Evidence: `docs/security/THREAT_MODEL.md` and per-feature files in `docs/security/threat-models/`. Part of `security-baseline.skill.md`; the S07 reviewer checks that each mitigation exists.

## When to Invoke
- Before implementing: authentication, authorization, user registration, file upload
- Before implementing: payment processing, data storage, API endpoints, admin features
- Before any feature that handles: PII, financial data, health data, secrets, files

## Steps

1. **Identify system components and trust boundaries**
   - Reference the C4 Component diagram if it exists (`docs/architecture/`)
   - Draw the data flow: user → entry point → processing → storage → response
   - Mark trust boundaries (where permissions or privilege changes)
   - Identify actors: authenticated user, anonymous user, admin, external service, attacker

2. **Apply STRIDE to each component**

   For each component (API endpoint, service, data store), systematically ask:

   **S — Spoofing (impersonation)**
   - Can an attacker pretend to be another user or service?
   - Example threats: stolen JWT tokens, forged API keys, session hijacking

   **T — Tampering (data modification)**
   - Can an attacker modify data in transit or at rest?
   - Example threats: MITM attacks, SQL injection, parameter tampering, mass assignment

   **R — Repudiation (deny actions)**
   - Can an attacker deny performing an action?
   - Example threats: no audit log, no digital signature for financial transactions

   **I — Information Disclosure (data leaks)**
   - Can an attacker access data they shouldn't see?
   - Example threats: IDOR, verbose error messages, log injection, SSRF

   **D — Denial of Service**
   - Can an attacker degrade or block service availability?
   - Example threats: no rate limiting, resource exhaustion, large file uploads

   **E — Elevation of Privilege**
   - Can an attacker gain more permissions than they should have?
   - Example threats: JWT algorithm confusion, IDOR to admin endpoints, business logic bypass

3. **Score each threat**

   | Factor | Low | Medium | High |
   |---|---|---|---|
   | **Likelihood** | Attacker needs special access/skills | Known exploit pattern exists | Trivial to exploit |
   | **Impact** | Minor data exposure | User data compromised | All data, system compromise |

   Priority = Likelihood × Impact (High×High = Critical)

4. **Propose mitigations for High and Critical threats**

   ```markdown
   | Threat | STRIDE | L | I | Priority | Mitigation |
   |---|---|---|---|---|---|
   | Stolen JWT allows impersonation | S | H | H | Critical | Short expiry (15min), refresh token rotation, token revocation list |
   | IDOR on /users/{id} endpoint | I | M | H | High | Verify ownership: user.id === session.userId before returning |
   | No rate limit on /auth/login | D | H | M | High | Max 5 attempts/min per IP, 3 per account, exponential backoff |
   ```

5. **Fill THREAT_MODEL_TEMPLATE.md**
   - Save to: `docs/security/THREAT_MODEL.md` for the system (S02) and `docs/security/threat-models/[feature-name]-threat-model.md` for a feature
   - For software with an AI model or agent, add the surfaces from `prompt-injection-defense.skill.md` and `agent-tool-review.skill.md`

6. **Record new security invariants** as EARS requirements in the spec or in the security section of `AGENTS.md` (only the human amends `CONSTITUTION.md`)
   - Example: "WHEN a user accesses /api/users/{id}, THE SYSTEM SHALL verify the requesting user owns that resource"

7. **Create tasks for mitigations**
   - Add each High/Critical mitigation to project/TASKS.md
   - These are blocking tasks — must be implemented before the feature is complete

8. **Human review required**
   - Present threat model to human before implementing the feature
   - Confirm all Critical and High mitigations will be implemented

## STRIDE Quick Reference

| Letter | Category | Question to ask |
|---|---|---|
| S | Spoofing | Who is claiming to be who, and how do we verify it? |
| T | Tampering | What data can be modified by unauthorized parties? |
| R | Repudiation | Can actions be denied? Are they logged immutably? |
| I | Information Disclosure | What can be leaked, and to whom? |
| D | Denial of Service | What can be exhausted, flooded, or blocked? |
| E | Elevation of Privilege | How can someone gain more access than intended? |

## Constraints
- Threat modeling is MANDATORY before implementing: auth, payment, file storage, admin features
- All Critical threats must have implemented mitigations before feature ships
- High threats must have mitigations or documented risk acceptance by human
- Never implement a security control without documenting why it addresses a specific threat

## Output Format
Completed threat model file at `docs/security/threat-models/[name]-threat-model.md` + tasks added for mitigations.

## Limits and safety
- Each High or Critical mitigation gets a linked row in `project/TASKS.md`. If the row cannot be written, stop and tell the human.
- Fill all six STRIDE letters for every component. Write "none found, because ..." instead of skipping one.
- After approval, a change that removes a threat row or a mitigation goes back to the human.
- When infrastructure code or a deployment exists, compare it with the model and report any drift.
