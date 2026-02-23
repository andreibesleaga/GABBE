---
name: telecom-networks
description: Architect Telecom interfaces using TM Forum ODA, GSMA CAMARA, and eSIM standards
triggers: [design telecom api, integrate tm forum, camara network api, esim provisioning, tmf, oda]
tags: [telecom, networking, camara, tmf, gsma]
context_cost: high
---
# telecom-networks

## Goal
To architect, integrate, and audit enterprise software running in or interfacing with the Telecommunications industry. This ensures compliance with established global standards (TM Forum, GSMA, 3GPP) to guarantee interoperability between Carrier Networks, OSS/BSS, and third-party developers.

## Steps
1. **Identify the Domain**: Determine if the architecture sits in the BSS (Business Support Systems - Billing, CRM), OSS (Operations Support Systems - Network provisioning, faults), or relies on Network Exposure (CAMARA APIs).
2. **Apply Standards**:
   - For internal/B2B Telecom architecture, map microservices to the **TM Forum Open Digital Architecture (ODA)** and use **TMF Open APIs** (e.g., TMF622 for Product Ordering, TMF629 for Customer Management).
   - For external developers querying network state, utilize **GSMA CAMARA APIs** (e.g., Device Location, Quality on Demand).
   - For IoT and Mobile deployments, incorporate **GSMA eSIM (SGP.22/SGP.32)** provisioning architectures (SM-DP+ integrations).
3. **Output**: Generate the API topology and architecture map using `agents/templates/industry/TELECOM_API_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **Strict Privacy Enforcement**: Telecom data includes hyper-sensitive CPNI (Customer Proprietary Network Information). The agent must enforce strict OAuth2/OIDC scoping and TLS encryption when designing data transit layers for location or billing data.

### 2. System Integration Security
- **Rate Limiting at the Edge**: When exposing Core Network capabilities to the public via CAMARA APIs, the agent must mandate robust API gateway rate-limiting to prevent signaling storms from taking down physical cell towers.

### 3. LLM & Agent Guardrails
- **No Hallucinated TMF Specs**: The LLM must not invent custom payload structures for operations where TM Forum APIs exist. It must reference the exact TMF specification number (e.g., `TMF620` for Product Catalog) to maintain strict interoperability.
