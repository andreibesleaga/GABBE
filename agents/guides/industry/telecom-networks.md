# Telecom Software & Networks Guide

## 1. Introduction
Building software for the Telecommunications industry requires adhering to massive scale, high reliability ("Five Nines" 99.999% uptime), and strict global standards. Telecom architecture is generally split between IT (driving billing, catalogs, CRM) and the Core Network (hardware, antennas, packet cores).

## 2. TM Forum & The Open Digital Architecture (ODA)
The TM Forum (TMF) is an alliance of global communication service providers. They maintain the standards for **OSS** (Operations Support Systems) and **BSS** (Business Support Systems).

### TMF Open APIs
Never design custom REST APIs for basic telecom functions; always use TMF Open APIs.
- **TMF620 (Product Catalog Management)**: Defines the lifecycle of selling a telecom product.
- **TMF622 (Product Ordering)**: The standard for submitting an order for a new SIM or internet plan.
- **TMF666 (Account Management)**: Managing customer billing accounts.
- **TMF639 (Resource Inventory)**: Tracking physical routers or logical numbers (MSISDNs).

### ODA (Open Digital Architecture)
ODA is a component-based software architecture replacing legacy, monolithic OSS/BSS platforms with cloud-native, plug-and-play microservices.

## 3. Network Exposure & CAMARA
Historically, the capabilities of a 4G/5G cellular network (like knowing exactly where a phone is, or guaranteeing latency) were locked inside the carrier.

### GSMA CAMARA Initiative
CAMARA is an open-source project defining standard APIs that expose network capabilities to third-party developers, regardless of which carrier the end-user is on.
- **Quality on Demand (QoD)**: An app can request a temporary slice of guaranteed 5G bandwidth (e.g., for a remote surgery or drone flight).
- **Device Location**: Query the cell towers to find a device, bypassing the phone's OS GPS spoofing.
- **SIM Swap**: A critical anti-fraud API for banks to check if a user's SIM card was recently ported to a hacker.

## 4. eSIM and IoT (eUICC)
The physical plastic SIM card is being replaced by the eUICC (Embedded Universal Integrated Circuit Card).
- **Consumer Standard (SGP.22)**: End-user scans a QR code to download a profile from the carrier's SM-DP+ server.
- **IoT Standard (SGP.32)**: Remote provisioning of thousands of smart meters or fleet vehicles without user intervention.

## 5. Agentic Implementation
When tasked with integrating enterprise systems with a cellular provider, or mocking a Telecom billing system, invoke the `telecom-networks` skill. The agent will restrict itself to TMF and CAMARA standards and output the required integration models in the `TELECOM_API_TEMPLATE.md`. This prevents building bespoke "spaghetti" integrations that carriers will reject.
