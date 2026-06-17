# Self-Healing Loop Summary

The Self-Healing Loop is a core autonomous mechanism in GABBE (detailed in `core/self-heal.skill.md`). It allows agents to diagnose, research, fix, and verify failures autonomously, minimizing human intervention for routine errors.

## Operation Summary

1. **Pre-Healing (Memory Check)**: Before attempting a fix, the agent reads `agents/memory/CONTINUITY.md`. If the error and its resolution are already documented, the agent applies the known fix immediately, preventing repeated failed attempts ("learning").
2. **Safety Check**: The agent ensures it is not in an infinite loop (e.g., trying the exact same fix for the 3rd time, or recursion depth > 10).
3. **Diagnosis & Classification**: The agent classifies the error (Type, Test, Import, Runtime, Build, Unknown).
   - *Autonomous fixes allowed*: Lint/type errors, test assertions (if spec changed), minor version bumps, formatting.
   - *Human escalation required immediately*: Architecture changes, breaking API changes, security changes, major version bumps.
4. **Research (If Unknown)**: The agent invokes `research.skill` to find authoritative solutions (Context-7 MCP or Tavily/Brave Search).
5. **Hypothesize & Fix**: The agent states a hypothesis and applies the *minimal* required change.
6. **Verify & Iterate**: The agent runs tests/builds. If it passes, it logs to `AUDIT_LOG.md`. If it fails, it increments the attempt counter (Max 5 attempts).
7. **Escalation (Attempt 5)**: If 5 attempts fail, autonomous action stops. An escalation report is generated detailing all attempts, research findings, and options for human decision. The task status becomes `BLOCKED`.

## Agent Execution & Verification
This loop is triggered automatically during Phase S05 (Implementation) of Loki mode when the `VERIFY` step (tests, typecheck, lint) fails. Agents are instructed to invoke `self-heal.skill` dynamically before escalating. This ensures that the system is resilient to minor regressions and only bothers the human architect with high-level decisions.

## Refresh: The Loop at a Glance
In short, the capability is a bounded **5-attempt self-heal loop** (diagnose → hypothesize → minimal fix → verify, capped to prevent runaway compute) backed by `self-heal.skill`. In CI it is paired with `ci-autofix.skill`, which applies the same diagnose-and-fix loop to red pipeline runs (lint, type, formatting, simple test breaks). Both honor the same guardrails: a **hardstop** halts autonomous action when an error is classed as high-risk (architecture, security, breaking API, or major version bumps), and **escalation** fires after the 5th failed attempt — generating a report and marking the task `BLOCKED` for human decision rather than guessing further.
