---
name: epistemology-knowledge
description: Implement rigorous knowledge representation and update beliefs via Active Inference
triggers: [knowledge, epistemology, active inference, belief, truth]
tags: [brain, theory, reasoning]
---
# Epistemology & Knowledge Representation

## Goal
## Description
This skill explores how agents "know" things, how they represent beliefs, and how they should update those beliefs using Active Inference and rigorous Epistemology.

## Steps
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

## Security & Guardrails

### 1. Skill Security (Epistemology & Knowledge)
- **Ontological Poisoning**: The Knowledge Graph (KG) represents the agent's absolute truth. If an attacker can inject a false relational edge (e.g., `Input_Validation` <- `is_deprecated_by` <- `Web_Agent`), the agent will systematically bypass security controls. The agent must require strict, threshold-based consensus (e.g., multiple verified sources) before an external input is allowed to forge a new structural edge in the KG.
- **Active Inference Exploitation (Pragmatic Sabotage)**: If an attacker understands the agent minimizes "Surprise," they can intentionally trigger cascading errors in a target system to generate massive Surprise. The agent might then take extreme "Pragmatic Actions" (Step 2) to stabilize the environment (e.g., restarting cluster nodes, dropping databases). The agent must hard-cap the impact radius of Pragmatic Actions taken under high-Surprise conditions.

### 2. System Integration Security
- **RAG/Vector Data Segregation**: When mixing Vector Search with Graph Traversal (Step 1), the agent must respect systemic data isolation bounds. If the agent retrieves a fact from a "Confidential" subgraph, it must not use that fact to inform actions or updates in a "Public" vector space. The Knowledge representation must carry inherent access-control metadata at the node level.
- **Epistemic Action Disclosure**: Epistemic Actions (Exploration) often test boundaries. If the agent decides its Epistemic Action is to "Read all files in `/etc` to understand the host," it behaves exactly like malware. The system integration must bind the Epistemic planner tightly to an OS-level sandbox (e.g., restricted Docker container) to physically limit the agent's "curiosity."

### 3. LLM & Agent Guardrails
- **Truth vs. Probability Hallucination**: LLMs fundamentally output statistical probability, not epistemological truth. The agent's skill explicitly demands rigorous epistemology. Therefore, the agent must not accept the raw LLM output as a "Belief" unless it survives the `ActiveInferenceAgent.step()` verification phase. Unverified LLM outputs must be flagged in memory as *hypotheses*, never *facts*.
- **Confirmation Bias in Model Updates**: When updating its internal model (Step 2.3), the LLM might exhibit confirmation bias, selectively heavily weighting observations that match its preexisting structural priors while down-weighting surprising, critical security alerts. The agent must mathematically force the processing of high-surprise observations, ensuring "uncomfortable" data isn't ignored to artificially keep Free Energy low.
