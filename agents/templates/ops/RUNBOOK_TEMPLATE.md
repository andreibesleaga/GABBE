# Runbook: [Alert / Scenario Name]

**Date:** [YYYY-MM-DD]
**Owner:** [team or on-call rotation]
**Last validated:** [YYYY-MM-DD]
**Status:** Draft | Active

<!-- A runbook is for a tired on-call engineer at 3am. Every step must be
     copy-pasteable, unambiguous, and safe. Prefer commands over prose. -->

---

## 1. At a Glance

| Field | Value |
|---|---|
| Alert name | [Exact alert/monitor name as it fires] |
| Severity | [SEV1 / SEV2 / SEV3] |
| Service | [Affected service] |
| Owning team | [ ] |

**Symptom:** [What the alert is actually telling you, in plain language.]

**Impact / blast radius:** [Who and what is affected? e.g. "All checkout requests fail; ~X% of revenue at risk."]

---

## 2. Diagnosis

<!-- Numbered, copy-pasteable. Each step should narrow down the cause. -->

1. Confirm the alert is real (not flapping):
   ```
   [command to check current state]
   ```
2. Check upstream dependency health:
   ```
   [command]
   ```
3. Inspect recent deploys/changes:
   ```
   [command]
   ```
4. Check error logs:
   ```
   [command]
   ```

**Decision point:** [How to tell which remediation path applies.]

---

## 3. Remediation

> Choose the path matching your diagnosis.

**Path A — [cause]:**
```
[step-by-step commands]
```

**Path B — [cause]:**
```
[step-by-step commands]
```

---

## 4. Rollback

<!-- The safe undo. When in doubt, roll back first, investigate later. -->
```
[exact rollback command(s)]
```
**Rollback verification:** [How to confirm the rollback took effect.]

---

## 5. Escalation Path

| Level | Who | Contact | When to escalate |
|---|---|---|---|
| L1 | [Primary on-call] | [channel/page] | [ ] |
| L2 | [Service owner] | [ ] | [If not resolved in N min] |
| L3 | [Eng lead / incident commander] | [ ] | [SEV1 / data loss] |

---

## 6. Verification (Resolved)

- [ ] Alert cleared and stays cleared for [N] minutes.
- [ ] Key metric back within SLO: [metric + bound].
- [ ] No new related errors in logs.
- [ ] Incident notes recorded; follow-up ticket filed if needed.

---

## 7. Related Dashboards & Links

- **Dashboard:** [name — where to find it]
- **SLO / metric:** [name]
- **Related runbooks:** [name only]
- **Architecture / ADR:** [reference by name or ADR number]
