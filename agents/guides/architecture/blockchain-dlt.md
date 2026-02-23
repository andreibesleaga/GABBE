# Blockchain & Distributed Ledger Technology (DLT) Guide

## 1. Introduction
Distributed Ledgers and Blockchains are revolutionary architectures for applications where no single party holds ultimate trust. Unlike traditional databases (which are controlled by central authorities), DLT ensures that data is immutable, transparent, and agreed upon by consensus.

## 2. Choosing the Right Network
Not all problems require a blockchain. If trust exists centrally, use a database. If not, choose the right ledger:

### Public Blockchains (Ethereum, Polygon, Solana)
- **Use Case**: Decentralized Finance (DeFi), global asset tokenization, DAOs, public registries.
- **Trust Model**: Zero trust (Trustless). Anyone can participate.
- **Throughput**: Lower (ranges from 15 to 65,000 TPS computationally depending on the chain/L2).
- **Consensus**: Proof of Stake (PoS), Proof of Work (PoW).

### Enterprise DLT (Hyperledger Fabric, R3 Corda)
- **Use Case**: Supply chain tracking, inter-bank settlements, secure corporate consortiums.
- **Trust Model**: Permissioned (Known participants).
- **Throughput**: High (designed for enterprise speeds).
- **Consensus**: Raft, PBFT (Practical Byzantine Fault Tolerance).

## 3. Smart Contract Architecture
Smart contracts are state machines deployed to the ledger. They dictate the rules of engagement.

### Key Considerations
1. **Immutability vs Upgradability**: Code deployed is final. Bug fixes require deploying entirely new contracts. To circumvent this, use the **Proxy Pattern** (separating the logic contract from the state-holding proxy contract).
2. **Determinism**: Smart contracts cannot compute random numbers securely or make external HTTP calls.
3. **Oracles**: To get real-world data (e.g., the price of AAPL stock, or current weather) inside a blockchain, you must use Decentralized Oracles (like Chainlink).

## 4. Security is Paramount
A bug in a traditional web server might cause downtime; a bug in a smart contract can cause the immediate, irreversible loss of millions of dollars.
- Always use established libraries like **OpenZeppelin** for ERC standards and mathematical operators.
- Enforce the **Checks-Effects-Interactions** pattern to prevent reentrancy attacks.
- Have code audited professionally.

## 5. Agentic Implementation
When working on web3 architectures, invoke the `blockchain-dlt` skill. The agent will assess the requirements, choose an appropriate network, and generate a robust `SMART_CONTRACT_TEMPLATE.md` ensuring security best practices are baked into the design phase.
