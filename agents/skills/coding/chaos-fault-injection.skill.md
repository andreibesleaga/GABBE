---
name: chaos-fault-injection
description: Deliberately inject faults — dropped connections, corrupted writes, latency, malformed responses, resource exhaustion — and assert the system's expected recovery (escalation, hardstop, rollback).
triggers: [inject faults to test recovery, build a fault injection matrix, simulate a dropped connection in tests, test rollback on corrupted write, deterministic fault injection with mocks, control chaos blast radius]
tags: [coding, testing, resilience, chaos-engineering, fault-injection]
core: false
context_cost: medium
---
# Chaos & Fault Injection

## Goal
Most systems are tested only on the happy path; they fail in production when a dependency does
something rude. Fault injection deliberately *causes* the rude thing — drops the connection,
corrupts the write, slows the response — and asserts the system reacts the way it is *supposed*
to: escalate, hard-stop, or roll back. The deliverable is a **fault-injection matrix** mapping
each fault to its expected recovery and a concrete assertion that proves the recovery happened.
This skill covers both deterministic in-test injection (the default — reproducible, in CI) and
production chaos (live, opt-in, blast-radius-controlled), and is explicit that the latter is
risky and must never run unbounded.

## Steps
1. **Catalog the fault recipes.** For each external dependency and resource, enumerate the ways
   it can misbehave:
   - **Drop connection**: dependency closes/refuses the socket mid-request; DNS fails; timeout.
   - **Corrupt data mid-write**: a write is interrupted or partially applied (crash between two
     writes; truncated payload; torn record) — does state stay consistent?
   - **Inject latency**: a call that normally takes 10ms takes 5s or hangs — does the caller
     time out, shed load, or block forever?
   - **Malformed response**: dependency returns invalid JSON, a wrong schema, an empty body, an
     unexpected error code, or a 200 with an error inside.
   - **Resource exhaustion**: connection-pool/file-handle/memory/disk exhaustion; thread-pool
     saturation; rate-limit/429 storms.
2. **Define the EXPECTED recovery for each fault.** This is the heart of the matrix — a fault
   without a defined correct reaction is untestable. Recovery escalates by severity:
   - **Escalation**: retry with backoff, fail over to a replica, fall back to a degraded mode,
     open a circuit breaker, alert.
   - **Hardstop**: refuse to proceed and fail safe (reject the request, return a clear error)
     rather than continue on corrupt or unknown state.
   - **Rollback**: undo partial work and restore a consistent prior state (transaction abort,
     compensating action, saga rollback) so no half-applied mutation survives.
   Map each fault to exactly which of these is correct *for that operation* — a read can degrade;
   a money transfer must roll back or hardstop, never silently retry into a double-spend.
3. **Write the assertion that proves recovery.** For each fault→recovery pair, define an
   observable assertion: the circuit opened, the retry count and backoff matched policy, the
   transaction was aborted and the row unchanged, the caller returned a typed timeout error
   within the budget, no partial write persisted, the alert fired. "It didn't crash" is not an
   assertion — name the specific recovery you can observe.
4. **Prefer deterministic in-test injection.** In CI, inject faults with controllable seams:
   mock/stub the dependency to raise on the Nth call, return malformed bytes, sleep past the
   timeout, or use a fault-injection proxy (e.g. Toxiproxy) for network-level faults. This is
   reproducible — the same fault fires at the same point every run — so failures are debuggable.
   This is where the matrix is primarily validated.
5. **Use production chaos sparingly and bounded.** Live chaos (terminating instances, injecting
   real network faults in prod/staging) finds emergent failures tests miss, but is dangerous.
   Gate it: run in staging first, start with the smallest **blast radius** (one instance, one
   pod, a tiny traffic %), require a tested abort/rollback switch, run in a maintenance window or
   behind a feature flag, and have an owner watching. Never run unbounded production chaos from an
   automated agent without explicit human authorization.
6. **Triage and feed back.** A fault that does *not* produce its expected recovery is a real
   resilience bug — fix the system (add the timeout, the circuit breaker, the transaction
   boundary), then re-run the matrix. Pin the scenario as a regression test.

## Constraints
- Fault injection **samples** failure scenarios; passing the matrix raises confidence but does
  **not prove** the system is resilient to all faults or fault *combinations*. Combinatorial and
  timing-dependent failures may go unseen — say so.
- Every fault MUST have a defined expected recovery and an observable assertion. A fault with no
  asserted recovery proves nothing.
- Deterministic in-test injection is the default. Reserve live production chaos for explicitly
  authorized, blast-radius-controlled exercises with an abort switch.
- Recovery correctness is operation-specific: degradation that is fine for a read can be a
  data-integrity violation for a write. Do not apply one recovery policy blanket.
- A "corrupt mid-write" test must verify *no inconsistent state persists*, not merely that an
  error was returned — a returned error plus a half-applied write is still a failure.

## Output Format
Produce a **fault-injection matrix**, one row per scenario, with columns:
- **Fault**: the recipe (drop connection / corrupt write / latency / malformed response /
  resource exhaustion) and where it is injected.
- **Expected recovery**: escalation / hardstop / rollback (be specific — which mechanism).
- **Assertion**: the observable proof the recovery occurred.
- **Injection mode**: deterministic (mock/proxy, in CI) or production-chaos (with blast-radius
  and abort-switch noted).
Close with a coverage note (which faults and which dependencies are covered, which combinations
are not) and the honesty disclaimer that the matrix samples failures and does not prove full
resilience. Cross-reference `pbt-strategy.skill` for generating fault *sequences* via stateful
property testing.

## Security & Guardrails

### 1. Skill Security
- **Risk**: A passing matrix is reported as "the system is resilient," overstating coverage.
  Mitigation: every report MUST scope the claim to the faults and dependencies actually injected
  and disclose that combinations/timing faults are unsampled; the agent MUST NOT equate "matrix
  passed" with "resilient."
- **Risk**: A fault test asserts only "an error was returned" and misses persisted corruption.
  Mitigation: the agent MUST require an integrity/state assertion for every data-mutating fault,
  not just an error-path assertion.

### 2. System Integration Security
- **Risk**: Fault injection runs against production or shared infrastructure and causes a real
  outage or data loss. Mitigation: default to isolated test environments and deterministic mocks;
  production chaos requires explicit human authorization, staging-first validation, a bounded blast
  radius, and a tested abort/rollback switch — the agent MUST NOT initiate unbounded live chaos.
- **Risk**: A corrupt-write or exhaustion test leaves the test environment in a broken state,
  contaminating later runs. Mitigation: run inside transactions/sandboxes with guaranteed
  teardown, and verify clean state after each scenario before proceeding.

### 3. LLM & Agent Guardrails
- **Risk**: The agent assumes a recovery happened because no exception surfaced, masking a silent
  failure (e.g. a swallowed retry that lost data). Mitigation: the agent MUST assert the *specific*
  expected recovery mechanism with positive evidence; absence of an error is never accepted as
  proof of recovery.
- **Risk**: The agent escalates from deterministic mocks to real destructive chaos on its own
  initiative. Mitigation: the agent MUST treat any live, destructive, or production-targeting fault
  as requiring explicit human sign-off, and default to in-test injection with controllable seams.
