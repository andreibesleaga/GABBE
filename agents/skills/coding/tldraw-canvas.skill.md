---
name: tldraw-canvas
description: Create, manage, and search tldraw canvases for visual design, wireframing, and UI prototyping.
triggers: [tldraw, canvas, wireframe, visual scratchpad, UI sketch, make-real]
tags: [coding, architecture, visual, design, prototyping]
context_cost: medium
---
# tldraw Canvas Skill

## Goal
Create, manage, and manipulate tldraw canvases (`.tldr` files) for visual design, wireframing, architecture sketching, and UI prototyping using the `@talhaorak/tldraw-mcp` server. The tldraw canvas acts as a persistent visual scratchpad that AI agents can programmatically read, write, and search.

## Prerequisites
- **MCP Server**: `tldraw` must be configured in your MCP config (see `templates/core/MCP_CONFIG_TEMPLATE.json`).
- **Runtime**: Node.js 18+
- **Viewer**: Open `.tldr` files at [tldraw.com](https://www.tldraw.com) or the tldraw desktop/VS Code extension.

## Capabilities

### MCP Tools Available
| Tool | Purpose |
|---|---|
| `tldraw_create` | Create a new empty canvas file |
| `tldraw_read` | Load and parse `.tldr` file contents |
| `tldraw_write` | Write/update a canvas with validation |
| `tldraw_list` | List all `.tldr` files with page/shape metadata |
| `tldraw_search` | Full-text search across all canvases |
| `tldraw_get_shapes` | Get all shapes, optionally filtered by page |
| `tldraw_add_shape` | Add a new shape (rectangle, ellipse, arrow, text, etc.) |
| `tldraw_update_shape` | Update properties of an existing shape |
| `tldraw_delete_shape` | Delete a shape from a canvas |

### Supported Use Cases
- **UI Wireframing**: Rapid visual prototypes for PRD phase
- **Architecture Sketching**: System diagrams, component layouts
- **Visual Scratchpad**: Persistent notes, brainstorming, TODO boards
- **Design-to-Code Bridge**: Create wireframes → use vision API to convert to code
- **Sprint Planning**: Visual boards with sticky notes, groupings, connectors

## Steps

1. **Create or open a canvas**
   - Call `tldraw_create` for a new canvas, or `tldraw_read` for existing
   - Organize by project: `docs/wireframes/login.tldr`, `docs/architecture/system.tldr`

2. **Add shapes and content**
   - Call `tldraw_add_shape` for each visual element:
     - `geo` shapes: rectangle, ellipse, diamond, pentagon, hexagon, star, etc.
     - `arrow` shapes: connectors between elements
     - `text` shapes: labels, annotations, notes
     - `draw` shapes: freeform paths
   - Specify position (x, y), size (w, h), color, and fill

3. **Build relationships**
   - Use arrow shapes to connect components
   - Group related shapes by proximity or color coding

4. **Search and navigate**
   - Use `tldraw_search` to find content across all canvas files
   - Use `tldraw_list` to enumerate canvases and their metadata

5. **Sync with project documentation**
   - Mirror canvas structure in text-based docs (PRD, PLAN.md)
   - Canvas files are JSON-based — commit to git for version control

## Integration with Other GABBE Skills

### With `sketch-to-diagram.skill`
Use `image-recognition` MCP to analyze hand-drawn sketches, then recreate as tldraw shapes:
```
Photo → image-recognition → element list → tldraw_add_shape (×N) → .tldr file
```

### With `excalidraw.skill`
tldraw and Excalidraw serve complementary purposes:
- **tldraw**: Better for UI wireframes, rapid prototyping, full canvas management (9 tools)
- **Excalidraw**: Better for formal architecture diagrams with node-edge semantics (4 tools)

### With `visual-mcp-integration` guide
Follow Section 3 guardrails: pre-map geometry, sync state to text, verify before sharing.

## Usage Examples

### Create a UI wireframe
```
> "Create a tldraw wireframe for the login page: header bar, email input, password input, login button, forgot password link"
```

### Create an architecture canvas
```
> "Set up a tldraw canvas for our microservices architecture with API Gateway, Auth, Users, Orders, and Database components"
```

### Search across canvases
```
> "Search all tldraw canvases for shapes mentioning 'auth' or 'login'"
```

## Security & Guardrails

### 1. Local Files Only
- tldraw MCP operates exclusively on local `.tldr` files — no network access, no cloud storage.
- No API key required — fully offline operation.

### 2. Agent Guardrails
- **Pre-map Layout**: Calculate X/Y positions mathematically before adding shapes. Random placement creates unreadable canvases.
- **State Sync**: Always update text-based documentation when modifying visual canvases.
- **File Organization**: Follow project conventions for canvas file paths (`docs/wireframes/`, `docs/architecture/`).
- **Verify Content**: Call `tldraw_get_shapes` or `tldraw_read` after modifications to validate the canvas state.
