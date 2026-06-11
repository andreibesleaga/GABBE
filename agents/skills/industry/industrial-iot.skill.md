---
name: industrial-iot
description: Architect high-throughput industrial telemetry via MQTT & OPC UA
triggers: [iiot, opc ua, mqtt, scale telemetry, purdue model, scada, plc]
tags: [iot, industrial, mqtt, opc-ua, edge]
context_cost: medium
---
# industrial-iot

## Goal
To architect robust, secure, and low-latency Industrial IoT (IIoT) architectures spanning the Edge (Factory Floor/Sensors) to the Cloud, specifically utilizing foundational protocols like OPC UA and MQTT for Industry 4.0 implementations.

## Steps
1. **Topology Definition**: Define the Purdue Model levels (Level 0: Physical Process to Level 5: Cloud) and identify where the network boundaries and firewalls sit.
2. **Protocol Mapping**:
   - **OPC UA**: Use for complex data modeling, semantic meaning, and secure Client/Server interaction within the factory floor (OT network).
   - **MQTT**: Use for lightweight, high-throughput Publisher/Subscriber telemetry routing from the Edge gateway to the Cloud IT infrastructure.
3. **Data Ingestion**: Design the Cloud ingestion pattern (e.g., AWS IoT Core, Azure IoT Hub, Kafka) handling high-velocity time-series data.
4. **Output**: Generate the telemetry layout and architecture using `agents/templates/industry/IOT_TELEMETRY_TEMPLATE.md`.

## Security & Guardrails

### 1. Skill Security
- **Airgap Respect**: The agent must never propose direct inbound connections from the open internet to Level 1/2 OT (Operational Technology) networks (e.g., directly querying a PLC database from AWS).

### 2. System Integration Security
- **Data Diode / Gateway Check**: All Edge-to-Cloud telemetry must flow outward via an Edge Gateway or Data Diode using TLS 1.2+ encrypted MQTT payloads.

### 3. LLM & Agent Guardrails
- **Time-Series Restraint**: The LLM must not propose relational databases (like MySQL/PostgreSQL) for storing raw sub-second sensor telemetry. It must default to Time-Series Databases (TSDB) like InfluxDB or TimescaleDB.
