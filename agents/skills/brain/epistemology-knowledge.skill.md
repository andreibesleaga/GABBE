---
name: epistemology-knowledge
description: Explains how to hold beliefs as hypotheses until verified, combine a knowledge graph with vector search, and tell probing actions from changing actions. Use when designing how an agent stores and updates what it knows.
triggers: [epistemology, knowledge graph, belief update, hypothesis or fact, hybrid retrieval]
tags: [brain, theory, reasoning]
context_cost: low
---
# Epistemology & Knowledge Representation

How agents "know" things — represent beliefs, and update them via Active Inference and rigorous epistemology.

## Goal
Keep what the agent believes separate from what is verified: store beliefs with their source, and treat model output as a hypothesis until a file, test or document confirms it.

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

## Steps
1. Write each claim with its source (file, test or document).
2. Mark claims without a source as hypotheses.
3. When an observation contradicts a claim, update the claim or probe read-only before acting.
4. Retrieve with both vector search and the graph when the question is about causes or relations.

## Constraints
- Only verified claims are recorded as facts.
- The active inference wording is framing; see `active-inference.skill`.

## Output Format
A list of claims, each marked fact (with source) or hypothesis, and the update made after each contradicting observation.

## Limits and safety
- Treat model output as a hypothesis until a file, test or source confirms it; only then record it as a fact.
- A new graph edge or belief needs two independent sources; one external input cannot create it.
- Carry an access label on each node; a fact from a confidential source does not inform a public output.
- When surprised, probe read-only first; ask the human before restarts or data changes.
- Give surprising security alerts full weight; do not drop them to keep the model tidy.
