---
name: production-verifier
description: "Verify a live deploy with read-only smoke checks, a 10% canary on error rate, p95 and business metrics, and a scripted browser journey. Use right after a production deploy, or to decide on a rollback. Use when: verify production deploy, post-deploy smoke test, canary validation, synthetic monitoring journey, should we roll back, healthz check."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/ops/production-verifier.skill.md"
  tags: "ops"
  core: "false"
  context_cost: "low"
---
# production-verifier Skill

## Goal
This skill verifies the system *after* it has crossed the finish line.

## Steps
## 1. Safety First
- **Read-Only**: Production tests should mostly be read-only (GET /health, GET /user).
- **Test User**: If writing, use a specific `test_bot` user account. Do NOT delete real data.

## 2. Canary Validation
1.  Deploy to 10% of traffic.
2.  Check Error Rate (5xx).
3.  Check Latency (p95).
4.  Check Business Metrics (Orders/sec).
5.  If variance > 5% from Baseline -> **Rollback**.

## 3. Synthetic Monitoring
- Create a scripted browser journey (Playwright) that runs every 5 mins.
- "Login -> Search 'Apple' -> Verify Result".
- If this fails, page the on-call engineer.

## 4. Verification Checklist
- [ ] `/healthz` endpoint returns 200 OK.
- [ ] Database is reachable.
- [ ] Cache is reachable.
- [ ] CDN is serving assets.
- [ ] SSL Certificate is valid.

## Constraints
- Checks come from the written list; do not explore other production endpoints.
- A check passes only with output you saw (status code, metric value); do not assume from past stability.

## Output Format
A verification record in the release notes or `AUDIT_LOG.md`: each check, command, result, time, and the decision (keep or roll back).

## Limits and safety
- Production checks are read-only; a write check uses the dedicated `test_bot` account with narrow rights and never touches real data.
- Block POST, PUT and DELETE in the verifier script unless an approved test names them.
- If a check fails, propose the rollback command; run it only after the human confirms or the approved plan says so.
- Do not call a failed check fine because earlier deploys were stable; show the passing output.
- Deduplicate synthetic-monitor alerts so a repeated failure pages once.
