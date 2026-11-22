---
name: neuroscience-foundations
description: "Describes thalamic gating, basal-ganglia action selection and prompt-population selection as design analogies. Use when you want a named analogy for routing signals, choosing among candidate plans or evolving prompts."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/brain/neuroscience-foundations.skill.md"
  tags: "brain, architecture, theory"
  core: "false"
  context_cost: "low"
---
# Neuroscience Foundations for Agents

Apply biological brain patterns to agentic software design: Cortico-Thalamic loops, Basal Ganglia gating, Neural Darwinism.

## Goal
Offer three named analogies for agent design (a signal filter, a gated action selector, a population of prompts). They are analogies, not evidence about how agents work.

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

## Steps
1. Decide which design question you have: filtering signals, choosing among plans, or improving prompts.
2. Take the matching analogy (thalamic gateway, gated action selector, prompt population).
3. Write it as concrete instructions or code with a limit, and test it with `cognitive-testing.skill`.

## Constraints
- State that the analogy is a design aid; do not use it as an argument that the design is safe.
- No safety control may rest on the analogy.

## Output Format
A short design note: the question, the analogy chosen, the concrete rule or code, and its limit.

## Limits and safety
- This is analogy only; no safety control rests on it.
- A destructive action needs the human's yes; a high expected-reward score does not release it.
- Security and anomaly signals keep a minimum priority whatever the salience score says.
- Keep the core rules (access control, no bypass of checks) outside the prompts you rank or mutate.
- Before deciding "this is only a test", check the environment (branch, host, variables); never infer it from a story.
