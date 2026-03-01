---
name: visual-specs
description: Process visual inputs (scans, sketches, diagrams) into structured product specifications before implementation.
triggers: [visual spec, design phase, visual requirements, scan to spec, diagram spec, visual design, sketch spec]
tags: [product, design, visual, architecture, requirements]
context_cost: high
---
# Visual Specs Skill

## Goal
Process visual inputs — whiteboard photos, napkin sketches, architecture diagrams, UI wireframes, state machines, ER models — into structured, version-controlled design artifacts that feed into the PRD and Spec templates. This skill produces a **Visual Spec Package** that serves as the design readiness gate before implementation.

## Prerequisites
- **Image Recognition MCP**: `image-recognition` must be configured (requires vision API key)
- **At least one output MCP** (recommended: all):
  - `excalidraw` — for architecture diagrams
  - `tldraw` — for UI wireframes
  - `drawio` — for enterprise diagrams (optional)
  - Mermaid — no MCP required (text-based)
- **Approved PRD**: This skill runs after PRD approval (S01 complete)

## Steps

### Phase 1: Collect Visual Inputs
1. **Inventory all visual inputs** provided by the user:
   - Whiteboard photos, napkin drawings, paper wireframes
   - Architecture sketches, system diagrams, flowcharts
   - State machine drawings, ER model sketches
   - Figma exports, existing screenshots, mockup images
2. **Classify each input** by diagram type:
   - Architecture | Flowchart | State | ER | Sequence | Wireframe | Component | Deployment | Mind map
3. **Document in Visual Spec Package**: Section 6 (Visual Input Log)

### Phase 2: Recognize and Structure
4. **Process each visual input** through `image-recognition` MCP:
   - Identify shapes, text labels, connections, groupings
   - Classify diagram type if not already known
5. **Structure recognized elements** into typed nodes and edges
6. **Present structured list to user** for verification (MANDATORY)
7. **Apply corrections** based on user feedback

### Phase 3: Generate Formal Diagrams
8. **Route each diagram to appropriate output tool**:

   | Diagram Type | Default Tool | Alternative |
   |---|---|---|
   | Architecture (C4) | Mermaid `flowchart` | Excalidraw (>15 nodes) |
   | UI wireframes | tldraw | — |
   | Flowcharts | Mermaid `flowchart` | Excalidraw (complex) |
   | State machines | Mermaid `stateDiagram-v2` | — |
   | ER diagrams | Mermaid `erDiagram` | Draw.io (detailed) |
   | Sequence diagrams | Mermaid `sequenceDiagram` | — |
   | Component diagrams | Mermaid `graph TD` | Excalidraw |
   | Deployment diagrams | Draw.io | Excalidraw |
   | Mind maps | tldraw | Excalidraw |

9. **Generate formal diagrams** using the selected tool
10. **Verify output** — call `getFullDiagramState` (Excalidraw) or `tldraw_read` (tldraw) to confirm

### Phase 4: Assemble Visual Spec Package
11. **Fill `VISUAL_SPEC_PACKAGE_TEMPLATE.md`**:
    - Section 1: System Architecture diagram(s)
    - Section 2: Workflow & State diagrams
    - Section 3: UI/UX wireframes
    - Section 4: Data Model / ER diagrams
    - Section 5: Use Case / Sequence diagrams
    - Section 6: Visual Input Log (original images + recognition results)
    - Section 7: Design Readiness Checklist
12. **Update PRD** — link generated diagrams in Sections 6, 7, 8
13. **Update SPEC** — embed architecture and data model diagrams

### Phase 5: Design Readiness Gate
14. **Run Design Readiness Checklist** (all items must pass):
    - Architecture diagram present and verified
    - Primary user workflows diagrammed
    - Data model documented (if DB involved)
    - UI wireframes created (if user-facing)
    - State diagrams for entities with >3 states
    - All visual inputs processed and documented
    - All diagrams committed to version control
15. **Present for human approval** before proceeding to S02/S03

## Deliverables
- `VISUAL_SPEC_PACKAGE_TEMPLATE.md` — filled with all visual design artifacts
- Generated diagram files (`.excalidraw`, `.tldr`, `.drawio`, Mermaid in `.md`)
- Updated PRD and Spec templates with diagram references
- Design Readiness Checklist passed

## Integration with Existing Skills

| Skill | Interaction |
|---|---|
| `spec-writer.skill` | Visual specs feed into SPEC_TEMPLATE.md |
| `req-review.skill` | Reviews visual specs for completeness |
| `excalidraw.skill` | Generates architecture diagrams |
| `tldraw-canvas.skill` | Generates UI wireframes |
| `sketch-to-diagram.skill` | Processes individual scans |
| `design-thinking.skill` | Empathy maps → visual user flows |
| `user-story-mapping.skill` | Use case diagrams link to user stories |

## Security & Guardrails

### 1. Visual Input Security
- Scanned images may contain sensitive information (credentials, internal IPs, customer data)
- The agent MUST warn before sending whiteboard photos to external vision APIs
- For sensitive diagrams: use verbal description or local Tesseract OCR

### 2. Agent Guardrails
- **Human verification is MANDATORY** after recognition, before formal diagram generation
- **Design Readiness Gate** must pass before proceeding to implementation
- **Text-first rule**: Default to Mermaid (text-based, git-diffable) unless visual complexity demands otherwise
- **State sync**: All visual diagrams must have corresponding text descriptions in PRD/SPEC
