---
name: epistemology-knowledge
description: Implement rigorous knowledge representation and update beliefs via Active Inference
triggers: [knowledge, epistemology, active inference, belief, truth]
tags: [brain, theory, reasoning]
context_cost: low
---
# Epistemology & Knowledge Representation

How agents "know" things — represent beliefs, and update them via Active Inference and rigorous epistemology.

## 1. Knowledge Representation (Ontologies & Graphs)
Knowledge is structured relationships between entities, not just text embeddings.

**Knowledge Graph Augmentation:** maintain a structured **Knowledge Graph** (nodes = entities, edges = relations). Don't rely on vector similarity (RAG) alone — use **hybrid retrieval**: vector search (semantic) + graph traversal (logical).

*Query "What causes System Failure?"*: vector finds docs mentioning "crash"/"bug"; graph traverses `System Failure <-caused_by- Memory Leak`.

## 2. Active Inference (The Free Energy Principle)
Agents act to minimize **Surprise** (Variational Free Energy) = gap between *expectation* and *sensation*. Goal isn't maximizing reward but aligning the internal model with reality.

**Prediction Error Minimization:** (1) predict next observation from model; (2) act/sense actual outcome; (3) on surprise (`obs != prediction`), either **update model** (perceptual learning) or **change world** to match prediction (active inference).

```python
class ActiveInferenceAgent:
    def step(self, observation):
        prediction = self.model.predict(self.state)
        error = measure_surprise(prediction, observation)
        if error > TOLERANCE:
            self.model.update(observation)                       # A: change model
            return self.planner.plan_to_reduce_error(target=prediction)  # B: act to fix world
        return None  # all is well
```

## 3. Epistemic vs. Pragmatic Actions
Distinguish actions that *change the world* (pragmatic, e.g. "click Submit") from those that *change the agent's knowledge* (epistemic, e.g. "read the error logs" → reduce uncertainty). High uncertainty → prioritize epistemic; low uncertainty → prioritize pragmatic.

## References
- Friston, K. (2010). *The Free-Energy Principle: A Unified Brain Theory?*
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*.

## Security & Guardrails

### 1. Skill Security (Epistemology & Knowledge)
- **Ontological Poisoning**: the KG is the agent's absolute truth; a single injected false edge (e.g. `Input_Validation <-is_deprecated_by- Web_Agent`) makes it bypass security controls. Require strict threshold-based consensus (multiple verified sources) before external input can forge a new structural edge.
- **Active Inference Exploitation (Pragmatic Sabotage)**: an attacker who knows the agent minimizes Surprise can trigger cascading errors so the agent takes extreme pragmatic actions (restart nodes, drop DBs) to stabilize. Hard-cap the impact radius of pragmatic actions taken under high-Surprise.

### 2. System Integration Security
- **RAG/Vector Data Segregation**: respect data isolation when mixing vector + graph; a fact from a "Confidential" subgraph must not inform actions/updates in a "Public" space. Carry access-control metadata at the node level.
- **Epistemic Action Disclosure**: exploration tests boundaries — "read all of `/etc`" behaves like malware. Bind the epistemic planner to an OS-level sandbox (restricted container) to physically limit curiosity.

### 3. LLM & Agent Guardrails
- **Truth vs. Probability Hallucination**: LLMs output statistical probability, not truth. Don't accept raw LLM output as a Belief unless it survives `ActiveInferenceAgent.step()` verification; flag unverified outputs as *hypotheses*, never *facts*.
- **Confirmation Bias in Model Updates**: when updating its model, the LLM may overweight observations matching priors and down-weight surprising security alerts. Mathematically force processing of high-surprise observations so "uncomfortable" data isn't ignored to keep Free Energy artificially low.
