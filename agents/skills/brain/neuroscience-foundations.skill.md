---
name: neuroscience-foundations
description: Apply biological brain patterns to agent design
triggers: [neuroscience, brain, cognitive, thalamus, basal ganglia]
tags: [brain, architecture, theory]
context_cost: low
---
# Neuroscience Foundations for Agents

Apply biological brain patterns to agentic software design: Cortico-Thalamic loops, Basal Ganglia gating, Neural Darwinism.

## 1. Cortico-Thalamic Loops (Feedback/Feedforward Engine)
The **Thalamus** is a central relay; the **Cortex** processes. Their loop drives consciousness and attention.

**Thalamic Gateway:** route critical signals through a central mediator instead of direct module-to-module calls. It (1) **filters** — pass only high-priority signals (attention); (2) **broadcasts** important signals to many cortical modules at once; (3) **loops** — lets the Cortex (agent logic) feed back to adjust future attention.

```python
class Thalamus:
    def process_signal(self, signal):
        if self.calculate_salience(signal) > THRESHOLD:
            self.broadcast_to_cortex(signal)
```

## 2. Basal Ganglia Action Selection (Gating)
The Basal Ganglia doesn't think of actions — it **selects** them, inhibiting all options and disinhibiting the most promising one by expected reward (dopamine).

**Gated Action Selector:** don't execute the first valid action. (1) Cortex (LLM) **generates** multiple plans; (2) Basal Ganglia (critic/judge) **evaluates** by expected utility; (3) **selects**/releases only the highest-value action.

**Go / No-Go pathways:** Direct (Go) facilitates the selected action; Indirect (No-Go) suppresses competitors.

## 3. Neural Darwinism (Selection of Somatic Groups)
Brain function is evolutionary — neurons that fire together, wire together.

**Evolutionary Prompts:** keep a population of system prompts/strategies, track each one's success rate, kill underperformers and mutate (reproduce) winners over time.

## References
- Edelman, G. M. (1987). *Neural Darwinism: The Theory of Neuronal Group Selection*.
- Izhikevich, E. M. (2007). *Dynamical Systems in Neuroscience*.

## Security & Guardrails

### 1. Skill Security (Neuroscience Foundations)
- **Thalamic Gateway Hijacking (Attention Sabotage)**: a malformed payload could crash or infinitely loop `calculate_salience`, blinding the Cortex to all later legitimate inputs. Enforce strict timeout and exception handling so signal relay continues under malicious load.
- **Basal Ganglia Disinhibition Exploit**: an overly simple reward metric (e.g. "fast execution") lets an attacker trigger the Direct Pathway for a destructive action. Make adherence to explicit Human Identity/Authorization a boolean prerequisite for any "Go", overriding heuristic reward.

### 2. System Integration Security
- **Cortico-Thalamic Feedback Loop Poisoning**: a compromised cortical module could feed back "ignore all future Security Alerts," perpetually compromising the system. Mandate an immutable minimum attention threshold for security/anomaly signals.
- **Evolutionary Prompt Mutation (Darwinian Degradation)**: mutation will naturally strip verbose security constraints that slow success rates. Enforce "Somatic Conservation" — anchor core security rules (e.g. "Do not bypass IAM") outside the mutable prompt population.

### 3. LLM & Agent Guardrails
- **Hallucinated Action Disinhibition**: the LLM-as-Basal-Ganglia might release a No-Go action by hallucinating a safe context ("we're in test, so `DROP TABLE` is fine"). Cross-reference environment state with cryptographic OS-level reality (AWS tags, hardcoded env vars) before disinhibiting destructive actions.
- **Simulated Neuroscience Bias**: the LLM may overcommit to the neuroscience persona and ignore real security practice for biological metaphors ("the immune system will handle the malware later"). Continuously ground metaphors in concrete, deterministic code constraints.
