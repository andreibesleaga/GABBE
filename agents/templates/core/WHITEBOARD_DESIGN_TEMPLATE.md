# Whiteboard & Spatial Design Template

**Purpose:** A conceptual mapping worksheet for agents to structure node-and-edge relationships *before* invoking spatial drawing tools (Miro, Draw.io). This prevents hallucinated coordinates and spaghetti logic.

---

## 1. Diagram Metadata
*   **Diagram Name**: `[e.g., Auth Flow Context]`
*   **Target MCP Platform**: `[Miro | Draw.io | SVG Render]`
*   **Diagram Type**: `[C4 Container | User Journey | Wireframe | Sequence]`
*   **Scale / Canvas Size**: `[e.g., 1920x1080]`

## 2. Global Styling Preferences
*   **Primary Color**: `[e.g., #0052CC (Blue)]`
*   **Secondary Color**: `[e.g., #FF5630 (Red)]`
*   **Font Family**: `[e.g., Inter, Arial]`
*   **Shape Style**: `[Rounded rectangle / circle / cylinder (for DBs)]`

## 3. Nodes (Entities)
List all entities that need to be drawn. **Crucial:** Approximate the (X, Y) layout to prevent overlaps.

| Node ID | Label / Text | Shape Type | Approx X | Approx Y | Notes / Security Level |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `UX_1` | User/Customer | Person | 100 | 500 | Public Actor |
| `API_1` | API Gateway | RoundRect | 500 | 500 | VPC Ingress |
| `SVC_1` | Auth Service | RoundRect | 900 | 400 | Intranet |
| `DB_1` | Auth PostgreSQL | Cylinder | 1300 | 400 | High Security - Redact Strings |
| `SVC_2` | Payment Service| RoundRect | 900 | 600 | Intranet |
| `API_2` | Stripe API | Cloud | 1500 | 600 | External Service |

## 4. Edges (Relationships)
Define how the nodes connect.

| Source ID | Target ID | Line Style | Arrow | Label (Action) |
| :--- | :--- | :--- | :--- | :--- |
| `UX_1` | `API_1` | Solid | End | 1. Sends login credentials |
| `API_1` | `SVC_1` | Solid | End | 2. Forwards payload |
| `SVC_1` | `DB_1` | Solid | End | 3. Validates hash |
| `API_1` | `SVC_2` | Solid | End | 4. Initiates checkout |
| `SVC_2` | `API_2` | Dashed | End | 5. Charges card (Async) |

## 5. Execution Pre-Flight Checklist
- [ ] Nodes are spaced adequately (min 300px horizontal gap).
- [ ] Secrets and PII are redacted from all node texts.
- [ ] Cloud providers (AWS, Azure, GCP) use their standard icons if supported.
- [ ] Read-only connections are marked as dashed lines; write/execute as solid lines.
