# Tech Debt Backlog
<!-- Maintained by: tech-debt.skill | Updated: [date] -->
<!-- Priority: P1 (High Impact + Low Effort) | P2 (High Impact + High Effort) | P3 (Low + Low) | P4 (Low + High) -->

---

## Active Debt Items

### TD-[NNN]: [Short Title]

**Debt ID:** TD-[NNN]
**Type:** Code | Test | Architecture | Security | Dependency | Documentation
**Location:** `[file path]:[line number]`
**Detected:** [date] by [tech-debt.skill / code review / etc]
**Status:** OPEN | IN_PROGRESS | RESOLVED

**Description:**
[What is the debt? What is wrong with the current implementation?]

**Why it's debt:**
[What principle or best practice is being violated?
e.g., "Cyclomatic complexity is 18 — exceeds limit of 10.
Makes the function hard to test and modify."]

**Impact** (H/M/L): [H]
[How does this debt slow down development or create risk?
e.g., "Blocks all team members trying to add payment features.
Any change to this function causes unexpected failures."]

**Effort to fix** (H/M/L): [L]
[How much work is required to resolve this debt?
e.g., "Extract 3 validation functions — ~2 hours of focused work."]

**Priority:** P[1/2/3/4]
[P1 = High Impact + Low Effort | P2 = High Impact + High Effort
 P3 = Low Impact + Low Effort  | P4 = Low Impact + High Effort]

**Proposed fix:**
[Concrete approach to resolving this debt item]

```
Example:
1. Extract validateEmail() from UserController.update()
2. Extract validateAge() from UserController.update()
3. Extract validatePhone() from UserController.update()
4. Update tests to cover each extracted function independently
```

**Acceptance criteria:**
- [ ] [Cyclomatic complexity of target function drops below 10]
- [ ] [All existing tests still pass]
- [ ] [New unit tests for each extracted function]
- [ ] [No new circular dependencies]

**Related PR/commit:** [link when resolved]

---

## Resolved Debt Items

| ID | Title | Type | Resolved Date | PR/Commit |
|---|---|---|---|---|
| TD-001 | [Example: Extracted UserValidator from Controller] | Code | [date] | [link] |

---

## Debt Backlog Summary

| Priority | Count | Total Effort |
|---|---|---|
| P1 (Do now) | [0] | [0h] |
| P2 (Plan next sprint) | [0] | [0d] |
| P3 (Good first issues) | [0] | [0h] |
| P4 (Deprioritize) | [0] | — |

---

## Debt Metrics

| Metric | Current | Target | Trend |
|---|---|---|---|
| Cyclomatic complexity (max) | [X] | < 10 | [improving/stable/worsening] |
| Test coverage | [X]% | > 96% | [improving/stable/worsening] |
| Code duplication | [X]% | < 3% | [improving/stable/worsening] |
| TODO/FIXME count | [X] | 0 untracked | [improving/stable/worsening] |
| Outdated major deps | [X] | 0 | [improving/stable/worsening] |

*Last measured: [date]*

---

## Adding New Debt Items

Run `tech-debt.skill` to automatically scan and populate new entries.
Or add manually using the template above.

**Manual entry guidelines:**
1. Assign next sequential ID (TD-[next number])
2. Choose the most specific Type
3. Score Impact AND Effort honestly (not everything is high impact)
4. Propose a concrete fix (not "just refactor it")
5. Define testable acceptance criteria
