---
name: visual-whiteboarding
description: Use spatial-canvas MCP servers (Miro, Draw.io, Figma) to map architectures, user flows, and wireframes.
triggers: [whiteboard, miro, draw.io, figma, canvas, spatial, wireframe]
tags: [architecture]
context_cost: low
---
# Visual Whiteboarding Skill

To be used when the user requests generating diagrams onto a physical board, canvas, or using external visual diagramming tools (Miro, Draw.io, Figma).

## 1. When to Use Visual Whiteboarding
*   **Complex Architectures**: If a project exceeds 5-7 microservices or involves complex cloud interconnects, suggest a live `Draw.io` or `Miro` synced architecture over text-bound Mermaid.
*   **PRD Syncing**: If a Product Requirements Document (PRD) requires a user flow or journey map, use the `Miro` MCP to generate a spatial flow diagram.
*   **Design to Code**: If tasked with creating a frontend component based on a `Figma` design, use the `Figma` MCP to read the nodes and tokens, maintaining semantic parity.

## 2. Choosing the Right Visual Tool
| Tool | Best For | MCP Capability |
| :--- | :--- | :--- |
| **Draw.io** | C4 Context/Container/Component Diagrams, UML, ERD | Create, read, and write `.drawio` XML directly. |
| **Miro** | User Flows, Mind Maps, Architectural Whiteboarding, Sticky Note PRDs | Create shapes, sticky notes, connectors on a live board. |
| **Figma** | High-fidelity UI Design, Component Specs, UI/UX tokens | Read-only extraction of visual semantics to output React/HTML/CSS code. |
| **Mermaid (Image)** | Quick, stateless, text-to-image rendering | Translates Markdown blocks to SVG/PNG images. |

## 3. Workflow for Generating Canvas Architecture
1.  **Understand Requirements**: Read the `PLAN.md` or `SYSTEM_ANALYSIS_TEMPLATE.md`.
2.  **Define Nodes and Edges**: Before calling the visual MCP tools, formulate the topology using the `WHITEBOARD_DESIGN_TEMPLATE.md`.
3.  **Execute the Drawing**: Use the specific MCP server tool (e.g., `create_shape` in Miro or `write_drawio_xml` in Draw.io) to instantiate the diagram on the board.
4.  **Verification**: Re-read the canvas or generated XML to ensure no relationships were hallucinated or omitted.

## 4. Avoiding Hallucinations
*   **Spatial Overlap**: Agents must calculate X/Y coordinates carefully to avoid stacking nodes on top of each other. Add an arbitrary offset (e.g., +200px) per new node in a sequence.
*   **Secret Leakage**: NEVER write API keys, database credentials, or real user data onto shared visual canvases like Miro or Figma. Redact all tokens.
