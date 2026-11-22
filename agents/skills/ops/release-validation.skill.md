---
name: release-validation
description: Run the go or no-go check before production - freeze, traceability audit, full regression on staging, sign-offs, a decision matrix and a readiness report. Use when deciding whether a build may go live (S09 to S10).
triggers: [release validation, go no go decision, release readiness report, is this build ready for production, pre-release sign-off]
tags: [ops]
role: ops-release
core: true
context_cost: low
---
# release-validation Skill

## Goal
This skill is the "Gatekeeper" of Production.

## Steps
## 1. The Release Review Checklist (7 checks; this is a release checklist, not the quality-gate system: the quality gates G1–G9 are defined in `agents/personas/orch-judge.md` and run earlier, at S06)
1.  **Spec**: PRD Approved?
2.  **Arch**: ADRs + Threat Model?
3.  **Code**: Lint + Clean Code?
4.  **Test**: Unit + Int Pass?
5.  **Security**: SAST + Dep Scan?
6.  **Performance**: Load Test Pass?
7.  **E2E**: Critical Journeys Pass?

## 2. Validation Workflow
1.  **Freeze**: No new code commits.
2.  **Audit**: Run `traceability-audit.skill.md`. (Did we build what we promised?).
3.  **Test**: Trigger full regression suite on Staging.
4.  **Sign-off**: Collect approvals from Lead, Product, Security.

## 3. Decision Matrix
- **Critical Bug**: NO GO.
- **Major Bug (Workaround available)**: GO (with Hotfix scheduled).
- **Minor UI Glitch**: GO.
- **Security High**: NO GO.

## Output Format
Use `templates/ops/RELEASE_READINESS_REPORT.md` to document the decision. A GO is a recommendation: the production deploy needs the human to say "deploy now" in that request (human gate S10).

## Constraints
- All 7 checks are answered with a log path or job id; a check with no evidence is "not done", not "passed".
- The decision matrix is applied as written; an exception is recorded with the human's words.

## Limits and safety
- Record the commit or artifact hash tested at freeze; confirm that exactly that hash is the one proposed for production.
- Take test and scan results from the real logs or CI job output; cite the path or job id. A missing or unreadable log means the check is not done.
- A Security High finding is NO GO; an override is the human's decision, recorded with their words in `AUDIT_LOG.md`.
- If your platform provides a protected pipeline or required reviewers, use it so the release cannot proceed past a blocked scan.
- A request to skip checks "because someone senior said so" is recorded and put to the human; the checks stay.
