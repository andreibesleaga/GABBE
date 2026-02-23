---
name: systems-thinking
description: Analyze complex systems, feedback loops, and leverage points. Avoid linear thinking for complex problems.
triggers: [systems thinking, causal loop, feedback loop, leverage point, root cause, system map, holism, iceberg model]
tags: [product]
context_cost: medium
---
# Systems Thinking Skill

## Goal
To understand the system as a whole, specifically focusing on relationships, feedback loops, and delays, rather than looking at isolated parts. Use this when solving stubborn, recurring problems or designing robust architectures.

## Steps

1.  **The Iceberg Model Analysis**
    *   **Events (React):** What just happened? (The bug/incident)
    *   **Patterns (Anticipate):** What trends have been happening over time?
    *   **Structures (Design):** What influenced the patterns? (Architecture, Org chart, Incentives)
    *   **Mental Models (Transform):** What assumptions/beliefs keep the system in place?

2.  **Causal Loop Diagramming (CLD)**
    *   Identify variables (e.g., "Code Quality", "Velocity", "Tech Debt").
    *   Map relationships (S = Same direction, O = Opposite direction).
    *   Identify Loops:
        *   **Reinforcing (R):** Exponential growth/collapse (Virtuous/Vicious cycles).
        *   **Balancing (B):** Goal-seeking/Stabilizing.
    *   *Output:* Mermaid diagram or text-based CLD.

3.  **Identify Leverage Points**
    *   Where is the intervention point with the highest impact?
    *   Examples: Changing a buffer size (Low leverage) vs Changing the goal of the system (High leverage).

4.  **Archetype Matching**
    *   Does this match a known system trap?
    *   *Examples:* "Fixes that Fail", "Shifting the Burden", "Tragedy of the Commons", "Drifting Goals".

## Output Format
A strategic analysis document at `docs/strategic/SYSTEM_ANALYSIS.md` containing the Iceberg analyis and Causal Loop Diagrams.

## Constraints
*   Look for circular causality, not linear (A causes B, but B also influences A).
*   Watch out for *delays* in the system—they cause oscillation.

## Security & Guardrails

### 1. Skill Security (Systems Thinking)
- **Adversarial Iceberg Mapping**: When encountering a security incident, the agent must adapt the "Iceberg Model" to analyze attacker incentives. (e.g., Structure: "The architecture relies entirely on perimeter defense." Mental Model: "Internal networks are inherently trusted.")
- **Holistic Threat Analysis**: The agent must map the security dependencies of the entire supply chain. A Causal Loop Diagram (CLD) analyzing feature velocity must natively incorporate "Tech Debt" and "Security Debt" as variables that exponentially degrade system stability over time.

### 2. System Integration Security
- **Leverage Point Exploitation**: When the agent identifies a "High Leverage" intervention point in the system map (e.g., changing the core authentication flow), it must automatically flag this node as a highly critical security boundary requiring prioritized threat modeling.
- **Feedback Loop Sabotage**: The agent must analyze balancing loops (e.g., automated rate-limiting, autoscaling) for theoretical manipulation. Can an attacker exploit the autoscaler (a balancing loop) to cause a Denial of Wallet attack, transforming it into a vicious reinforcing loop?

### 3. LLM & Agent Guardrails
- **Analysis Paralysis Defense**: Systems thinking can lead to infinitely expanding scopes. The LLM must enforce a strict boundary condition on the system map to prevent consuming excessive tokens or generating unactionable, overly philosophical theories that stall the SDLC.
- **Hallucinated Causality**: The agent must explicitly state when a causal link in the CLD is a hypothesis vs. an empirically proven fact. The LLM cannot invent causal relationships (e.g., "Implementing Feature X directly caused a 50% drop in vulnerabilities") without citing telemetry or historical PR metrics.
