---
name: security-baseline
description: Sets what every project built with the kit does for security, phase by phase, by risk tier, and records it in project/SECURITY_BASELINE.md. Use at S01 and S02 when starting a project, when a project handles personal data, money or an AI agent with tools, or when asked what security work a phase needs.
triggers: [security baseline, security tier, security by phase, what security do we need, security plan, secure by default, security evidence]
tags: [security, lifecycle, risk]
context_cost: medium
core: true
---
# Security Baseline

## Goal
Give the project one security path through S01 to S13: a minimum for every project, and more for riskier ones. The baseline adds evidence to the quality gates G1-G9. It never replaces a gate. Guide: `guides/principles/security-baseline.md`. Owner: `personas/ops-security.md`.

## Steps
1. **Choose the tier** from the requirements (S01). The highest row that matches is the tier. Done when you can name the matching row.

| Tier | Matches when |
|---|---|
| 1 | Internal tool or script; no personal data; no money; not reachable from the internet; no AI agent with tools |
| 2 | Reachable from the internet, or holds personal data, or has user accounts; no tier 3 row matches |
| 3 | Money or payment cards; health data; harm to people or assets if it fails; it provides login for other systems; an AI agent that has tools (it can write, send, run code or call services); regulated data |

2. **Ask the human to confirm the tier.** Write `project/SECURITY_BASELINE.md` from `templates/security/SECURITY_BASELINE_TEMPLATE.md`, with the tier and the human's confirmation line. Add one `AUDIT_LOG.md` row. The human may raise or lower the tier; the agent never lowers it alone.
3. **Work the table below phase by phase.** Do the "all tiers" column always; add the tier column. At each phase end, set the status and the evidence path of each control in `project/SECURITY_BASELINE.md`. Done when no row of the phase is empty.

| Phase | All tiers | Tier 2 adds | Tier 3 adds | Skill |
|---|---|---|---|---|
| S01 | List security and privacy requirements as EARS lines; classify the data | Abuse cases for each login, upload and payment-like step | Regulation check; hazard list if harm is possible | `security-requirements`, `compliance-review`, `hazard-analysis`, `ai-ethics-compliance` |
| S02 | Trust boundaries drawn; dependency choices listed with licence | Threat model (STRIDE); data flow map | Assurance level per component; network zones; crypto choices in an ADR | `threat-model`, `secure-architecture`, `privacy-audit`, `assurance-ladder`, `legal-review` |
| S03 | Auth, authorisation and input rules written in the spec | API contract with an auth rule per endpoint | Permission matrix; rate limits | `api-security`, `access-control`, `spec-writer` |
| S05 | Secrets outside code; dependencies pinned; no secret in a commit | Input validation and output encoding at every boundary | Review of every security-critical change by the human | `secure-coding`, `secrets-management`, `dependency-security`, `safety-scan` |
| S06 | Gate G5 (no CRITICAL or HIGH); secret scan; static analysis run | Static analysis findings triaged; SBOM produced | Fuzzing of parsers; red-team run for AI software; provenance for artifacts | `dependency-security`, `safety-scan`, `security-audit`, `ai-red-teaming` |
| S07 | Security review and checklist; human sign-off | Privacy review; logging review | Compliance gap report; level 3 trusted-base review | `security-audit`, `privacy-audit`, `compliance-review`, `log-analysis` |
| S09, S10 | Debug off; defaults changed; deploy credentials limited to what the deploy needs; rollback tested | Headers and TLS checked; restore test | Network rules checked; separate deploy and runtime identities | `deployment`, `network-security`, `backup-recovery`, `cryptography-standards` |
| S11 | Patch within the period in the baseline; a named person gets advisories | Vulnerability intake path published; incident plan with contacts | Scheduled rescan; incident drill; key rotation | `dependency-lifecycle`, `secrets-management`, `incident-response` |
| S13 | Data and keys disposed of as planned | Deletion of personal data confirmed | Disposal record for the regulator or customer | `decommission-sunset`, `privacy-data-protection` |

4. **For AI or agentic software** (any tier) also do, at S02 and S07: instruction injection and the trifecta test (`prompt-injection-defense`); tool permissions (`agent-tool-review`); output handling and rails (`ai-safety-guardrails`, `output-validation`); isolation (`agent-sandboxing`); model, data and package supply chain (`dependency-security`, `integrity-check`). Tier 3 adds `ai-red-teaming`.
5. **Show the evidence.** Each control row names a file under `docs/security/` (see the evidence column of the template). At S07 the reviewer opens `project/SECURITY_BASELINE.md` and follows each path. A row without a file is a FAIL.
6. **Record accepted risks.** Only the human accepts one: name, date, reason in the open-risks table. The agent never writes an acceptance for the human.
7. **Link to the rest of the kit.** A security-critical core gets an assurance level in `project/ASSURANCE_PLAN.md` (`assurance-ladder`); tier 3 means level 2 or higher is proposed for authorisation and money logic. Quality gates stay as defined by orch-judge. G5 is the dependency gate; the baseline adds its evidence.

## Constraints
- The tier is confirmed by the human before phase work starts.
- A control row is DONE only when its evidence file exists.

## Output Format
`project/SECURITY_BASELINE.md`, updated at each phase end, and the evidence files it points to.

## Limits and safety
- This is a plan and an evidence list. It does not enforce anything: branch protection, required checks and secret scanning come from your platform (see the guide).
- A filled table shows that steps were done, not that the software is secure. Say so in the S07 summary.
- Do not install tools in the user's project without the human's yes. Do not lower a tier or accept a risk for the human.
- Standards named in the guide change. Re-check the edition on the build day before quoting it.
