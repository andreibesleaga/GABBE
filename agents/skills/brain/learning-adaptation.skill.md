---
name: learning-adaptation
description: Mechanisms for In-Context Reinforcement Learning, Meta-Learning, and Neuroplasticity.
triggers: [learning adaptation]
tags: [brain]
context_cost: high
tools: [replace_file_content, write_to_file]
---
# Learning & Adaptation Skill

## Goal
> "Neurons that fire together, wire together." (Hebbian Learning)

## Steps
## 1. Synaptic Plasticity (Rewiring)
This skill allows the system to "rewire" itself based on experience.
- **Potentiation (Strengthening):** If a prompt/tool works well, save it to a "Best Practices" bank.
- **Depression (Weakening):** If a tool fails often, add a warning or deprecate it.

## 2. Meta-Learning (Learning to Learn)
The agent should not just learn *information*; it should learn *strategies*.

### Strategy Reflection Loop
After a task is complete, perform a "Post-Mortem":
1.  **Observation:** "I hallucinated a library name."
2.  **Hypothesis:** "I didn't check the docs first."
3.  **New Rule:** ("ALWAYS check docs for library imports.")
4.  **Storage:** Save to `system_rules.md`.

## 3. Reinforcement Learning (RL) Integration
- **Actor:** The Agent performing the task.
- **Critic:** A separate module (or human) that scores the outcome (Reward).
- **Policy Update:** Update the **Few-Shot Context**.
    - *Old:* Zero-shot prompt.
    - *New:* Prompt + 3 Successful Examples from `learning-adaptation` bank.

## 4. Episodic Consolidation (Dreaming)
Biological brains consolidate short-term memories into long-term structures during sleep.

### Implementation: The "Nightly Build"
1.  **Compress:** Run a summarization job on the day's logs.
2.  **Extract:** Extract key facts and successful code patterns.
3.  **Consolidate:** Update the Knowledge Graph and clear the raw logs.

## References
- **Sutton, R. S., & Barto, A. G.** (2018). *Reinforcement Learning: An Introduction*.
- **Hebb, D. O.** (1949). *The Organization of Behavior*.

## Security & Guardrails

### 1. Skill Security (Learning & Adaptation)
- **Malicious Hebbian Wiring**: If an attacker continuously forces the agent to interact with a vulnerable code pattern, "Hebbian Learning" (Step 1) might inadvertently strengthen the agent's reliance on that insecure pattern, mistaking frequency for correctness. The agent must ensure that "Potentiation" (saving to Best Practices) requires a cryptographic signature or explicit human validation for core security flows.
- **System Rule Corruption**: The "Strategy Reflection Loop" (Step 2) culminates in writing new constraints to `system_rules.md`. An attacker who compromises the agent's observation capabilities could trick the agent into inducing a rule like "Never use HTTPS for internal requests." The agent must mandate that `system_rules.md` is strictly additive and that new rules physically cannot contradict explicit, hardcoded constitutional security laws.

### 2. System Integration Security
- **Critic Compromise in RL**: In the Reinforcement Learning loop (Step 3), the "Critic" scores the outcome. If the Critic relies on easily spoofable metrics (like "Did the code compile?" or "Did the tests pass without error?"), an attacker can feed malicious code that compiles perfectly, securing a high "Reward." The Critic MUST integrate systemic security scanners (SAST/DAST) into its reward function.
- **Consolidation Data Leakage**: The "Nightly Build" (Step 4) compresses logs into long-term structures. These logs often capture highly sensitive tokens or temporary PII used during the day's operations. The compression and extraction algorithms must be coupled with an aggressive Data Loss Prevention (DLP) sanitization pass, ensuring no ephemeral secrets are permanently etched into the Knowledge Graph.

### 3. LLM & Agent Guardrails
- **Over-Fitting to the Context Window**: Meta-Learning algorithms implemented entirely within an LLM's context window are prone to catastrophic interference (forgetting old, safe rules when learning new, dangerous ones). The agent must anchor its "Few-Shot Context" (Step 3) to an external, rigorously audited Vector Database to ensure historical safety precedents are never arbitrarily evicted from memory.
- **Hallucinated Causality in Post-Mortems**: During the Reflection Loop, the LLM might hallucinate the root cause of a failure (e.g., blaming a network timeout when the actual cause was a SQL injection payload crashing the DB). If the agent learns a strategy based on a hallucinated cause, it will actively generate blind spots. Root cause extraction must be strictly grounded in system stack-traces and audit trails.
