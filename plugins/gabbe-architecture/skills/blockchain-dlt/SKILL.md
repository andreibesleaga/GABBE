---
name: blockchain-dlt
description: "Architecture and security notes for blockchain and smart contract systems — network choice, contract design, key handling, oracles. Use when a design involves a ledger, Solidity code or a web3 integration with an enterprise system."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/architecture/blockchain-dlt.skill.md"
  tags: "blockchain, web3, security, dlt"
  core: "false"
  context_cost: "high"
---
# blockchain-dlt

## Goal
To architect, evaluate, and securely integrate Distributed Ledger Technologies (DLT), blockchains, and smart contracts into enterprise systems, ensuring immutability, consensus precision, and interoperability.

## Steps
1. **Network Selection**: Assess if a public blockchain (Ethereum/Polygon), private/permissioned DLT (Hyperledger Fabric/Corda), or hybrid approach is required based on trust models and transaction throughput needs.
2. **Contract Architecture**: Design immutable state machines. Define access controls, upgradeability patterns (e.g., Proxy pattern), and event emitters.
3. **Interoperability**: Outline integration with traditional enterprise systems via Oracles and off-chain indexing (e.g., The Graph).
4. **Output Generation**: Produce the system architecture and logic flow using `agents/templates/architecture/SMART_CONTRACT_TEMPLATE.md`.

## Constraints
- Contract code is checked for reentrancy, integer overflow and front-running.
- Keys are held in a key manager or hardware module, never in files.

## Output Format
The architecture and logic flow in `SMART_CONTRACT_TEMPLATE.md` (`templates/architecture/`).

## Limits and safety
- A review of contract code checks reentrancy, integer overflow and front-running and says which checks were run. It is not an audit: a contract that holds value needs an independent human audit.
- Private keys never go into code or config; propose a key manager or hardware module.
- Before proposing a state change to a deployed contract, say that it cannot be undone except through the upgrade mechanism. Deploying to a mainnet is the human's action.
