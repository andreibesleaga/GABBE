# Bug Report: [Brief Title]
<!-- Fill before using debug.skill — helps agent understand and reproduce the bug -->
<!-- Created: [date] | Reported by: [name] -->

---

## Summary

**One-line description:** [What is broken in plain language]

**Severity:** Critical | High | Medium | Low

**Impact:** [Who is affected, how often, what the business impact is]

**Environment:**
```
OS:           [Linux / macOS / Windows + version]
Browser:      [Chrome 120 / Firefox 121 / N/A]
Node/PHP/etc: [runtime version]
App version:  [git commit hash or release tag]
Database:     [PostgreSQL 16 / MySQL 8 / etc]
```

---

## Steps to Reproduce

<!-- Be specific — a bug that can't be reproduced can't be fixed -->

1. [Starting state: "Given a user is logged in as role X"]
2. [Action: "When they navigate to /settings/profile"]
3. [Action: "And they click 'Save Changes' without modifying any field"]
4. [Observed: "Then they see a 500 Internal Server Error"]

**Minimum reproduction:** [The fewest steps to see the bug]

**Is it reproducible?** [Always / Intermittently (estimate %) / Rare / Only once]

**Reproduction rate (if intermittent):** [Approximately X out of Y tries]

---

## Expected Behavior

[What should have happened? Be specific.]

Example: "Clicking 'Save Changes' with unchanged data should return 200 OK and display 'No changes saved' message."

---

## Actual Behavior

[What actually happens? Include exact error messages, HTTP status codes, UI state.]

Example: "API returns HTTP 500 with body: `{ "error": "Cannot read properties of undefined (reading 'email')" }`"

---

## Error Messages & Stack Trace

```
[Paste full error message and stack trace here]

Example:
TypeError: Cannot read properties of undefined (reading 'email')
    at UserController.update (/app/src/adapters/http/user.controller.ts:45:22)
    at Layer.handle [as handle_request] (/app/node_modules/express/lib/router/layer.js:95:5)
```

---

## Logs

```
[Relevant log lines from application or server logs]
[Include timestamps if available]
```

---

## Screenshots / Videos

[If UI bug: link to screenshot or screen recording]
[If API bug: include request/response from browser DevTools or Postman]

**API Request:**
```
POST /api/v1/users/123 HTTP/1.1
Authorization: Bearer [token]
Content-Type: application/json

{}
```

**API Response:**
```
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{ "error": "Internal server error" }
```

---

## Hypothesis (Initial Guess)

[Your initial hypothesis about what's causing the bug — even if uncertain]

Example: "Suspect the save handler doesn't check for empty body before accessing `body.email`"

---

## Context

**Related code:** [file path and line number if known]
**Related PR/commit:** [link if you know when this was introduced]
**Regression?** [Did this work before? When did it stop working?]
**Workaround?** [Is there a temporary workaround users can use?]

---

## Definition of Fixed

<!-- What exact behavior will confirm this bug is resolved? -->

- [ ] [Specific test that must pass]
- [ ] [Specific behavior that must work]
- [ ] [No regressions in related functionality]

---

## Assignment

**Assigned to:** [agent / human developer]
**Priority:** [P1 (immediate) / P2 (this sprint) / P3 (backlog)]
**Labels:** [ui, api, database, performance, security]
