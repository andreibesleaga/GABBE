---
name: reliability-engineering
description: Design failover, redundancy and stability patterns, and compute availability from MTBF and MTTR. Use when a requirement sets an availability target or when one failure must not stop the service.
triggers: [reliability engineering, redundancy, failover, availability target, mtbf, circuit breaker, five nines]
tags: [security]
role: prod-safety-engineer, prod-architect
context_cost: low
---
# reliability-engineering Skill

## Goal
This skill designs systems that continue to function in the presence of faults.

## Where it fits
Phase and gate: S02 (design), S06 (tests), S09 (failover test in staging). Lead: prod-safety-engineer. Evidence: the calculation with its assumptions in `docs/architecture/`.

## Steps
## 1. Redundancy Patterns
- **Active/Passive (Hot Standby)**: Primary handles load, Secondary takes over on heartbeat loss.
- **Active/Active (Load Balancing)**: Both handle load. System survives if N-1 nodes active.
- **TMR (Triple Modular Redundancy)**: 3 voters. 2/3 majority wins. Used in avionics/space.

## 2. Design for Reliability
- **Watchdog Timers**: Hardware/Software timer that resets the system if it hangs.
- **Safety Bag / Monitor**: Independent channel that monitors outputs and cuts power if limits exceeded.
- **N-Version Programming**: 3 teams write the same software in 3 languages (Python, Rust, Ada) to avoid common bugs.

## 3. Calculations
- **MTBF (Mean Time Between Failures)**: Total Time / Number of Failures. Use for **repairable** systems (the model used throughout this skill).
- **MTTF (Mean Time To Failure)**: the analogous metric for **non-repairable** components (you replace, not repair); MTBF ≈ MTTF + MTTR.
- **Availability**: MTBF / (MTBF + MTTR). Goal: 99.999% ("Five Nines" = 5 mins downtime/year).
- **Failure Rate ($\lambda$)**: 1 / MTBF.

## 4. Stability Patterns
- **Circuit Breaker**: Stop calling a failing service to prevent cascading failure.
- **Bulkhead**: Isolate components so a crash in one doesn't sink the ship.
- **Backpressure**: Reject new work when overloaded.

## Constraints
- State the failure assumptions behind each availability number.
- Each redundancy pattern has a test that shows the failover works.

## Output Format
The pattern chosen per component, the availability calculation with its assumptions, and the failover test result.

## Limits and safety
- The numbers are estimates from stated assumptions. Write the assumptions down. Never present an availability figure as a guarantee.
- Run failover and fault-injection tests in staging or test. In production only with the human's yes in the request.
- N-version programming is costly. State the cost and ask the human before proposing it.
