---
name: cryptography-standards
description: Enforce correct cryptographic algorithms, hashing, and TLS standards
triggers: [encrypt data, hash passwords, set tls policy]
tags: [security]
context_cost: low
---
# cryptography-standards

## Goal
Apply, enforce, and maintain robust cryptographic strategies to protect data at rest and data in transit across all services.


## Steps
1. **Identify Requirement**: Determine if data requires at-rest hashing, symmetric encryption, or transit protection.
2. **Algorithm Selection**: Utilize modern, enterprise-approved primitives (e.g., Argon2id, AES-256-GCM, TLS 1.3).
3. **Key Management**: Document integration paths to secure KMS or Vaults; never hardcode cryptographic keys.
4. **Verification**: Write static tests that fail the build if deprecated algorithms (MD5, SHA1) are used.

## Security & Guardrails

### 1. Skill Security
- **Secret Generation Mute**: Do not allow the agent to generate valid "test" private keys or robust secrets dynamically and log them to the filesystem or chat interface.
- **Code Execution Ban**: Prevent the skill from dynamically executing complex crypto mathematics inside the markdown parser sandbox.

### 2. System Integration Security
- **Algorithm Veto**: Implicitly block the use of deprecated primitives (MD5, SHA1, DES, ECB mode). The CI should fail if these tokens are present.
- **Entropy Exhaustion**: Agents must ensure proper CSPRNG functions (e.g., `/dev/urandom`, `crypto.randomBytes()`) are used, never `Math.random()`.

### 3. LLM & Agent Guardrails
- **Hallucinated Cryptography**: The LLM must NEVER output or suggest a custom-designed cryptographic algorithm. It must rely exclusively on mature, peer-reviewed libraries (e.g., libsodium).
- **Misapplied Encryption**: The agent must distinguish between hashing (for passwords) and symmetric encryption (for PII). It cannot confidently recommend hashing for credit card retrieval logic.
