---
name: adaptive-architecture
description: Design systems that evolve and work offline (Local-First, WASM, CRDTs).
context_cost: medium
---
# Adaptive Architecture Skill

## Triggers
- local-first
- offline-first
- crdt
- automerge
- yjs
- wasm
- webassembly
- edge ai
- resiliency

## Purpose
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

## Instructions
1.  **Data Ownership**: Give users their data (SQLite on device).
2.  **Optimistic UI**: UI updates immediately. Sync happens in background.
3.  **Conflict Resolution**: Use CRDTs to mathematically guarantee convergence.

## Deliverables
-   `sync-strategy.md`: Choice of CRDT vs Last-Write-Wins.
-   `wasm-plugin.rs`: Template for a WASM extension.
-   `local-db.schema`: Schema for client-side SQLite.
