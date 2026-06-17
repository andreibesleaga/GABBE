# Decommission / Sunset Plan: [Service / Product Name]

**Date:** [YYYY-MM-DD]
**Owner:** [name or team]
**Approver:** [name]
**Status:** Draft | Approved | In progress | Complete

<!-- Sunsetting is a project, not an afterthought. Plan the wind-down with the
     same rigor as a launch. Communicate early; remove last. -->

---

## 1. Summary

**What is being decommissioned:** [System and its scope.]
**Why:** [Reason — replaced by X / low usage / cost / risk.]
**Replacement (if any):** [Where users go instead.]

---

## 2. Deprecation Timeline

| Milestone | Date | Notes |
|---|---|---|
| Announce deprecation | [YYYY-MM-DD] | [Public/internal] |
| Feature freeze (no new signups) | [ ] | [ ] |
| Migration window opens | [ ] | [ ] |
| Read-only / degraded mode | [ ] | [ ] |
| Hard shutdown | [ ] | [ ] |
| Final teardown | [ ] | [ ] |

---

## 3. Affected Users & Communications

| Audience | Count / segment | First notice | Reminder cadence | Channel | Owner |
|---|---|---|---|---|---|
| [internal teams] | [ ] | [ ] | [e.g. T-90, T-30, T-7, T-1] | [ ] | [ ] |
| [external customers] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 4. Data: Retention, Migration, Export

| Data set | Owner | Action (migrate/export/delete) | Destination / format | Deadline |
|---|---|---|---|---|
| [ ] | [ ] | [ ] | [ ] | [ ] |

**Self-serve export:** [How users get their own data out before shutdown.]
**Retention obligations:** [Legal/compliance minimums that override deletion.]

---

## 5. Archival

- [ ] Code repository archived (read-only) at [location].
- [ ] Final data snapshot stored at [location], retention [period].
- [ ] Documentation / runbooks archived.
- [ ] Configuration & secrets recorded then revoked.

---

## 6. License / Contract Wind-Down

| Item | Vendor / counterparty | Action | Notice required | Deadline | Owner |
|---|---|---|---|---|---|
| [SaaS subscription] | [ ] | [cancel/downgrade] | [e.g. 30d] | [ ] | [ ] |
| [domain / cert] | [ ] | [ ] | [ ] | [ ] | [ ] |

---

## 7. Traffic Drain Steps

<!-- Drain gradually so problems surface while rollback is still possible. -->

1. Redirect [X]% of traffic to replacement / error page: `[command]`
2. Lower DNS TTL ahead of cutover: `[command]`
3. Increase drain to 100%; keep service warm for rollback: `[command]`
4. Disable inbound; monitor for stragglers: `[command]`

---

## 8. Final Teardown Checklist

- [ ] All traffic drained; zero live requests for [N] days.
- [ ] Compute / containers stopped and deleted.
- [ ] Databases snapshotted, then deprovisioned.
- [ ] DNS records removed.
- [ ] Secrets / API keys / IAM roles revoked.
- [ ] Monitoring, alerts, and on-call rotation removed.
- [ ] Billing confirmed stopped.
- [ ] Index/registry entries pointing at this service removed.

---

## 9. Post-Sunset Verification

- [ ] No traffic or errors observed in [N] days post-teardown.
- [ ] No orphaned cloud resources still billing (cost report checked).
- [ ] No broken references in dependent systems.
- [ ] Stakeholders notified of completion.
- [ ] Lessons recorded for future decommissions.
