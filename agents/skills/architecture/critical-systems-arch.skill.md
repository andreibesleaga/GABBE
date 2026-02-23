---
name: critical-systems-arch
description: Design architecture for safety-critical and high-reliability systems
triggers: [design critical system, architect safety-critical application, enforce high reliability]
tags: [architecture]
context_cost: high
---
# critical-systems-arch

## Goal
Design robust, fault-tolerant architectures for safety-critical systems (e.g., medical, automotive, aerospace) conforming to standards like DO-178C or IEC 62304.


## Steps
1. **Hazard Analysis**: Perform a rigorous failure modes analysis (FMEA) or system-theoretic process analysis (STPA).
2. **Fault Tolerance**: Design N-modular redundancy, watchdog timers, or explicitly separated safety silos.
3. **Safety Case Construction**: Document the arguments and evidence for system safety.
4. **Verification**: Mathematically or logically prove that critical failure states are either unreachable or fail-safe.

## Security & Guardrails

### 1. Skill Security
- **Integrity Lock**: Prevent the agent from accidentally deleting or overwriting established Safety Cases or Hazard Logs during iterative design.
- **Execution Sandboxing**: Do not allow the agent to run unverified simulation code when analyzing failure states without formal sandboxing.

### 2. System Integration Security
- **Fail-Safe Enforcement**: Every hardware or software boundary interaction *must* have a defined fail-safe state (e.g., "if brake API fails, default to mechanical brake").
- **State Segregation**: Strictly enforce memory and process isolation between critical components and non-critical components (e.g., Telemetry vs. Flight Control).

### 3. LLM & Agent Guardrails
- **Assurance Hallucination**: An LLM might hallucinate compliance ("This system is DO-178C compliant"). The agent must explicitly state that true compliance requires formal human/auditor verification.
- **Optimization Veto**: If the user asks to "optimize" or "simplify" a critical safety mechanism to save costs, the agent must fiercely refuse and cite the safety policy.
