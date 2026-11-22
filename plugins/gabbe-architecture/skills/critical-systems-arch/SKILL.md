---
name: critical-systems-arch
description: "Architecture for safety-critical systems — hazard analysis, fault tolerance, fail-safe states and a safety case outline. Use when failure could harm people or assets (medical, automotive, aerospace) and the design must follow DO-178C or IEC 62304."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/critical-systems-arch.skill.md"
  tags: "architecture"
  core: "false"
  context_cost: "high"
---
# critical-systems-arch

## Goal
Design robust, fault-tolerant architectures for safety-critical systems (e.g., medical, automotive, aerospace) conforming to standards like DO-178C or IEC 62304.

## Steps
1. **Hazard Analysis**: Perform a rigorous failure modes analysis (FMEA) or system-theoretic process analysis (STPA).
2. **Fault Tolerance**: Design N-modular redundancy, watchdog timers, or explicitly separated safety silos.
3. **Safety Case Construction**: Document the arguments and evidence for system safety.
4. **Verification**: Mathematically or logically prove that critical failure states are either unreachable or fail-safe.

## Constraints
- Every boundary has a fail-safe state.
- Critical and non-critical components share no memory or process.

## Output Format
The hazard analysis (FMEA or STPA), the fault-tolerance design and the safety case outline, as Markdown files in the project's docs folder.

## Limits and safety
- Never overwrite or delete a safety case or hazard log: write a new version and keep the old.
- Run simulation or analysis code only in a throwaway environment, never connected to real devices.
- Every hardware or software boundary has a defined fail-safe state; critical and non-critical components are isolated.
- Never write that a design "complies" with DO-178C or IEC 62304; list the evidence that exists and leave compliance to an independent assessor.
- Do not weaken a safety mechanism to save cost or complexity; ask the human and cite the policy.
