---
name: hazard-analysis
description: Conducting FMEA (Failure Mode & Effects Analysis) and identifying hazards.
role: prod-safety-engineer
triggers:
  - fmea
  - hazop
  - hazard analysis
  - stpa
  - risk assessment
---

# hazard-analysis Skill

This skill identifies how the system can fail and what happens when it does.

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
