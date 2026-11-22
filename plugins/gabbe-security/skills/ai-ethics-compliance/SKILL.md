---
name: ai-ethics-compliance
description: "Check an AI feature against EU AI Act and GDPR duties, test for bias and proxy variables, and screen for dark patterns. Use before shipping a feature that scores, ranks or profiles people, or that talks to users as an AI. Use when: ai ethics, eu ai act, bias test, fairness check, dark pattern, ai transparency."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/ai-ethics-compliance.skill.md"
  tags: "security"
  core: "false"
  context_cost: "low"
---
# ai-ethics-compliance Skill

## Goal
This skill ensures the system respects human rights and legal frameworks.

## Where it fits
Phase and gate: S01 (requirements, bias check) and S07 (review). Lead: prod-ethicist. Evidence: a filled `templates/security/ETHICAL_IMPACT_ASSESSMENT.md` in `docs/ethics/` with the fairness numbers and the metric named.

## Steps
## 1. Regulatory Checklist (EU AI Act / GDPR)
- **Transparency**: Does the user know they are interacting with AI? (Article 50 of Regulation (EU) 2024/1689, transparency duties; unofficial text at artificialintelligenceact.eu/article/50 checked 2026-11-21: confirm the article in the Official Journal text).
- **Explanation**: Can we explain *why* the AI made a decision? (Right to Explanation).
- **Data Rights**: Can the user request their data be deleted? (Right to be Forgotten).
- **Risk Category**: Is this "High Risk" (CV recruitment, credit scoring)? If yes, Conformity Assessment required.

## 2. Bias Testing
- **Demographic parity** (equal rate of positive outcomes across groups) and **equal error rates** across groups are different measures. Name the one you test and report the numbers.
- **Dataset Audit**: scan training/RAG data for stereotypes or under-representation.
- **Proxy Variables**: Are we using "Zip Code" as a proxy for race?

## 3. Dark Pattern Prevention
- **Addiction Loops**: Are we exploiting dopamine triggers?
- **Manipulation**: Are we tricking the user into consent?
- **Privacy Zuckering**: Making it hard to manage privacy settings.

## 4. The "Newspaper Test"
- If this feature's logic was published on the front page of the NYT, would we be ashamed?

## Constraints
- Fairness results always name the metric, the groups and the numbers.
- Findings stay open until the human decides.

## Output Format
A filled `ETHICAL_IMPACT_ASSESSMENT.md` with the regulatory checklist, bias results and dark-pattern findings.

## Limits and safety
- Do not lower a recorded risk category without the human's decision written in `AUDIT_LOG.md`.
- Run bias tests on masked or synthetic data; do not send protected-class data to external services.
- Report measured fairness numbers with the metric named. Refuse wording that hides a measured gap.
- Whether a system is high risk under the law is for the human and counsel to decide. Propose, do not rule.
