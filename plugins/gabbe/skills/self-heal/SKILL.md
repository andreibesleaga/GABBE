---
name: self-heal
description: "Runs a bounded diagnose, research, fix, verify loop with a 5-attempt cap and a written escalation report. Use when a test, build or command fails and the cause is not yet known."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/self-heal.skill.md"
  tags: "core"
  core: "true"
  context_cost: "medium"
---
# Self-Heal Skill

## Goal
When an agent encounters a failure, autonomously diagnose, research (if needed), fix, and verify — escalating to human only after exhausting all autonomous options (max 5 attempts).

## Self-Healing Loop

```
FAIL detected
  -> Attempt 1: Diagnose error type
  -> Apply fix
  -> Verify
  -> PASS? Done (log to AUDIT_LOG.md)
  -> FAIL? Attempt 2...
  -> ...
  -> Attempt 5 fails? ESCALATE TO HUMAN (stop all action)
```

### Stop-condition precedence (whichever trips FIRST wins)
These are not three competing caps — they are layered tripwires; STOP and escalate as
soon as any one fires:
1. **Repeated-fix tripwire (tightest):** about to apply the **same fix a 3rd time** → STOP
   immediately. Re-trying an identical fix is wasted budget; don't burn the remaining attempts.
2. **Attempt cap (headline):** **max 5 distinct attempts** per task. Each attempt must try a
   *different* hypothesis (the tripwire above prevents 5 reruns of one fix).
3. **Recursion-depth ceiling (defensive backstop):** if nested/recursive self-heal invocations
   exceed **depth 10** → STOP. This guards against runaway re-entry even if the per-task counter
   is somehow bypassed; in normal operation attempt-cap (5) or the repeated-fix tripwire fires long first.
On any STOP → human escalation (below).

## Steps

### Pre-Healing: Check CONTINUITY.md (Dynamic Optimization)
Before starting, read `agents/memory/CONTINUITY.md`:
- Has this exact error or approach been tried before?
- If yes: **STOP**. Apply the recorded solution directly (skip re-discovery).
- If no: proceed with diagnosis. This allows the system to "learn" from past mistakes dynamically.

### Per-Attempt Procedure

0. **Safety Check (Loop Avoidance)** — apply the *Stop-condition precedence* above:
   - Check `production-health.skill.md` rules.
   - About to apply the same fix a 3rd time? -> **STOP** (repeated-fix tripwire).
   - Attempt counter already at 5? -> **STOP** (attempt cap).
   - Recursion depth > 10? -> **STOP** (defensive backstop).

1. **Diagnose the error**
   - Read the full error message and stack trace
   - Classify the error type:
     - **Known error** (in CONTINUITY.md) → apply past solution
     - **Type error** → fix types without changing logic
     - **Test failure** → determine: is test wrong (false positive) OR implementation wrong?
     - **Import/dependency error** → check package installed, correct version
     - **Runtime error** → check data shape, null guards, async/await
     - **Build error** → check syntax, missing exports, circular imports
     - **Unknown error** → invoke research.skill

2. **Classify: automation vs human decision**

   **Agents may self-heal autonomously:**
   - Type errors and lint errors
   - Test assertion updates (when behavior spec changed, not logic)
   - Deprecated API calls (verified via Context-7 MCP)
   - Import path corrections
   - Missing await on async calls
   - Patch/minor version dependency bumps
   - Formatting issues

   **Requires human decision (STOP immediately):**
   - Architecture or library changes
   - Breaking API changes
   - Security-affecting changes
   - Major version dependency bumps
   - Any change to CONSTITUTION.md
   - Unknown error after research finds no solution

3. **Research if needed (for unknown errors)**
   - Invoke research.skill with the error message + library version
   - Check Context-7 MCP for library-specific error patterns
   - Check GitHub issues for the library (via GitHub MCP)
   - If past-knowledge (knowledge cutoff) might be wrong: research current version

4. **Hypothesize and implement fix**
   - State the hypothesis explicitly before fixing
   - Apply the MINIMAL change needed to fix the error
   - Do not refactor or improve other code during self-heal

5. **Verify**
   - Run the failing test/build
   - Run the full test suite (must not introduce regressions)
   - If PASS: log to AUDIT_LOG.md and done
   - If FAIL: increment attempt counter, go to next attempt with new hypothesis

### On Attempt 5 Failure: Human Escalation

Stop ALL autonomous action. Create escalation report:

```markdown
## ESCALATION REQUIRED

**Error:** [exact error message]

**Context:** [what was being implemented when this occurred]

**Attempt 1:**
- Hypothesis: [what I thought the cause was]
- Fix tried: [what I changed]
- Result: [how it failed]

**Attempt 2:** [same format]
**Attempt 3:** [same format]
**Attempt 4:** [same format]
**Attempt 5:** [same format]

**Research Findings:**
[what authoritative sources say about this error, if anything]

**Options for human decision:**
1. [option A] — [what this would mean]
2. [option B] — [what this would mean]

**Recommended:** [option X because Y]

**Awaiting:** Your decision on which option to proceed with.
```

Then:
- Write escalation to AUDIT_LOG.md (action type: HUMAN_ESCALATION)
- Update task in project/TASKS.md → status: BLOCKED
- Do nothing else until human responds

### After Resolution
Once human provides direction:
- Record the resolution in CONTINUITY.md (to prevent future repetition)
- Apply the human-approved fix
- Verify all tests pass
- Update AUDIT_LOG.md with resolution

## Constraints
- Maximum 5 autonomous attempts before escalation — never exceed this
- Never change architecture or library during self-heal (these require human approval)
- Always check CONTINUITY.md first (prevents repeating known failed approaches)
- Escalation report must be complete and specific — vague reports delay resolution

## Output Format
Either: "SELF-HEALED — fixed on attempt [N]. All tests passing." OR "ESCALATION REQUIRED — [report]"

## Cost & Permission Gating
Self-healing is bounded by `GABBE_AUTONOMY` + budget (AGENTS.md §8, Article X):
- **Cost-aware retries:** each attempt costs tokens. Try the cheapest diagnosis→fix path first; do not escalate to expensive reasoning or SOTA models for a simple lint/type fix. If a fix genuinely needs an expensive approach, **ask first** (hybrid *and* auto pause for expensive/SOTA/irreversible).
- **Protected files:** never edit build/IaC/CI/dependency manifests during a heal loop unless the failure is specifically dependency/build-related and within the §8 allowlist — otherwise escalate.
- **Bounded loop = cost ceiling:** the 5-attempt cap also caps spend; on exhaustion STOP and escalate rather than burning budget.
- **Persist around each attempt:** refresh `RESUME_POINTER.md` and append to `AUDIT_LOG.md` (`state-preserve.skill`) so a cutoff mid-heal is recoverable.
- **Misaligned-replay guard:** learn only from the *successful* fix; never feed a failed attempt back as a pattern to repeat (`update-scan.skill`).

## Limits and safety
- Edit only the file or module that failed. Build files, IaC, CI config and dependency manifests are off limits unless the failure is a dependency or build failure inside the AGENTS.md section 8 allowlist.
- Stop and write the escalation report at the same fix a third time, at the fifth attempt, or at recursion depth 10.
- Never fix a failure by deleting or weakening a test, switching off a lint or security check, changing file permissions, or disabling authentication or CSRF. These are not valid hypotheses.
- A fix that downgrades a dependency needs the human's yes (it may bring back a known vulnerability).
- Try speculative fixes where a failure cannot hurt data (a branch, a test database). If your platform provides a sandbox, use it.
