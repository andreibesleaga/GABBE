# System Traceability Matrix

**Project**: [Project Name]
**Last Updated**: [YYYY-MM-DD]

| Req ID | Requirement Summary | Priority | Design Component | Implementation File(s) | Test Case ID | Status |
|---|---|---|---|---|---|---|
| REQ-001 | User must be able to login via Email/Pass | High | AuthController | `src/auth/login.ts` | `TEST-AUTH-001` | ✅ Pass |
| REQ-002 | Password must be hashed (bcrypt) | Critical | AuthMiddleware | `src/auth/utils.ts` | `TEST-AUTH-002` | ⚠️ WIP |
| REQ-003 | Failed login attempts > 5 locks account | Medium | RateLimiter | `src/middleware/rate-limit.ts` | *Missing* | ❌ Fail |

## Legend
-   **Req ID**: Unique identifier from PRD.
-   **Status**:
    -   ✅ Pass: Implemented & Verified.
    -   ⚠️ WIP: In Progress.
    -   ❌ Fail: Implemented but failing verification.
    -   ⚪ Pending: Not started.
