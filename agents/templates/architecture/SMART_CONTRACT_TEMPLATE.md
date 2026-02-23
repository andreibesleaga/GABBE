# Smart Contract & DLT Architecture Template

**Contract/System Name:** [System Name]
**Network / Protocol:** [e.g., Ethereum Mainnet, Hyperledger Fabric, Polygon]
**Author / Auditor:** [Name / Agent]

## 1. System Overview
[Describe the business logic this distributed ledger aims to solve. Why is a blockchain needed here instead of a traditional database?]

## 2. Architecture & Components

### 2.1 On-Chain Logic (Smart Contracts)
- **Primary Contract(s)**: [List main contracts and their responsibilities]
- **State Variables**: [Which variables are stored permanently on-chain?]
- **Events**: [What events are emitted for off-chain listeners?]

### 2.2 Upgradeability Pattern
- [ ] Immutable (Deploy once, no changes)
- [ ] Proxy Pattern (Transparent / UUPS)
- [ ] Diamond Pattern (EIP-2535)
*Rationale:* [Explain the choice]

### 2.3 Off-Chain Integration (Oracles & App Layer)
- **Oracles**: [How does real-world data enter the blockchain? e.g., Chainlink]
- **Indexing**: [How is data queried? e.g., The Graph, custom backend indexer]
- **Wallet / Auth**: [MetaMask, WalletConnect, Enterprise Custodial Wallet]

## 3. Security Analysis (Critical)

| Vulnerability Category | Mitigation Strategy in Code |
| :--- | :--- |
| **Reentrancy** | E.g., Use Checks-Effects-Interactions pattern & `nonReentrant` modifier |
| **Access Control** | E.g., OpenZeppelin `Ownable` or `AccessControl` roles |
| **Front-Running (MEV)** | [Mitigation logic] |
| **Logic Errors / Math** | E.g., Rely on Solidity ^0.8.0 built-in overflow protection |

## 4. Gas & Performance Optimization
- [List specific decisions made to keep transaction costs (gas) low, e.g., tightly packing structs, avoiding loops over unbounded arrays.]

## 5. Deployment & Testing Plan
1. **Local Testnet**: [Hardhat / Foundry / Ganache]
2. **Test Coverage Target**: [e.g., 100% Branch Coverage]
3. **Public Testnet (e.g., Sepolia)**: [Target Date]
4. **Third-Party Security Audit**: [Requirement before Mainnet]
