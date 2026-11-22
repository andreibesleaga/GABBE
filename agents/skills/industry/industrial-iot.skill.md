---
name: industrial-iot
description: Edge-to-cloud design for industrial telemetry with Purdue levels, OPC UA, MQTT and cloud ingestion. Use when factory equipment, PLC or SCADA data must reach cloud systems.
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

## Constraints
- Network boundaries and firewalls are shown per Purdue level.
- OPC UA stays on the factory floor; MQTT carries edge-to-cloud telemetry.

## Output Format
`IOT_TELEMETRY_TEMPLATE.md` (`agents/templates/industry/`) filled in with the topology and ingestion pattern.

## Limits and safety
- Never propose inbound connections from the internet or cloud into Level 1 or 2 OT networks; data flows outward through an edge gateway or data diode.
- Generated code and tests never write to a PLC or send control commands; against real equipment they are read-only, otherwise use a simulator.
- Telemetry is encrypted in transit (TLS 1.2 or later).
- Raw sub-second telemetry goes to a time-series database unless the human justifies another store.
