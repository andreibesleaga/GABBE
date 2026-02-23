---
name: blockchain-dlt
description: Architect and audit Distributed Ledger/Blockchain systems and Smart Contracts
triggers: [design blockchain, write smart contract, dlt architecture, web3 integration, ethereum, solidity, ledger]
tags: [blockchain, web3, security, dlt]
context_cost: high
---
# blockchain-dlt

## Goal
To architect, evaluate, and securely integrate Distributed Ledger Technologies (DLT), blockchains, and smart contracts into enterprise systems, ensuring immutability, consensus precision, and interoperability.

## Steps
1. **Network Selection**: Assess if a public blockchain (Ethereum/Polygon), private/permissioned DLT (Hyperledger Fabric/Corda), or hybrid approach is required based on trust models and transaction throughput needs.
2. **Contract Architecture**: Design immutable state machines. Define access controls, upgradeability patterns (e.g., Proxy pattern), and event emitters.
3. **Interoperability**: Outline integration with traditional enterprise systems via Oracles and off-chain indexing (e.g., The Graph).
4. **Output Generation**: Produce the system architecture and logic flow using `agents/templates/architecture/SMART_CONTRACT_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **Strict Verification Rules**: The agent must natively enforce checks for Reentrancy attacks, Integer Overflow/Underflow, and Front-Running vulnerabilities when reviewing or outputting Solidity/Smart Contract code.

### 2. System Integration Security
- **Key Management Isolation**: The agent must outline strict segregation of private keys (using HSMs or secure enclaves like AWS KMS) and never suggest writing raw private keys to configuration files.

### 3. LLM & Agent Guardrails
- **Immutable Consequence Warning**: The LLM must explicitly warn the human user when proposing smart contract state changes, highlighting that once deployed to mainnet, the logic cannot be reversed without heavy mitigations (like proxy upgrades).
