---
name: req-review
description: Systematic review of existing requirements documents for quality, completeness, consistency, and alignment. Applies IEEE 29148 / ISO 25010 quality criteria and EARS compliance. Produces a structured review report with gap list and recommendations.
triggers: [review requirements, audit requirements, check requirements, requirements quality, are requirements complete, requirements analysis, requirements gap, existing requirements]
context_cost: medium
---

# Requirements Review Skill

## Goal

Assess the quality of an existing requirements document (PRD, SRS, user stories, feature
spec) using formal criteria. Identify gaps, inconsistencies, ambiguities, and missing
stakeholder concerns. Produce a structured review report with actionable findings.

---

## When to Use

- **Scenario 2 (Review existing)**: Requirements already exist — PRD, SRS, user stories, feature descriptions, or any natural-language specification.
- **Before architecture**: Verify requirements are complete before designing a system.
- **Before implementation**: Gate check to catch gaps before code is written (cheaper to fix here).
- **After requirements update**: Re-review whenever requirements change significantly.

---

## Step 1 — Load and Parse Requirements

```
1. Identify the requirements artifact(s):
   - What format? (PRD.md, user stories, SRS, informal description, Confluence page)
   - What scope? (full system, single feature, subsystem)
   - What version/date? (are these current?)

2. Extract all requirement statements:
   - Identify every "shall", "must", "should", "will" statement
   - Identify all acceptance criteria
   - Identify all listed non-functional requirements

3. Identify what's missing before reading content:
   - Is there a stakeholder list?
   - Is there scope definition (in-scope/out-of-scope)?
   - Is there a priority or MoSCoW classification?
   - Are requirements numbered/identified?
```

---

## Step 2 — IEEE Quality Criteria Assessment

```
Evaluate each requirement and the requirements document as a whole against 8 criteria:

1. CORRECT
   Each requirement states a real need (no gold-plating or undefined gold standards).
   Verify: "Does this requirement come from a real stakeholder need?"
   Fail signs: Requirements invented by developers, requirements that solve implementation problems

2. COMPLETE
   All functional, quality, and constraint requirements are present.
   Verify: "Is there anything the system needs to do that isn't captured?"
   Fail signs: Missing error paths, missing admin functions, missing non-functional specs

3. CONSISTENT
   No two requirements contradict each other.
   Verify: "Do any requirements conflict in behavior, priority, or resource use?"
   Fail signs: FR-002 requires encryption but CON-007 requires plaintext logging

4. UNAMBIGUOUS
   Each requirement has exactly one interpretation.
   Verify: "Could two people read this differently?"
   Ambiguity patterns (flag every occurrence):
     - Subjective terms: fast, user-friendly, secure, robust, easy, flexible
     - Vague scope: "appropriate", "as needed", "if necessary", "may"
     - Incomplete comparatives: "better", "improved", "more"
     - Undefined references: "the user" (which user?), "the data" (what data?)

5. TESTABLE (VERIFIABLE)
   Each requirement can be verified by test, inspection, analysis, or demonstration.
   Verify: "Could an independent tester write a pass/fail test for this?"
   Fail signs: "The system shall be user-friendly" (how measured?),
               "The system shall handle high load" (how much?)

6. FEASIBLE
   Each requirement is technically and economically achievable within constraints.
   Verify: "Is this achievable given budget, timeline, and technology?"
   Flag: Requirements that appear technically infeasible — escalate to human

7. NECESSARY
   Each requirement is actually needed (not nice-to-have presented as mandatory).
   Verify: "What happens if this requirement is dropped? Would stakeholders object?"
   Flag: Requirements that appear to be implementation decisions, not true requirements

8. TRACEABLE
   Each requirement can be traced to a stakeholder need or higher-level goal.
   Verify: "Why does this requirement exist? Who asked for it?"
   Fail signs: Orphan requirements with no stakeholder connection

Score each criterion: GREEN (meets criteria) / YELLOW (partial/concern) / RED (fails)
```

---

## Step 3 — EARS Compliance Check

```
For each formal requirement statement, check EARS pattern compliance:

  ✓ Uses correct EARS keyword (WHEN/WHILE/WHERE/IF/none for ubiquitous)
  ✓ Contains exactly one "shall"
  ✓ Subject is the system (not "the user shall", not "the admin will")
  ✓ Single behavior per statement (no "and" joining two behaviors)
  ✓ No technology named (implementation-agnostic)
  ✓ Measurable — quantified where needed

EARS conversion examples:
  BAD:  "Users should be able to log in quickly"
  GOOD: "WHEN an authenticated user submits valid credentials,
         the system SHALL issue a session token within 500ms."

  BAD:  "The system should handle errors"
  GOOD: "IF an upstream service is unavailable,
         THEN the system SHALL return a 503 response with a retry-after header."

Flag all non-compliant requirements with conversion suggestions.
```

---

## Step 4 — Coverage Analysis

```
Check for MISSING requirement categories:

Functional coverage checklist:
  □ All user roles have documented interactions
  □ All data creation/read/update/delete operations specified
  □ All error and exception paths specified
  □ All integration points (external systems, APIs) specified
  □ All authentication and authorization flows specified
  □ All notifications and communications specified
  □ System startup/shutdown behavior specified
  □ Data migration or initial population specified (if applicable)
  □ Audit/logging requirements specified
  □ Reporting and monitoring requirements specified

Quality attribute coverage:
  □ Performance targets (response time, throughput, capacity)
  □ Availability and reliability targets
  □ Security requirements (authentication, authorization, encryption)
  □ Usability requirements (accessibility, learnability)
  □ Maintainability/operability requirements
  □ Interoperability requirements (if system integrates externally)

Constraint coverage:
  □ Technical constraints documented
  □ Regulatory constraints documented
  □ Resource constraints (budget, time, personnel) documented
  □ Legal/licensing constraints documented
```

---

## Step 5 — Consistency Cross-Check

```
Build a simple consistency matrix:
  For each pair of related requirements:
  - Do they make compatible assumptions about data?
  - Do they make compatible assumptions about system state?
  - Do they make compatible resource demands?

Common consistency errors to check:
  □ Two requirements describe the same behavior differently
  □ Priority conflicts: A "MUST" requires resource that a "SHOULD" assumes doesn't exist
  □ Timing conflicts: Two things claimed to happen simultaneously that can't
  □ Security vs usability conflicts: Security requirement vs accessibility requirement
  □ Data conflicts: One req says field is required, another treats it as optional

Document each conflict found — list the conflicting FR IDs and the nature of conflict.
```

---

## Step 6 — Traceability Verification

```
Verify bidirectional traceability:

Forward traceability (source → requirement):
  Every requirement traces to a stakeholder/goal/use case.
  Orphan requirements (no source) = suspect, flag for review.

Backward traceability (requirement → verification):
  Every requirement has an identified verification method.
  Possible methods: test, inspection, analysis, demonstration.
  Requirements without verification method = untestable, flag.

If traceability matrix exists:
  Verify completeness: no blank cells
  Verify correctness: cited links actually match

If traceability matrix doesn't exist:
  Create a basic one and populate as much as possible.
  Identify gaps where source is unknown.
```

---

## Output Format

Fill `templates/product/REQUIREMENTS_REVIEW_TEMPLATE.md`, producing:

```markdown
# Requirements Review Report

**Document reviewed**: [name, version, date]
**Review date**: [YYYY-MM-DD]
**Reviewer**: [agent/human]
**Scope**: [feature/system/subsystem]

## Executive Summary
Overall quality: GREEN / YELLOW / RED
[2-3 sentence summary]

## Quality Criteria Scores
| Criterion | Score | Issues Found |
|-----------|-------|--------------|
| Correct | GREEN/YELLOW/RED | [N issues] |
| Complete | GREEN/YELLOW/RED | [N issues] |
| Consistent | GREEN/YELLOW/RED | [N issues] |
| Unambiguous | GREEN/YELLOW/RED | [N issues] |
| Testable | GREEN/YELLOW/RED | [N issues] |
| Feasible | GREEN/YELLOW/RED | [N issues] |
| Necessary | GREEN/YELLOW/RED | [N issues] |
| Traceable | GREEN/YELLOW/RED | [N issues] |

## Critical Findings (must fix before proceeding)
[Finding ID] | [FR-NNN] | [Criterion violated] | [Description] | [Recommendation]

## Minor Findings (should fix)
...

## Coverage Gaps (missing requirements)
[List of functional areas with no requirements coverage]

## Recommendations
1. [Specific action item]
2. [Specific action item]

## Approval Gate
[ ] All CRITICAL findings resolved → Proceed to architecture
[ ] YELLOW findings documented with rationale → Acceptable to proceed
[ ] Traceability matrix created
```

---

## Constraints

- Never approve requirements with RED on Testable or Complete criteria
- All CRITICAL findings must be resolved or explicitly accepted by human before design begins
- Do not suggest implementation solutions — only flag requirement quality issues
- Ambiguity that you cannot resolve requires direct human clarification — do not guess intent
- If requirements are described in natural language without structure, still apply all 8 criteria — scoring will reflect the informal format
