---
name: telecom-networks
description: Telecom API and architecture map using TM Forum ODA and Open APIs, GSMA CAMARA and eSIM provisioning. Use when building for carrier BSS or OSS systems or exposing network capabilities to developers.
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

## Constraints
- Use TM Forum Open APIs where one exists instead of custom payloads.
- State whether the system sits in BSS, OSS or network exposure.

## Output Format
`TELECOM_API_TEMPLATE.md` (`agents/templates/industry/`) filled in with the API topology and architecture map.

## Limits and safety
- Location, billing and subscriber data need OAuth2 or OIDC scopes and TLS; confirm consent and legal basis with the human.
- Public network-exposure APIs (CAMARA) get gateway rate limits; write down the limits assumed.
- Cite TM Forum APIs by exact number (for example TMF620); if you are not sure of a number, write "unverified" and do not invent payloads.
- Use a sandbox, never live network or provisioning APIs with real subscribers.
