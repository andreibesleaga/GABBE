---
name: hazard-analysis
description: "Run FMEA and STPA on a safety-relevant design and fill the hazard log. Use when failure could harm people or assets, or before approving safety-critical requirements."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/security/hazard-analysis.skill.md"
  tags: "security"
  core: "false"
  context_cost: "low"
---
# hazard-analysis Skill

## Goal
This skill identifies how the system can fail and what happens when it does.

## Where it fits
Phase and gate: S01 (hazards become requirements), S02 (design controls), S07 (review). Lead: prod-safety-engineer. Evidence: the filled hazard log, copied to `docs/safety/HAZARD_LOG.md`. A tier 3 trigger in `security-baseline.skill.md`.

## Steps
## 1. FMEA (Failure Mode & Effects Analysis)
- **Component**: [Name]
- **Failure Mode**: How does it fail? (e.g., "Stuck Open", "No Output", "Corrupt Data").
- **Effect**: What is the impact? (e.g., "Engine overheats").
- **Severity**: 1-10 (10 = Catastrophic/Death).
- **Probability**: 1-10 (10 = Certain).
- **Detection**: 1-10 (10 = Undetectable).
- **RPN (Risk Priority Number)**: Sev * Prob * Det.

## 2. STPA (System-Theoretic Process Analysis)
- Focus on *control* loops rather than component failures.
- **Unsafe Control Actions (UCA)**:
  - Not providing a control action when needed.
  - Providing a control action when not needed.
  - Providing a control action too early/late.
  - Stopped too soon or applied too long.

## 3. Hazard Identification Checklist
- **Energy**: High voltage, pressure, heat?
- **Timing**: Latency, jitter, race conditions?
- **Data**: Corruption, stale data, NaN/Infinity?
- **Interface**: Mismatched units (Metric vs Imperial)?

## 4. Output
- Populate `templates/security/HAZARD_LOG.md`.

## Constraints
- Every hazard gets a severity, a cause and a control, or stays open.
- Run FMEA for components and STPA for control loops; say which was used.

## Output Format
The filled hazard log (`templates/security/HAZARD_LOG.md`) with FMEA rows, unsafe control actions and open hazards.

## Limits and safety
- This is an engineering aid. For a regulated safety system a qualified safety engineer reviews the log. Never state that a system "is safe".
- Severity and probability scores are proposals for the human to confirm. Never lower a severity to reduce the RPN.
- A hazard with no mitigation stays open in the log and in the open risks.
