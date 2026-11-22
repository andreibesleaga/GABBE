---
name: adaptive-architecture
description: Design offline-first and local-first systems — sync strategy (CRDT or last-write-wins), WASM plugin boundaries, edge versus cloud AI split. Use when an app must work offline, sync between devices, or run plugins or models on the user's device.
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
1.  **Data Ownership**: Give users their data (SQLite on device). For the pattern choice that comes before this, see `arch-patterns.skill`.
2.  **Optimistic UI**: UI updates immediately. Sync happens in background.
3.  **Conflict Resolution**: Use CRDTs to mathematically guarantee convergence.

## Output Format
-   `sync-strategy.md`: Choice of CRDT vs Last-Write-Wins.
-   `wasm-plugin.rs`: Template for a WASM extension.
-   `local-db.schema`: Schema for client-side SQLite.

## Constraints
- Use CRDTs only where eventual consistency is acceptable.
- Add WASM, CRDTs or edge AI only when a stated requirement needs them.
- Regulated data stored on a device is encrypted and expires.

## Limits and safety
- Offline-first suits data that tolerates eventual consistency. For ledgers, stock or other strong-consistency work, say so and do not propose CRDTs.
- Treat operations from offline clients as untrusted input: the design says how a bad client's operations are authenticated and validated before merge.
- If the data is regulated (HIPAA, GDPR), list what a local replica stores and get the human's yes on on-device encryption and expiry.
- WASM plugins get no filesystem or network access by default; list each grant. Never put system prompts or API keys into on-device models.
- Propose WASM, CRDTs or edge AI only when a stated requirement needs them.
