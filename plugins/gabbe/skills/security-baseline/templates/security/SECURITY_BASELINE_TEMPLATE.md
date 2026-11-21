# Security Baseline — <project>
<!-- Copy to project/SECURITY_BASELINE.md at S01. Skill: agents/skills/security/security-baseline.skill.md. Owner: ops-security. Update at each phase end. -->

## 1. Tier
| Item | Value |
|---|---|
| Tier (1, 2 or 3) | |
| Row of the tier table that matched | |
| Date | |

Human's confirmation (their words, name, date): "..."

## 2. Controls by phase
Status: `NOT_STARTED`, `IN_PROGRESS`, `DONE`, `N/A` (write the reason). `DONE` needs an evidence file that exists.

| Phase | Control | Applies to tier | Status | Evidence path | Checked by (S07) |
|---|---|---|---|---|---|
| S01 | Security and privacy requirements, data classification | 1, 2, 3 | | `docs/requirements/DATA_CLASSIFICATION.md` | |
| S01 | Abuse cases | 2, 3 | | `docs/security/ABUSE_CASES.md` | |
| S02 | Trust boundaries and dependency choices | 1, 2, 3 | | `docs/security/THREAT_MODEL.md` | |
| S02 | Threat model | 2, 3 | | `docs/security/THREAT_MODEL.md` | |
| S02 | Assurance level per component | 3 | | `project/ASSURANCE_PLAN.md` | |
| S03 | Auth, authorisation and input rules in the spec | 1, 2, 3 | | `SPEC.md` | |
| S05 | Secrets outside code; dependencies pinned | 1, 2, 3 | | `docs/security/evidence/` | |
| S06 | Gate G5; secret scan; static analysis | 1, 2, 3 | | `docs/security/evidence/` | |
| S06 | SBOM | 2, 3 | | `docs/security/evidence/` | |
| S06 | Red-team run (AI software), provenance (artifacts) | 3 | | `docs/security/RED_TEAM_REPORT.md` | |
| S07 | Security review, checklist, human sign-off | 1, 2, 3 | | `docs/security/SECURITY_REVIEW.md` | |
| S09/S10 | Hardening, least-privilege deploy credentials, rollback | 1, 2, 3 | | `docs/ops/` | |
| S11 | Patching period, advisory contact, incident plan | 1, 2, 3 | | `docs/ops/` | |
| S13 | Data and key disposal | 1, 2, 3 | | `docs/ops/` | |
| any | AI software: injection, tool permissions, output handling | AI | | `docs/security/AGENT_TOOLS.md` | |

Patching period: ______ days for CRITICAL/HIGH. Rescan schedule: ______.

## 3. Open risks accepted by the human
| Risk | Accepted by (name) | Date | Reason | Review date |
|---|---|---|---|---|
| | | | | |

Only the human adds a row. The agent never writes an acceptance.

## 4. Dependencies and tools (pinned versions)
| Name | Version (exact) | Purpose | Source checked (URL, date) |
|---|---|---|---|
| | | | |
