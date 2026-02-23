---
name: reliability-engineering
description: Designing failover patterns (Hot Standby, TMR), redundancy, and MTTF calculations.
triggers: [reliability engineering]
tags: [security]
role: prod-safety-engineer, eng-arch
---
# reliability-engineering Skill

## Goal
This skill designs systems that continue to function in the presence of faults.

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
- **MTBF (Mean Time Between Failures)**: Total Time / Number of Failures.
- **Availability**: MTBF / (MTBF + MTTR). Goal: 99.999% ("Five Nines" = 5 mins downtime/year).
- **Failure Rate ($\lambda$)**: 1 / MTBF.

## 4. Stability Patterns
- **Circuit Breaker**: Stop calling a failing service to prevent cascading failure.
- **Bulkhead**: Isolate components so a crash in one doesn't sink the ship.
- **Backpressure**: Reject new work when overloaded.

## Security & Guardrails

### 1. Skill Security (Reliability Engineering)
- **Failover State Tampering**: The logic governing the "Heartbeat Loss" in Active/Passive setups is highly sensitive. The agent must mandate that the failover orchestration system requires cryptographically signed heartbeats. If a malicious actor can spoof a "node dead" message, they can force the system into a continuous, thrashing failover state (a localized DoS).
- **Watchdog Integrity**: The agent must specify that Software Watchdog Timers operate at a higher ring/privilege level than the application they monitor. An application compromised by an attacker or locked in an infinite loop must not be able to indefinitely suspend or disable its own Watchdog timer.

### 2. System Integration Security
- **Circuit Breaker Data Leakage**: When a Circuit Breaker trips and rejects new work, the fallback response (e.g., an HTTP 503 error) must be strictly sanitized. The agent must verify that the fallback mechanism does not inadvertently leak internal stack traces, database states, or backend IP addresses to the client during the failure mode.
- **Redundancy as an Attack Vector**: If the architecture uses N-Version Programming (multiple teams writing the same software to avoid common bugs), the agent must ensure strict network and IAM isolation between the N versions. If a single Zero Day exploits `Version A`, the architecture must guarantee the attacker cannot pivot to compromise `Version B`.

### 3. LLM & Agent Guardrails
- **MTBF Hallucination**: The LLM must not invent arbitrary "Five Nines" (99.999%) availability guarantees for proposed architectures without mathematically backing up the assertion with the combined failure rates ($\lambda$) of the underlying cloud provider SLAs and dependent services.
- **Cost vs. Reliability Bias**: A user might prompt the agent: "We need 100% uptime for this blog, design an Active/Active multi-region Kubernetes cluster." The agent must act as a rational guardrail. While technically possible, the agent must highlight the extreme cost and complexity for a non-critical workload and suggest a static S3 bucket instead, prioritizing pragmatic architectural security over over-engineering.
