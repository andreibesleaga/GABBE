---
name: adaptive-architecture
description: Design systems that evolve and work offline (Local-First, WASM, CRDTs).
triggers: [local-first, offline-first, crdt, automerge, yjs, wasm, webassembly, edge ai, resiliency]
tags: [architecture]
context_cost: medium
---
# Adaptive Architecture Skill

## Goal
To build systems that are robust, responsive, and respectful of user data ownership.

## Capabilities

### 1. Local-First (The New Standard)
-   **CRDTs**: Conflict-free Replicated Data Types for automatic syncing (Automerge/Yjs).
-   **Sync Engines**: Replicache, ElectricSQL, PouchDB.
-   **Philosophy**: The *client* is the source of truth. The *server* is just a backup/relay.

### 2. Emerging Runtimes (WASM)
-   **Universal Compute**: Run the same Rust/Go code on Server, Browser, and IoT Edge.
-   **Sandboxing**: Securely run untrusted plugins (Extensibility).
-   **WASI**: WebAssembly System Interface for "Write Once, Run Anywhere" (really).

### 3. Edge AI Offloading
-   **Hybrid Inference**: Run small models (SLMs) on-device (latency/privacy) and large models (LLMs) in cloud.
-   **TensorFlow Lite / ONNX**: Optimizing models for mobile/edge.

## Steps
1.  **Data Ownership**: Give users their data (SQLite on device).
2.  **Optimistic UI**: UI updates immediately. Sync happens in background.
3.  **Conflict Resolution**: Use CRDTs to mathematically guarantee convergence.

## Deliverables
-   `sync-strategy.md`: Choice of CRDT vs Last-Write-Wins.
-   `wasm-plugin.rs`: Template for a WASM extension.
-   `local-db.schema`: Schema for client-side SQLite.

## Security & Guardrails

### 1. Skill Security (Adaptive Architecture)
- **CRDT Poisoning Defense**: When agents design Local-First applications, they must mandate cryptographic signing for all CRDT (Conflict-free Replicated Data Type) operations. If an offline client's operations are merged without signature verification, a compromised local device could inject malicious state changes that replicate across the entire network.
- **WASM Sandbox Escape Identification**: The agent must treat WebAssembly (WASM) not as a perfect security boundary, but as a defense-in-depth layer. Any architecture utilizing WASI must explicitly define the minimal required capability grants (e.g., denying arbitrary filesystem access to WASM plugins).

### 2. System Integration Security
- **Data Residency & Local-First**: If the system handles regulated data (HIPAA, GDPR), the agent must heavily scrutinize the offline-first design. Storing full SQLite replicas on untrusted user devices (phones, laptops) bypasses central data loss prevention (DLP) controls. The architecture must enforce aggressive local data expiration and mandatory on-device encryption at rest (e.g., SQLCipher).
- **Edge AI Prompt Leakage**: When offloading inference to the Edge (SLMs), the architecture must not rely on sensitive, system-level prompts or API keys that are transmitted to the local device. The agent must verify that the Edge AI component only processes localized, sandboxed logic without exposing central intellectual property.

### 3. LLM & Agent Guardrails
- **Offline Mode Hallucination**: The LLM might confidently propose an offline-first architecture for operations that inherently require synchronous, central validation (e.g., financial ledger transactions). The agent must aggressively push back against applying CRDTs or Local-First patterns to strong-consistency domains, preventing "double-spend" vulnerabilities by design.
- **Complexity Bias**: The agent must counter its own bias towards proposing complex, modern patterns (WASM + CRDTs + Edge AI) for simple problems. It must enforce a "Simplicity Veto" if the NFRs do not explicitly demand extreme disconnection tolerance, thereby reducing the overall attack surface.
