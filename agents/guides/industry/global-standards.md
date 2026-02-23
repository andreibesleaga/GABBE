# UN, ITU, & Global Open Source Standards Guide

## 1. Introduction
Enterprise software does not exist in a vacuum. True interoperability and public-sector procurement require adherence to global treaties, non-governmental organizations (NGOs), and open-source foundations. This guide outlines the pillars of global software standardization.

## 2. United Nations: Sustainable Development Goals (SDGs)
The UN's 17 SDGs are the blueprint for peace and prosperity. Software architecture primarily intersects with:
- **Goal 9 (Industry, Innovation, and Infrastructure)**: Ensuring your platform's APIs and data are open, bridging the digital divide, and providing robust (uptime > 99.9%) infrastructure that developing nations can rely on without exorbitant licensing costs.
- **Goal 10 (Reduced Inequalities)**: Following WCAG 2.1 AA/AAA accessibility standards natively so software is inclusive worldwide.
- **Goal 12 (Responsible Consumption and Production)**: Aligning directly with Green Software Engineering (see `green-software.skill.md`) to minimize datacenter e-waste.

## 3. International Telecommunication Union (ITU)
The ITU is the UN specialized agency for ICTs (Information and Communication Technologies).
- **ITU-T X.509**: The foundational standard for public key infrastructure (PKI) and digital certificates defining how TLS/SSL operates globally.
- **ITU-T E.164**: The international public telecommunication numbering plan (why phone numbers look like `+1-555-0100`). Always store telephonic data in E.164 format.
- **ITU-T H-Series**: If building video conferencing or streaming tools, you are interacting with H.264/H.265 (HEVC) standards dictating packetization and compression.

## 4. Worldwide Open Source Foundations
No modern software is written from scratch. Utilizing global Open Source effectively requires strict compliance:
- **Open Source Initiative (OSI)**: The steward of the Open Source Definition. Understand the difference between Permissive licenses (MIT, Apache 2.0) and Copyleft licenses (GPL, AGPL) to prevent legal liability in enterprise codebases.
- **OpenSSF (Open Source Security Foundation)**: The Linux Foundation project for securing the software supply chain. Implement the **SLSA** (Supply-chain Levels for Software Artifacts) framework to prevent dependency confusion and supply chain attacks (e.g., the SolarWinds hack).

## 5. Agentic Implementation
When building systems targeting government procurement, international NGOs, or massive open-source integration, invoke the `global-standards` skill. The agent will audit the architecture against these international frameworks, generating a `GLOBAL_STANDARDS_AUDIT_TEMPLATE.md` to ensure your system represents global best-practices.
