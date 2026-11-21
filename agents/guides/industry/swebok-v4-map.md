# SWEBOK v4 Map

> Which parts of GABBE address which knowledge area of the SWEBOK Guide. This is a reading aid, not a
> claim that GABBE conforms to SWEBOK.

## Source

SWEBOK Guide V4.0a, edited by Hironori Washizaki, IEEE Computer Society. It has **18 knowledge areas
(KAs)**, numbered as in the table below. Download:
`https://ieeecs-media.computer.org/media/education/swebok/swebok-v4.pdf` (page `https://computer.org/swebok`).
The number and the names were read from that file's table of contents on 21 November 2026.
The 2014 edition (V3) had 15 areas with different numbers; do not mix the two.

## How to read the ratings

- **Strong**: a skill, a persona or a template, and a phase or gate where the work is checked.
- **Partial**: one or two of those.
- **Weak**: scattered mentions, or no step that an agent can follow.
- **None**: nothing in the kit.

Phases are S00 to S13 in `agents/guides/processes/loki-sdlc-phases.md`.

## Map

| KA | Knowledge area | Kit items | Phases | Rating |
|---|---|---|---|---|
| 1 | Software Requirements | skills `req-elicitation`, `spec-writer`, `req-review`, `user-story-mapping`, `spec-analyze`; persona `prod-pm`; templates `PRD_TEMPLATE`, `NFR_TEMPLATE`, `REQUIREMENTS_REVIEW_TEMPLATE` | S01, S03 | Strong |
| 2 | Software Architecture | skills `arch-design`, `attribute-driven-design`, `arch-review`, `architecture-governance`, `fitness-functions`, `adr-writer`; persona `prod-architect`; templates `ADR_TEMPLATE`, `C4_ARCHITECTURE_TEMPLATE` | S02 | Strong |
| 3 | Software Design | skills `design-patterns`, `domain-model`, `api-design`, `error-handling-strategy`; guides in `agents/guides/patterns/` | S02, S03 | Strong |
| 4 | Software Construction | skills `tdd-cycle`, `clean-coder`, `refactor`, `secure-coding`, `git-workflow`; Constitution; personas `eng-*` | S05 | Strong |
| 5 | Software Testing | skills `testing-strategy`, `pbt-strategy`, `metamorphic-testing`, `characterization-tests`, `mutation-testing`, `chaos-fault-injection`, `browser-tdd`; persona `eng-qa`; templates `TEST_PLAN_TEMPLATE`, `TEST_CASE_TEMPLATE` | S06 | Strong |
| 6 | Software Engineering Operations | skills `deployment`, `infra-devops`, `observability-stack-setup`, `runbook-authoring`, `incident-response`, `reliability-sre`; personas `ops-devops`, `ops-sre`, `ops-incident` | S09 to S11 | Strong |
| 7 | Software Maintenance | skills `existing-project-onboarding`, `code-archaeology`, `safe-refactoring`, `incremental-feature`, `dependency-upgrade`, `tech-debt`; persona `eng-maintainer`; guide `brownfield-lifecycle` | S11, brownfield stages B0 to B4 | Partial: no change-request intake and no split into corrective, adaptive, perfective and preventive work |
| 8 | Software Configuration Management | skills `configuration-management`, `git-workflow`, `release-management`, `dependency-lifecycle`; persona `ops-release` | S05, S10 | Strong |
| 9 | Software Engineering Management | skills `estimation-sizing`, `stakeholder-management`, `change-management`, `decompose`; templates `ESTIMATION_TEMPLATE`; file `project/TASKS.md` | S04 | Weak: no risk-management or measurement-programme skill |
| 10 | Software Engineering Process | skills `system-lifecycle`, `retrospective`, `engineering-standards`; guides `loki-sdlc-phases`, `full-system-lifecycle` | S00 to S13 | Partial: the small-change lane tailors the process; there is no process assessment |
| 11 | Software Engineering Models and Methods | guide `modeling-methods`; skills `systems-thinking`, `semantic-web`, `diagramming`, `hazard-analysis`, `formal-spec-lightweight`, `design-by-contract` | S02, S03 | Partial |
| 12 | Software Quality | skills `final-review`, `integrity-check`, `traceability-audit`, `eval-driven-development`, `assurance-ladder`; persona `orch-judge`; quality gates G1 to G9 | S06, S08 | Strong |
| 13 | Software Security | skills `security-baseline`, `security-requirements`, `threat-model`, `security-audit`, `secure-coding`; persona `ops-security`; template `SECURITY_BASELINE_TEMPLATE`; guide `security-baseline` | S01 to S07 | Strong |
| 14 | Software Engineering Professional Practice | skills `professional-practice`, `legal-review`, `ai-ethics-compliance`; personas `prod-ethicist`, `biz-legal` | S08 | Partial |
| 15 | Software Engineering Economics | skills `business-case`, `financial-governance`, `cost-optimization`, `estimation-sizing`; template `BUSINESS_CASE_TEMPLATE` | S00, S02 | Partial: no build-or-buy or total-cost method |
| 16 | Computing Foundations | guide `computing-foundations`; skill `time-complexity` | none | Partial: a guide, with no step that turns it into a check |
| 17 | Mathematical Foundations | guide `mathematical-foundations` | none | Weak: a guide only |
| 18 | Engineering Foundations | skills `empirical-methods`, `eval-driven-development`, `hazard-analysis` | S06 | Partial: measurement and statistics only |

## Gaps

Weak or partial areas with the largest gap: KA 9 (management), KA 7 (maintenance process), KA 11
(model checking and proof are only light-weight skills), KA 15 (economics).
