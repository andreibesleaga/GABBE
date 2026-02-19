---
name: epistemology-knowledge
description: Implement rigorous knowledge representation and update beliefs via Active Inference
triggers: [knowledge, epistemology, active inference, belief, truth]
tags: [brain, theory, reasoning]
---

# Epistemology & Knowledge Representation

## Description
This skill explores how agents "know" things, how they represent beliefs, and how they should update those beliefs using Active Inference and rigorous Epistemology.

## 1. Knowledge Representation (Ontologies & Graphs)

**Core Idea:** Knowledge is not just text embeddings; it is structured relationships between entities.

### Implementation Pattern: Knowledge Graph Augmentation
- Don't just rely on vector similarity search (RAG).
- Maintain a structured **Knowledge Graph (KG)** (Nodes = Entities, Edges = Relations).
- **Hybrid Retrieval**: Combine Vector Search (semantic similarity) with Graph Traversal (logical connection).

**Example:**
*Query: "What causes System Failure?"*
- **Vector Search**: Finds docs mentioning "crash", "bug".
- **Graph Search**: Traverses `System Failure` <- `caused_by` - `Memory Leak`.

## 2. Active Inference (The Free Energy Principle)

**Core Idea:** Agents act to minimize **Surprise** (Variational Free Energy). Surprise is the difference between the Agent's *Expectation* and its *Sensation*.

### Implementation Pattern: Prediction Error Minimization
The agent is not just maximizing a reward function; it is trying to align its internal model with external reality.
1.  **Predict**: Agent predicts the next observation based on its Model.
2.  **Act / Sense**: Agent acts and observes the actual outcome.
3.  **Update**:
    - If `Observation != Prediction` (Surprise!):
        - **Update Model**: Change beliefs (Perceptual Learning).
        - **Change World**: Act to make the world match the prediction (Active Inference).

**Code Metaphor:**
```python
class ActiveInferenceAgent:
    def step(self, observation):
        prediction = self.model.predict(self.state)
        error = measure_surprise(prediction, observation)
        
        if error > TOLERANCE:
            # Option A: Change Model
            self.model.update(observation)
            
            # Option B: Act to fix world
            action = self.planner.plan_to_reduce_error(target=prediction)
            return action
        return None # "All is well"
```

## 3. Epistemic vs. Pragmatic Actions

**Core Idea:** Distinguish between actions that *change the world* (Pragmatic) and actions that *change the agent's knowledge* (Epistemic).

### Implementation Pattern: Exploration Bonuses
- **Pragmatic Action**: "Click the 'Submit' button" (Achieves goal).
- **Epistemic Action**: "Read the error logs" (Reduces uncertainty).
- **Strategy**: When Uncertainty is high, prioritize Epistemic Actions. When Uncertainty is low, prioritize Pragmatic Actions.

## References
- **Friston, K.** (2010). *The Free-Energy Principle: A Unified Brain Theory?*
- **Pearl, J.** (2009). *Causality: Models, Reasoning, and Inference*.
