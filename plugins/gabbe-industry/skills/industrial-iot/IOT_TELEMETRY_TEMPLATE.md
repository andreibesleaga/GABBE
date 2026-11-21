# Industrial IoT (IIoT) & Telemetry Architecture Template

**System/Factory:** [Factory or System Name]
**Date:** [YYYY-MM-DD]
**Architect / Agent:** [Agent Name]
**Throughput Target:** [e.g., 50,000 messages/sec]

## 1. Network Topology (Purdue Model)
*Map the physical deployment levels and the protocols crossing boundaries.*

### Operational Technology (OT) Layer (Levels 0-2)
- **PLCs/Sensors**: [e.g., Siemens S7, Modbus RTU, IO-Link]
- **Local Protocol**: [e.g., OPC UA, Ethernet/IP, Profinet]
- **Data Collection Rate**: [e.g., 100ms polling]

### Edge / Fog Layer (Level 3)
- **Edge Gateway Hardware**: [e.g., IPC, Cisco IE, Raspberry Pi Compute]
- **Edge Processing**: [e.g., Protocol Translation (OPC UA -> MQTT), Data Aggregation, Edge ML Inference]
- **Local Historian**: [Is there a fallback time-series DB if cloud goes offline? e.g., InfluxDB Edge]

### IT / Cloud Layer (Levels 4-5)
- **Cloud Broker**: [e.g., AWS IoT Core, Azure IoT Hub, HiveMQ]
- **Ingestion Protocol**: [e.g., MQTT over TLS 1.2]

## 2. Topic Architecture (MQTT)
*Define the structured payload topics for the broker.*

**Standard Topic Format**: `[Namespace]/[Site]/[Area]/[AssetGroup]/[Asset]/[Topic]`

| Topic Example | Publisher | Subscriber(s) | QoS | Description |
| :--- | :--- | :--- | :--- | :--- |
| `acme/plant_1/line_a/pump/102/telemetry` | Edge Gateway | Cloud DB, Alert Engine | `1` | Real-time sensor metrics (Vibration, Temp) |
| `acme/plant_1/line_a/pump/102/command` | Cloud App | Edge Gateway | `1` | Start/Stop control signals (Extreme Caution) |
| `acme/plant_1/+/+/+/alarms` | Edge Gateway | Cloud Alert Engine | `2` | High-priority fault notifications |

## 3. Payload Schema (JSON Snippet)
*Standardized edge payload combining timestamps, metadata, and sensor values.*
```json
{
  "timestamp": "2026-03-01T14:05:01.332Z",
  "asset_id": "pump-102",
  "site_id": "plant_1",
  "telemetry": {
    "vibration_hz": 45.2,
    "temperature_c": 72.1,
    "rpm": 1450
  },
  "status": "active"
}
```

## 4. Security Enforcement (Edge-to-Cloud)
- **Authentication**: [e.g., X.509 Device Certificates minted by AWS IoT]
- **Authorization**: [e.g., IoT Policies restricting publish access strictly to the assigned asset Topic tree]
- **Encryption**: Over-the-wire encryption via TLS 1.2.

## 5. Data Storage Strategy
- **Hot Data (0-30 days)**: [e.g., Time-Series Database (InfluxDB) for fast dashboard querying]
- **Cold Data (30+ days)**: [e.g., S3 Glacier / Parquet for ML model training]
