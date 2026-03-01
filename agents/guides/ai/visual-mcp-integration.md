# Guide: Visual AI vs Text AI Diagramming

When agents operate inside of a project, determining how to communicate architectural designs is critical. The GABBE Kit supports both traditional **Text-based rendering** (Mermaid, PlantUML via markdown) and **Visual Canvas rendering** (Draw.io, Miro via MCP servers).

This guide dictates when an agent should use which method.

## 1. The Default: Text-Based Diagramming (Mermaid)
By default, the agent **MUST** prioritize text-based diagramming. It is deterministic, version-controllable, easily refactored by other LLMs, and does not require complex spatial reasoning.

**Use Mermaid/Markdown when:**
*   Generating initial PRDs (`PRD_TEMPLATE.md`).
*   Writing out standard architectural patterns.
*   Documenting sequential workflows or logic inside a README.
*   The system complexity is low-to-medium (Under 15 nodes).
*   The primary consumer is another developer or agent reading markdown.

## 2. The Exception: Visual Canvas Integrations (MCP Servers)
Visual canvases are exceptional tools for high-level human collaboration, non-technical stakeholders, or massive ecosystem maps that become unreadable in Mermaid text blocks. To use these, the corresponding [Miro, Draw.io, Figma] MCP server must be enabled.

**Use Visual Canvases when:**
*   **Explicit Human Request**: The user specifically says "Draw this in Miro" or "Generate a Draw.io XML file."
*   **Extreme Complexity**: The system has \>15 interconnected microservices, rendering a Mermaid graph unreadable (the "spaghetti" effect).
*   **Spatial Requirements**: The problem requires physical grouping, swimlanes, or free-form whiteboarding (e.g., Event storming sessions).
*   **Cross-Functional Output**: The result must be consumed by Product Managers, Designers, or Executives who do not use Markdown renderers.

## 3. Operations Guardrails for Visual Tools
If the agent triggers a Visual tool (Draw.io, Miro, Excalidraw):
1.  **Coordinate Mapping**: The agent must pre-map the geometry. Use the `WHITEBOARD_DESIGN_TEMPLATE.md` to establish an X/Y grid. LLMs are poor at spatial arrangement; pre-calculating coordinates mathematically guarantees a legible graph. 
2.  **State Syncing**: If an agent updates an architecture in Miro or Excalidraw, it MUST also reflect the structural changes back into the text-based `PLAN.md` or `SYSTEM_ANALYSIS_TEMPLATE.md` to ensure the project's internal semantic memory is updated. A picture is not searchable by default RAG tools; the metadata must stay in text.
3.  **Authentication Constraints**: Visual MCP servers require OAuth or Bearer Tokens (Miro, Figma). Excalidraw and Draw.io are local-only and need no authentication. The agent must verify connectivity by calling a read operation (e.g., `get_board`) before attempting to dump 50 nodes into a massive write operation.

## 4. Excalidraw Integration

Excalidraw provides a hand-drawn aesthetic ideal for architecture diagrams, flowcharts, and wireframes. The `@cmd8/excalidraw-mcp` server enables programmatic diagram creation.

**MCP Config:**
```json
{
  "excalidraw": {
    "command": "npx",
    "args": ["-y", "@cmd8/excalidraw-mcp", "--diagram", "./docs/architecture.excalidraw"]
  }
}
```

**Tools:** `createNode`, `createEdge`, `deleteElement`, `getFullDiagramState`

**When to use Excalidraw over Draw.io/Miro:**
- Hand-drawn aesthetic is desired (informal collaboration, brainstorming)
- No authentication or cloud service needed (fully local)
- Quick architecture sketches during specs or PRD phase
- The diagram will be committed to git (`.excalidraw` is JSON-based, diffable)

**See:** `coding/excalidraw.skill.md` for full usage.

## 5. tldraw Integration

tldraw provides a persistent visual canvas ideal for UI wireframing, rapid prototyping, and visual scratchpads. The `@talhaorak/tldraw-mcp` server offers 9 tools for full canvas CRUD.

**MCP Config:**
```json
{
  "tldraw": {
    "command": "npx",
    "args": ["-y", "@talhaorak/tldraw-mcp"]
  }
}
```

**Tools:** `tldraw_create`, `tldraw_read`, `tldraw_write`, `tldraw_list`, `tldraw_search`, `tldraw_get_shapes`, `tldraw_add_shape`, `tldraw_update_shape`, `tldraw_delete_shape`

**When to use tldraw over Excalidraw/Draw.io:**
- UI wireframing and rapid prototype sketching
- Persistent visual scratchpad the agent can read and search later
- Full shape CRUD with fine-grained control (9 tools vs 4)
- Canvas files viewable at [tldraw.com](https://www.tldraw.com) or VS Code extension

**See:** `coding/tldraw-canvas.skill.md` for full usage.

## 6. Sketch-to-Diagram Pipeline

For converting **hand-drawn sketches** (whiteboard photos, napkin drawings) into formal diagrams, the GABBE kit supports a **Sketch → Recognize → Redraw** pipeline using two MCP servers:

1. **`image-recognition` MCP**: Sends the sketch image to a vision API (Anthropic/OpenAI/Cloudflare) which describes all visible elements, connections, and labels.
2. **Output MCP** (choice of):
   - `excalidraw` → `.excalidraw` file
   - `drawio` → Draw.io XML
   - None → Mermaid text (no MCP needed)

**Workflow:**
```
Photo/Scan → image-recognition MCP → Structured Element List → Human Verification → Formal Diagram
```

**Security note:** Sketch images are sent to external vision APIs. For sensitive diagrams (internal architecture, credentials on whiteboards), use local OCR (Tesseract) or have the user describe the diagram verbally instead.

**See:** `coding/sketch-to-diagram.skill.md` for full usage.
**Template:** `coding/SKETCH_TO_DIAGRAM_TEMPLATE.md` for structured output.

## 7. Visual Product Design Phase

For a complete end-to-end workflow that processes visual inputs (scanned sketches, architecture diagrams, wireframes) into structured product specifications before implementation, see:

- **Guide:** `planning/visual-product-specs.md` — input catalogue, recognition pipeline, output mapping, design readiness gate
- **Skill:** `product/visual-specs.skill.md` — 5-phase workflow from visual inputs to Visual Spec Package
- **Template:** `product/VISUAL_SPEC_PACKAGE_TEMPLATE.md` — collects all visual design artifacts with readiness checklist

