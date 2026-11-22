---
name: security-requirements
description: "Turn a feature list into security and privacy requirements and abuse cases, written as testable EARS lines. Use at S01 when writing or reviewing a PRD for software with logins, personal data, uploads, payments or an AI agent. Use when: security requirements, abuse cases, misuse cases, security user stories, privacy requirements, security acceptance criteria."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/security-requirements.skill.md"
  tags: "security, requirements"
  core: "false"
  context_cost: "low"
---
# Security Requirements

## Goal
Make security part of the requirements, so S02 can design for it, S06 can test it and S07 can check it. Fits S01 (after `product/spec-writer.skill.md`, with `security-baseline.skill.md` for the tier). Lead: prod-pm with ops-security.

## Steps
1. **List the assets and actors.** Assets: data, money, accounts, the agent's tools. Actors: anonymous user, signed-in user, admin, other system, someone who wants to misuse the feature. Done when each feature in the PRD names its assets and actors.
2. **Classify the data.** For each data element write one class: public, internal, personal, sensitive (health, payment, credentials). Put the table in `docs/requirements/DATA_CLASSIFICATION.md`.
3. **Write abuse cases** for each feature that has a login, upload, payment-like step, search over other users' data, or tool call. Format: "As <actor>, I try to <misuse> to get <gain>." Three per feature at most; pick the likeliest. Done when each abuse case has a matching requirement in step 4.
4. **Write the requirements in EARS** with a measurable result, in `docs/requirements/EARS_REQUIREMENTS.md`, tagged `Security` or `Privacy`:
   - "WHEN a user requests a resource they do not own, THE SYSTEM SHALL return 403 and log the attempt."
   - "THE SYSTEM SHALL store passwords only as salted hashes made with Argon2id."
   - "WHEN login fails five times in one minute for one account, THE SYSTEM SHALL block further attempts for that account for a set period."
   Start from the lists in `guides/principles/security-baseline.md` (ASVS chapters) and pick what applies; do not copy a whole standard.
5. **Add the privacy items** that apply: purpose of each personal field, retention period, deletion and export path (`privacy-data-protection.skill.md`), consent where tracking or marketing is involved.
6. **Add the AI items** if a model or agent is used: what it may do without approval, which actions need the human, which data it may see (`prompt-injection-defense.skill.md`, `agent-tool-review.skill.md`).
7. **Hand over.** Each Security or Privacy requirement has an ID that `traceability-audit.skill.md` will check for a test. The human approves them with the PRD at gate S01.

## Constraints
- Every requirement is testable and has an ID.
- Each abuse case maps to at least one requirement.

## Output Format
`docs/requirements/DATA_CLASSIFICATION.md`, Security and Privacy lines in `docs/requirements/EARS_REQUIREMENTS.md`, and the abuse cases in `docs/security/ABUSE_CASES.md`.

## Limits and safety
- Requirements state what must hold, not a tool or a vendor. Do not copy numbers from a standard without naming the standard and its version.
- Which law applies is for the human or counsel to decide. Ask; do not assume.
- Do not write requirements that need data or access the project does not have; list them as open questions.
- Abuse cases are about the project's own software. Do not run them against any system.
