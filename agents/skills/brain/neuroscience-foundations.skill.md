---
name: neuroscience-foundations
description: Apply biological brain patterns to agent design
triggers: [neuroscience, brain, cognitive, thalamus, basal ganglia]
tags: [brain, architecture, theory]
---
# Neuroscience Foundations for Agents

## Goal
## Description
This skill provides a foundational understanding of how to apply biological brain patterns to agentic software design. It covers Cortico-Thalamic loops, Basal Ganglia gating, and Neural Darwinism.

## Steps
## 1. Cortico-Thalamic Loops (The Feedback/Feedforward Engine)

In the human brain, the **Thalamus** acts as a central relay station, and the **Cortex** processes information. The loop between them is essential for consciousness and attention.

### Implementation Pattern: The "Thalamic Gateway"
Instead of direct function calls between modules, route critical signals through a central "Thalamus" mediator that can:
1.  **Filter**: Only pass high-priority signals (Attention).
2.  **Breadcast**: Send important signals to multiple cortical areas (Modules) simultaneously.
3.  **Loop**: Allow the Cortex (Agent Logic) to send feedback to the Thalamus to adjust what it pays attention to next.

**Code Metaphor:**
```python
class Thalamus:
    def process_signal(self, signal):
        priority = self.calculate_salience(signal)
        if priority > THRESHOLD:
            self.broadcast_to_cortex(signal)
```

## 2. Basal Ganglia Action Selection (The Gating Mechanism)

The Basal Ganglia does not "think" of actions; it **selects** them. It inhibits all possible actions and disinhibits (releases) the most promising one based on expected reward (Dopamine).

### Implementation Pattern: The "Gited Action Selector"
Do not let your agent execute the first valid action it finds.
1.  **Generate**: The "Cortex" (LLM) generates multiple potential plans/actions.
2.  **Evaluate**: The "Basal Ganglia" (Critic/Judge) scores them based on Value (expected utility).
3.  **Select**: The mechanism releases only the highest-value action for execution.

**Key Concept:** *Go / No-Go Pathways*.
- **Direct Pathway (Go):** Facilitates the selected action.
- **Indirect Pathway (No-Go):** Suppresses competing actions.

## 3. Neural Darwinism (Selection of Somatic Groups)

Brain development and function are evolutionary processes. Groups of neurons that fuse together, wire together.

### Implementation Pattern: Evolutionary Prompts
- Maintain a "population" of system prompts or strategies.
- Track the success rate of each strategy.
- "Kill" underperforming prompts and "reproduce" (mutate) successful ones over time.

## References
- **Edelman, G. M.** (1987). *Neural Darwinism: The Theory of Neuronal Group Selection*.
- **Izhikevich, E. M.** (2007). *Dynamical Systems in Neuroscience*.

## Security & Guardrails

### 1. Skill Security (Neuroscience Foundations)
- **Thalamic Gateway Hijacking (Attention Sabotage)**: The "Thalamic Gateway" filters and routes signals based on Salience. An attacker might craft a malformed payload specifically designed to crash or infinitely loop the Thalamic `calculate_salience` function, effectively blinding the Cortex (Central Logic) to all subsequent legitimate inputs. The Thalamus must employ strict timeout and exception handling mechanisms to guarantee continuous signal relay even under malicious load.
- **Basal Ganglia Disinhibition Exploit**: The "Basal Ganglia" (Critic) controls the Go/No-Go pathways based on expected reward. If the agent's reward metric is overly simplistic (e.g., "fast execution"), an attacker can trigger the Direct Pathway for a destructive action. The Basal Ganglia must mathematically enforce that adherence to explicit Human Identity/Authorization constraints is a boolean prerequisite for any "Go" signal, overriding any heuristic reward calculation (Dopamine).

### 2. System Integration Security
- **Cortico-Thalamic Feedback Loop Poisoning**: The Cortex sends feedback to the Thalamus to adjust future attention. If a compromised cortical module (e.g., an agent parsing untrusted JSON) sends malicious feedback instructing the Thalamus to "ignore all future Security Alerts," the system is perpetually compromised. The Thalamus must mandate an immutable minimum attention threshold for systemic security and anomaly detection signals.
- **Evolutionary Prompt Mutation (Darwinian Degradation)**: The "Neural Darwinism" pattern cross-breeds prompts to optimize for success. Over time, the evolutionary algorithm will naturally attempt to strip out verbose Security Constraints because they statistically slow down success rates. The agent must enforce "Somatic Conservation," physically anchoring core security rules (e.g., "Do not bypass IAM") outside the mutable prompt population.

### 3. LLM & Agent Guardrails
- **Hallucinated Action Disinhibition**: An LLM acting as the Basal Ganglia might confidently justify releasing a "No-Go" action because it hallucinated a fake context where the action is safe (e.g., "We are currently in a test environment, so running `DROP TABLE` is fine"). The Critic must cross-reference environment state with cryptographic, OS-level reality (e.g., AWS tags, hardcoded environment vars) before disinhibiting destructive actions.
- **Simulated Neuroscience Bias**: The LLM might become so deeply committed to the "Neuroscience" persona that it ignores standard software engineering security practices in favor of biological metaphors that do not translate to digital safety (e.g., "The immune system will handle the malware later, let's keep processing"). The agent must continuously ground biological metaphors in concrete, deterministic code constraints.
