# Industrial IoT (IIoT) & Industry 4.0 Guide

## 1. Introduction
The Industrial Internet of Things (IIoT) brings cloud compute, machine learning, and advanced telemetry to the factory floor. Unlike consumer IoT (smart thermostats), IIoT deals with mission-critical infrastructure where a millisecond of latency or a dropped connection can cause a halting of production lines, chemical spills, or physical danger.

## 2. The Purdue Enterprise Reference Architecture
IIoT is structured topographically for security and reliability, known as the Purdue Model.
- **Level 0**: The Physical Process (the actual spinning motor).
- **Level 1**: Basic Control (PLCs, Remote I/O, Sensors).
- **Level 2**: Area Supervisory Control (SCADA systems, HMIs pointing to local machines).
- **Level 3**: Site Manufacturing Operations (MES, Historian databases).
- **Level 3.5 (DMZ)**: The Demilitarized Zone isolating the factory from the corporate network.
- **Level 4/5**: Enterprise IT and Cloud (ERP, AWS IoT, Big Data Analytics).

**Security Rule:** Data flows *up* relatively freely. Data flowing *down* (commands from Cloud to PLC) crosses extreme security boundaries and often requires human intervention or dedicated physical gateways (Data Diodes).

## 3. Core Protocols
To bridge the gap between "Operational Technology" (OT - the factory) and "Information Technology" (IT - the cloud), two protocols dominate:

### OPC UA (Open Platform Communications Unified Architecture)
- **Role**: The lingua franca of the factory floor.
- **How it works**: Client/Server model. It doesn't just send raw bytes (like `45.2`), it sends *semantic models* (e.g., "This is Sensor A on Pump 2, it measures Vibration, the unit is Hz, and the upper limit is 50Hz").
- **Where it's used**: Levels 1 to 3. PLCs talking to SCADA systems.

### MQTT (Message Queuing Telemetry Transport)
- **Role**: The bridge to the cloud.
- **How it works**: Publish/Subscribe over TCP/IP. An edge gateway "publishes" telemetry to a central "Broker" (like AWS IoT Core), and multiple cloud microservices "subscribe" to that data.
- **Why it's used**: Extremely lightweight, handles flaky network connections gracefully, and decouples the sender from the receiver.

*Modern deployments often use an Edge IPC (Industrial PC) acting as a protocol translator—reading OPC UA from the machines and publishing MQTT to the cloud.*

## 4. Agentic Implementation
When tasked to design a telemetry pipeline from a manufacturing facility, invoke the `industrial-iot` skill. The agent avoids naive architectures (like connecting a PLC directly to a public MySQL instance) and outputs a comprehensive mapping of Topics, Edge gateways, and TSDB (Time Series Database) storage using the `IOT_TELEMETRY_TEMPLATE.md`.
