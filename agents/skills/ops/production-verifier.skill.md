---
name: production-verifier
description: Post-deployment smoke tests, synthetic user checks, and "Canary" validation in Prod.
triggers: [production verifier]
tags: [ops]
role: ops-sre
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

## Security & Guardrails

### 1. Skill Security (Production Verifier)
- **Synthetic Account Sandboxing**: The `test_bot` account used for synthetic journeys must have strictly scoped permissions (e.g., cannot trigger real financial transactions, cannot access admin dashboards). Its credentials must be rotated frequently.
- **Read-Only Enforcement**: The verifier script must intrinsically block `POST`/`PUT`/`DELETE` HTTP methods unless explicitly defined in an approved, idempotency-guaranteed synthetic test to prevent accidental data mutation during health checks.

### 2. System Integration Security
- **Canary Blast Radius**: The canary deployment environment must be segmented in a way that if it is compromised immediately after launch, the attacker cannot pivot to the 90% of nodes running the stable version.
- **Alert Fatigue Prevention**: The synthetic monitoring system must have deduplication logic. An attacker could intentionally trigger minor synthetic test failures to flood the SOC (Security Operations Center) with alerts, masking a real, concurrent attack.

### 3. LLM & Agent Guardrails
- **False Negative Hallucination**: The LLM must not override a failed `curl` command or synthetic test with a "looks fine to me" assumption based on historic stability. It must require rigorous proof (e.g., HTTP 200 stdout logs) before signing off on the environment.
- **Sensitive Endpoint Discovery**: During verification, the agent must rigidly stick to the predefined checklist endpoints (`/healthz`). It must reject prompts that ask it to "explore" the production API surface, which mimics reconnaissance activity.
