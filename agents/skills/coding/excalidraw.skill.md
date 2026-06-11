---
name: excalidraw
description: Create and manage Excalidraw diagrams via MCP for architecture visualization.
triggers: [excalidraw, whiteboard, visual diagram, hand-drawn diagram]
tags: [coding, architecture, visual, diagramming]
context_cost: medium
---
# Excalidraw Skill

## Goal
Create, edit, and manage Excalidraw diagrams programmatically using the `@cmd8/excalidraw-mcp` server. Generate architecture diagrams, flowcharts, system maps, and wireframes with the hand-drawn Excalidraw aesthetic.

## Prerequisites
- **MCP Server**: `excalidraw` must be configured in your MCP config (see `templates/core/MCP_CONFIG_TEMPLATE.json`).
- **Runtime**: Node.js 18+
- **File**: A `.excalidraw` file path must be specified (created automatically if it doesn't exist).

## Capabilities

### MCP Tools Available
| Tool | Purpose |
|---|---|
| `createNode` | Create a shape (rectangle, ellipse, diamond) with label text. Returns node ID |
| `createEdge` | Create an arrow connecting two nodes by ID or label |
| `deleteElement` | Remove a node or edge by ID or label |
| `getFullDiagramState` | Get markdown representation of the full diagram (nodes, edges, frames, colors) |

### Supported Diagram Types
- **Architecture Diagrams**: C4 Context, Container, Component views
- **Flowcharts**: Decision trees, process flows, SDLC workflows
- **System Maps**: Microservice topology, network diagrams
- **Wireframes**: UI layout sketches, page flows
- **Entity Relationships**: Database schema visualizations
- **Event Storming**: Domain event maps with sticky-note aesthetics

## Steps

1. **Plan the diagram structure**
   - Use `WHITEBOARD_DESIGN_TEMPLATE.md` to pre-map geometry (X/Y grid)
   - List all nodes (name, shape, color) and edges (source → target, label)
   - Pre-calculate coordinates to avoid overlap — LLMs are poor at spatial arrangement

2. **Create nodes**
   - Call `createNode` for each element with appropriate shape and position
   - Group related nodes by color or frame

3. **Create edges**
   - Call `createEdge` to connect nodes by ID or label
   - Add edge labels for relationship descriptions

4. **Verify diagram**
   - Call `getFullDiagramState` to review the complete diagram
   - Check for missing connections, overlapping nodes, or unlabeled edges

5. **Sync back to text**
   - Mirror structural changes into `PLAN.md` or `SYSTEM_ANALYSIS_TEMPLATE.md`
   - Diagrams are not searchable by RAG — keep metadata in text

## Deliverables
- `.excalidraw` file with the completed diagram
- Text-based summary of diagram structure in project documentation

## Usage Examples

### Create an architecture diagram
```
> "Create an Excalidraw architecture diagram for our microservices: API Gateway → Auth Service, User Service, Order Service. Save to docs/architecture.excalidraw"
```

### Visualize a database schema
```
> "Draw the database schema in Excalidraw showing Users, Orders, and Products tables with relationships"
```

### Create a flowchart
```
> "Create an Excalidraw flowchart for the CI/CD pipeline: Build → Test → Security Scan → Deploy → Smoke Test"
```

## Security & Guardrails

### 1. Skill Security
- **Local Files Only**: Excalidraw MCP operates on local `.excalidraw` files. No network access, no cloud storage.
- **No Code Execution**: The MCP creates diagram elements — it does not execute any code.
- **File Scope**: Ensure the `--diagram` path points to a file within the project directory.

### 2. Agent Guardrails
- **Pre-map Geometry**: Always calculate node positions before creating elements. Random placement results in unreadable diagrams.
- **State Sync**: Always update text-based documentation when modifying visual diagrams.
- **Verify Before Sharing**: Call `getFullDiagramState` to validate the diagram is complete before presenting to the user.
