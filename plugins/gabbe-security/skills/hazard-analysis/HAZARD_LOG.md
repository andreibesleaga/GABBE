# Hazard Log

**System**: [Name]
**Date**: [YYYY-MM-DD]

| ID | Component | Failure Mode | Effect (Severity) | Cause (Probability) | Detection | RPN | Mitigation | Status |
|---|---|---|---|---|---|---|---|---|
| H-001 | LiDAR | No Data Output | Collision Risk (10) | Cable Break (2) | Heartbeat (2) | 40 | Redundant LiDAR | OPEN |
| H-002 | Battery | Thermal Runaway | Fire (10) | Short Circuit (3) | Temp Sensor (3) | 90 | Liquid Cooling | CLOSED |

## Definitions
- **Severity**: 1 (None) to 10 (Catastrophic/Loss of Life).
- **Probability**: 1 (1 in 1M hours) to 10 (Frequent).
- **Risk Class**:
  - High (RPN > 100): Must mitigate.
  - Med (RPN > 50): ALARP (As Low As Reasonably Practicable).
  - Low (RPN < 50): Acceptable.
