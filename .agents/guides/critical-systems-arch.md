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
*   **Safety Monitor (Deterministic):** Checks limits ($$ G < 4.0 $$, $$ Alt > 500 $$).
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
3.  **Hazard Analysis (FMEA/STPA):**
    *   Agent brainstorms "What if?" scenarios ("What if the GPS sensor sends NaN?").

---

## 4. The "Lethal Trifecta" in Critical Ops
Avoid these three at all costs:
1.  **Unbounded Loops:** Control loops must be deterministic.
2.  **Dynamic Memory Allocation:** Critical C/C++ often forbids `malloc` after init.
3.  **Deadlocks:** Actors/Agents must have proven liveness.

---

## 5. References
*   [DO-178C / ED-12C Software Considerations]
*   [IEC 62304 Medical Device Software]
*   [CAST-32A Multi-Core Processors]
