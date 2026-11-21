---
name: sketch-to-diagram
description: "Turn a hand-drawn sketch or whiteboard photo into an editable diagram (Excalidraw, Mermaid or Draw.io) after the human approves the recognised elements. Use when the user supplies an image of a diagram, wireframe or event-storming board."
triggers: [sketch, hand-drawn, whiteboard photo, napkin, wireframe scan, recognize diagram]
tags: [coding, architecture, visual, recognition, AI]
context_cost: high
---
# Sketch-to-Diagram Skill

## Goal
Transform hand-drawn sketches (whiteboard photos, napkin drawings, paper wireframes) into formal, editable digital diagrams using the **Sketch → Recognize → Redraw** pipeline:
1. **Recognize**: Image recognition MCP describes elements, connections, and labels from the sketch
2. **Structure**: Agent organizes recognized elements into a structured diagram description
3. **Redraw**: Agent generates formal diagram via Excalidraw MCP, Mermaid code, or Draw.io XML

## Prerequisites
- **Image Recognition MCP**: `image-recognition` must be configured (requires `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`)
- **Output MCP** (at least one):
  - `excalidraw` — for `.excalidraw` output
  - `drawio` — for Draw.io XML output
  - Or none — for Mermaid text output (no MCP needed)
- **Optional**: Tesseract OCR installed for text extraction from noisy images

## Supported Input Types
| Input | Examples |
|---|---|
| **Whiteboard photos** | Architecture sketches, event storming boards, sprint planning |
| **Napkin drawings** | Quick flowcharts, ER diagrams, state machines |
| **Paper wireframes** | UI layouts, page flows, component hierarchies |
| **Screenshot mockups** | Existing diagram screenshots to recreate as editable |
| **Hand-drawn charts** | Bar charts, timelines, Gantt outlines |
| **Annotated screenshots** | Marked-up UIs with arrows and notes |

## Steps

### Phase 1: Capture & Recognize
1. **Receive the image** — user provides a file path or base64-encoded image
2. **Call image-recognition MCP** — send image for analysis:
   - Describe all shapes (rectangles, circles, diamonds, arrows)
   - Identify text labels on each shape
   - Map connections (which arrows connect which shapes)
   - Note colors, groupings, and spatial layout
3. **Extract text** (optional) — if handwriting is unclear, use Tesseract OCR

### Phase 2: Structure
4. **Build element list** — organize recognized elements into:
   - Nodes: `{id, label, shape, position, color, group}`
   - Edges: `{source, target, label, direction}`
   - Frames/Groups: `{name, children[]}`
5. **Validate** — check for unconnected nodes, duplicate labels, missing edges
6. **Present to user** — show structured description for approval before redrawing

### Phase 3: Redraw
7. **Choose output format** based on user preference or diagram complexity:
   - **Excalidraw** (visual, hand-drawn style): Use `excalidraw` MCP tools
   - **Mermaid** (text-based, version-controllable): Generate Mermaid syntax
   - **Draw.io** (enterprise, XML): Use `drawio` MCP tools
8. **Create diagram** — generate the formal diagram using chosen tool
9. **Document** — fill `SKETCH_TO_DIAGRAM_TEMPLATE.md` with results

## Output Formats

| Format | When to Use | MCP Required |
|---|---|---|
| Excalidraw (`.excalidraw`) | Visual collaboration, hand-drawn aesthetic | `excalidraw` |
| Mermaid (`.md`) | Version-controlled docs, PRDs, READMEs | None |
| Draw.io (`.drawio`) | Enterprise docs, Confluence, detailed layouts | `drawio` |
| PNG/SVG export | Static documentation, presentations | Depends on source |

## Usage Examples

### Whiteboard photo to architecture diagram
```
> "Here's a photo of our whiteboard architecture sketch. Convert it to an Excalidraw diagram."
```

### Napkin flowchart to Mermaid
```
> "I drew this flowchart on paper [image]. Convert it to Mermaid syntax for our README."
```

### UI wireframe to diagram
```
> "Recognize this hand-drawn wireframe and create a component hierarchy diagram."
```

### Event storming board to formal diagram
```
> "Here's a photo of our event storming session. Extract all events, commands, and aggregates into a structured diagram."
```

## Deliverables
- `SKETCH_TO_DIAGRAM_TEMPLATE.md`: Structured report with original image description, recognized elements, and generated diagram
- Generated diagram file (`.excalidraw`, `.md` with Mermaid, or `.drawio`)

## Constraints
- Do not redraw before the human has approved the element list.
- Every node and edge comes from the image or the human's description.

## Limits and safety
- If the sketch may show credentials, internal addresses or personal data, ask the human before sending it to an external vision service; the local option is Tesseract OCR for text plus a description of the shapes.
- Show the structured element list and get the human's approval before redrawing; after the first redraw ask for corrections.
- Mark low-confidence elements in the list; do not invent nodes or edges the image does not show.
- If recognition is poor (blurry, overlapping), ask the human to describe the diagram instead of guessing.
