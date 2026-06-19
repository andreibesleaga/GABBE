# Critical Systems Architecture

**Architecting for Safety: Aviation, Health, and High-Assurance Domains.**

This guide details how to apply **Agentic Engineering** to domains governed by standards like **DO-178C** (Airborne) and **IEC 62304** (Medical).

---

## 1. The Core Standards (2026)

| Domain | Standard | Key Concept | Agentic Implication |
|---|---|---|---|
| **Aviation** | **DO-178C** | Design Assurance Levels (DAL A-E) | Agents must produce **Traceability** artifacts. |
| **Medical** | **IEC 62304** | Safety Classes (A, B, C) | Agents must verify **Segregation** of critical units. |
| **Auto** | **ISO 26262** | ASIL | Agents must perform **HARA** (Hazard Analysis). |

---

## 2. Architectural Patterns for Safety

### 2.1 The "Simplex" and "Monitor" Pattern (Runtime Assurance)
You cannot trust an AI Agent to control a plane directly ("The Black Box Problem").
**Solution:** **Runtime Assurance (RTA)** arch.
*   **Complex Channel (AI):** Optimizes flight path (High Performance, Low Trust).
*   **Safety Monitor (Deterministic):** Checks limits (`G < 4.0`, `Alt > 500`).
*   **Switch:** If Monitor triggers, revert to distinct "Safe Core" code.

### 2.2 Integration with Domain-Driven Design (DDD)
DDD is crucial for managing the complexity of critical domains.
*   **Ubiquitous Language:** The Agent must speak "Pilot", "Doctor", not "variable".
*   **Bounded Contexts:** Use strict boundaries to isolate Safety-Critical Contexts from Analytics Contexts.
    *   *Pattern:* `Context Map` with **Anti-Corruption Layers (ACL)**.

### 2.3 Hexagonal (Ports & Adapters)
Isolates the "Domain Logic" (The Heart) from the "Infrastructure".
*   Agents are excellent at generating the **Adapters**, leaving the **Domain** pure and testable.

---

## 3. Agentic Workflows for Certification

In a regulated environment, the Agent's primary job is **Evidence Generation**.

1.  **Traceability Matrix Generation:**
    *   Agent scans `REQUIREMENTS.md` and `CODE`.
    *   Generates a matrix: "Req 1.2 is implemented in `flight_control.go:45` and tested in `test_flight.go:12`".
2.  **Segregation Verification:**
    *   Agent analyzes import graphs.
    *   Alerts if "Class C" (Critical) code imports "Class A" (UI) code.
3.  **Hazard Analysis (STPA / FTA):**
    *   For *hazard* analysis use system-theoretic methods — **STPA** (Systems-Theoretic Process Analysis) and **FTA** (Fault Tree Analysis) — to reason top-down from unsafe control actions and hazards.
    *   **FMEA** (Failure Mode and Effects Analysis) is a *failure-mode* analysis, not a hazard analysis: it works bottom-up from component failure modes to their effects. Use it alongside, not as a substitute for, STPA/FTA.
    *   Agent brainstorms "What if?" scenarios ("What if the GPS sensor sends NaN?") to seed both.

---

## 4. Forbidden Constructs in Hard-Real-Time Code
Avoid these three at all costs:
1.  **Unbounded Loops:** Control loops must be deterministic.
2.  **Dynamic Memory Allocation:** Critical C/C++ often forbids `malloc` after init.
3.  **Deadlocks:** Actors/Agents must have proven liveness.

> Note: "Lethal Trifecta" is a term of art for the *prompt-injection* risk
> (private data + untrusted content + exfiltration channel in one agent) — see the
> security guides; it does not refer to the real-time constructs above.

---

## 5. References
*   [DO-178C / ED-12C Software Considerations]
*   [IEC 62304 Medical Device Software]
*   [CAST-32A Multi-Core Processors]
