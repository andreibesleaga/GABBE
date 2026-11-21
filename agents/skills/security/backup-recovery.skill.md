---
name: backup-recovery
description: Set recovery objectives (RPO, RTO), choose a backup method and run a restore test. Use at S09 to S11 when planning disaster recovery or when checking that backups can be restored.
triggers: [backup, restore test, rpo rto, disaster recovery, point in time recovery]
tags: [security]
role: ops-sre, eng-database
context_cost: low
---
# backup-recovery Skill

## Goal
"A backup is not a backup until you have successfully restored from it."

## Where it fits
Phase and gate: S09 and S10 (a restore test before go-live), S11 (periodic drill), S13 (retention at the end). Evidence: the restore-test log with date and result in `docs/ops/restore-tests.md`.

## Steps
## 1. Define Objectives
- **RPO (Recovery Point Objective)**: Max data loss. (e.g., "1 hour", "5 minutes", "0 seconds").
- **RTO (Recovery Time Objective)**: Max downtime. (e.g., "4 hours", "30 minutes").

## 2. Strategies
- **Point-In-Time Recovery (PITR)**: Archive WAL/Binlogs to replay transactions up to a specific second. (Critical for RPO ~0).
- **Snapshot**: Daily/Hourly full disk copy. Low impact, slower restore.
- **Logical Dump**: `pg_dump` / `mysqldump`. Portable, slow for large data.

## 3. Storage & Retention
- **Immutability**: Backups must be Read-Only (WORM) to prevent Ransomware encryption.
- **Off-site**: Replicate to a different region/cloud provider (3-2-1 Rule).
- **Retention**: Keep Dailies for 7 days, Weeklies for 1 month, Monthlies for 1 year.

## 4. Testing (The Golden Rule)
- **Automated Restore Drill**: Weekly CI job that:
  1. Spins up a fresh DB.
  2. Pulls the latest backup.
  3. Restores it.
  4. Runs integrity check (`SELECT count(*) ...`).
  5. Reports success/failure to Slack.

## Constraints
- RPO and RTO are written down and approved before a method is chosen.
- A backup counts only after a restore test passed.

## Output Format
`docs/ops/restore-tests.md` (date, backup used, result, time taken) and the RPO and RTO values.

## Limits and safety
- Run restore tests into a separate test environment, never over a live database. Cut outbound access where the platform allows it.
- Do not delete, shorten the retention of or overwrite backups. Propose the exact command; run it after the human confirms.
- Leave short-lived secrets (sessions, reset tokens) out of logical dumps. Keep backup keys apart from production keys.
- Restoring production data to a new place needs the human's yes in the request.
- If your platform provides write-once storage, use it for archive backups.
