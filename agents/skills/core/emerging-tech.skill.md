---
name: emerging-tech
description: Gives design guidance and a short plan for 6G edge placement, Matter IoT devices and vector search with RAG. Use when a design involves low-latency edge compute, smart-home devices, embeddings or semantic search.
triggers: [6g, iot, matter, vector, embedding, semantic search, rag, edge native, post-quantum]
tags: [core]
context_cost: medium
---
# Emerging Tech Skill

## Goal
To future-proof applications for the next wave of connectivity and intelligence.

## Capabilities

### 1. 6G & Edge-Native Design
-   **Ultra-Low Latency**: Design systems for <1ms loops (Haptic Internet).
-   **Compute Continuum**: Seamlessly move workloads between Device <-> Edge <-> Cloud.
-   **Agentic IoT**: Devices that negotiate with each other autonomously (M2M economy).

### 2. Matter Protocol (IoT)
-   **Interoperability**: One protocol for Apple/Google/Amazon smart home ecosystems.
-   **Local Control**: Devices work without internet (privacy-first).
-   **Thread/Wi-Fi 6**: Understanding the mesh network topology.

### 3. Vector Computing (AI Memory)
-   **Semantic Search**: Replacing keyword search with "meaning" search (Embeddings).
-   **RAG Pipelines**: Retrieval-Augmented Generation for grounding LLMs.
-   **Databases**: Pinecone, Weaviate, pgvector strategy.

## Steps
1.  **Latency Matters**: In 6G apps, the speed of light is the bottleneck. Move data closer to the user.
2.  **Privacy by Design**: Matter devices talk locally. Don't send sensitive sensor data to the cloud unless necessary.
3.  **Embed Everything**: Text, Images, Audio. If it's data, it can be a vector.

## Deliverables
-   `vector-strategy.md`: Plan for embedding data.
-   `matter-config.yaml`: Device capability profile.
-   `edge-placement.drawio`: Diagram of compute distribution.

## Constraints
- Say for each standard whether it is final or a draft; do not build on a draft as if it were final.
- Cite a source for every latency figure, date or protocol claim, or mark it "unverified".
- Check security advisories for any new protocol library before recommending it.

## Output Format
The deliverables above (`vector-strategy.md`, `matter-config.yaml`, `edge-placement.drawio`) plus a list of the sources used and the claims marked "unverified".

## Limits and safety
- State whether each standard is final or a draft; never recommend building on a draft extension as if it were stable.
- In a RAG design, store access rules in the vector metadata so one user's data is never retrieved for another; strip secrets and personal data before embedding.
- Put Matter and other IoT devices on their own network segment, apart from the application network.
- Design for replaceable cryptography (no hard-coded RSA or ECC choice) when the system must live past 2030.
