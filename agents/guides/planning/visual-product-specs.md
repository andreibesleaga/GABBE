# Guide: Visual Product Design Phase

<!-- Bridge between product discovery/PRD and architecture/implementation -->
<!-- Integrates: image-recognition MCP, Excalidraw MCP, tldraw MCP, Draw.io MCP, Mermaid -->

## Purpose

Before implementation begins, the system must have **complete visual specifications** alongside text-based requirements. This guide defines how to process visual inputs — whiteboard photos, napkin sketches, architecture diagrams, UI wireframes, state machines, and ER models — into structured, version-controlled design artifacts.

**This phase sits between PRD approval (S01) and Architecture Design (S02).**

```
S00 Strategy → S01 PRD (text) → ★ VISUAL SPEC PHASE ★ → S02 Architecture → S03 Implementation
```

---

## 1. Visual Input Catalogue

The agent accepts the following visual input types and maps each to appropriate recognition and output tools:

| Input Type | Examples | Recognition | Output Tool | Output Format |
|---|---|---|---|---|
| **Architecture sketches** | Whiteboard C4, service topology | `image-recognition` | Excalidraw or Mermaid | `.excalidraw` / `flowchart` |
| **UI wireframes** | Paper wireframes, napkin UIs | `image-recognition` | tldraw | `.tldr` |
| **Flowcharts** | Process flows, decision trees | `image-recognition` | Mermaid or Excalidraw | `flowchart TD` |
| **State diagrams** | State machines, lifecycle flows | `image-recognition` | Mermaid | `stateDiagram-v2` |
| **ER diagrams** | Database schemas, entity relationships | `image-recognition` | Mermaid or Draw.io | `erDiagram` |
| **Sequence diagrams** | API flows, actor interactions | `image-recognition` | Mermaid | `sequenceDiagram` |
| **Use case diagrams** | Actor-system interactions | `image-recognition` | Mermaid or Excalidraw | `flowchart` / `.excalidraw` |
| **Component diagrams** | Module hierarchy, package structure | `image-recognition` | Mermaid | `graph TD` |
| **Network/deployment diagrams** | Infrastructure topology | `image-recognition` | Draw.io or Excalidraw | `.drawio` / `.excalidraw` |
| **Mind maps / brainstorm boards** | Feature maps, idea clusters | `image-recognition` | tldraw | `.tldr` |
| **Figma/design tool exports** | High-fidelity mockups | Direct import | Reference only | `.png` / `.svg` |

---

## 2. Recognition Pipeline

### Step 1: Ingest Visual Input
```
User provides: photo, scan, screenshot, or exported image
Agent receives: file path or base64 image
```

### Step 2: Recognize Elements
Using `image-recognition` MCP:
- Identify all shapes (rectangles, circles, diamonds, arrows, lines)
- Extract text labels from each shape (OCR)
- Map connections (which arrows connect which elements)
- Note spatial groupings, colors, and layers
- Classify diagram type (architecture / flowchart / wireframe / ER / state / sequence)

### Step 3: Structure Results
Organize recognized elements into typed nodes and edges:
```
Nodes: {id, label, type, shape, group, position}
Edges: {source, target, label, direction, style}
Groups: {name, children[], color}
```

### Step 4: Human Verification
**MANDATORY**: Present structured element list to user before generating formal diagrams.
Recognition is imperfect — missing elements, misread labels, and ambiguous arrows are common.

### Step 5: Generate Formal Diagram
Route to appropriate output tool based on diagram type (see Section 1 table).

### Step 6: Document
Fill `VISUAL_SPEC_PACKAGE_TEMPLATE.md` with all results.

---

## 3. Output Mapping — Tool Selection Guide

### When to use each tool

| Diagram Type | **Mermaid** (text) | **Excalidraw** (visual) | **tldraw** (canvas) | **Draw.io** (enterprise) |
|---|---|---|---|---|
| Architecture (C4) | ✅ Simple (<15 nodes) | ✅ Complex, hand-drawn style | ❌ | ✅ Enterprise docs |
| Flowcharts | ✅ Default choice | ✅ Large flows | ❌ | ✅ Confluence export |
| State machines | ✅ Default choice | ❌ | ❌ | ⚠️ Only if complex |
| ER diagrams | ✅ Default choice | ❌ | ❌ | ✅ Detailed schemas |
| Sequence diagrams | ✅ Default choice | ❌ | ❌ | ❌ |
| UI wireframes | ❌ | ⚠️ Simple layouts | ✅ Default choice | ❌ |
| Mind maps | ❌ | ✅ | ✅ | ❌ |
| Deployment/infra | ⚠️ Simple only | ✅ | ❌ | ✅ Default choice |

**Priority rule**: Text-based (Mermaid) first, visual tools only when complexity demands.
See `visual-mcp-integration.md` for full tool selection criteria.

---

## 4. Integration with Product Templates

### PRD_TEMPLATE.md
- **Section 6 (Data Model)**: Supplement text schema with Mermaid `erDiagram`
- **Section 8 (UI/UX Notes)**: Link to tldraw wireframes or Figma exports
- **Section 7 (API Surface)**: Supplement with Mermaid `sequenceDiagram` for key flows

### SPEC_TEMPLATE.md
- Reference generated architecture diagrams (Excalidraw/Mermaid C4)
- Include state diagrams for complex lifecycle entities
- Embed or link ER diagrams from the Visual Spec Package

### USER_STORY_MAP_TEMPLATE.md
- Link use case diagrams to user stories
- Reference flowcharts for acceptance criteria visualization

### VISUAL_SPEC_PACKAGE_TEMPLATE.md (NEW)
- Central document collecting all visual design artifacts
- Design Readiness Checklist acts as quality gate before S02

---

## 5. Visual Spec Package Contents

A complete Visual Spec Package includes (not all required — depends on project):

### Required (for any project)
- [ ] System architecture diagram (C4 Context at minimum)
- [ ] At least one workflow/flowchart for the primary user flow
- [ ] Data model / ER diagram if persistent storage is involved

### Recommended (for UI-facing projects)
- [ ] UI wireframes for key screens (tldraw or Figma)
- [ ] Screen flow / navigation diagram
- [ ] Component hierarchy

### Optional (for complex systems)
- [ ] State diagrams for lifecycle entities (orders, payments, sessions)
- [ ] Sequence diagrams for multi-service interactions
- [ ] Deployment / infrastructure diagram
- [ ] Use case diagram for actor-system boundaries

---

## 6. Design Readiness Gate

**The agent MUST NOT proceed to implementation (S03) until the following checklist passes:**

```
Design Readiness Checklist:
  □ PRD approved (S01 complete)
  □ Architecture diagram generated and human-verified
  □ Primary user workflows diagrammed (flowchart/sequence)
  □ Data model documented (text + ER diagram if DB involved)
  □ UI wireframes created (if user-facing)
  □ State diagrams present for entities with >3 states
  □ All scanned/sketched inputs processed and documented
  □ Visual Spec Package template filled
  □ All diagrams committed to git (Mermaid in .md, .excalidraw, .tldr)
  □ Human approval received on Visual Spec Package
```

---

## 7. Security Considerations

- **External API usage**: `image-recognition` MCP sends images to vision APIs. For sensitive architecture diagrams, use verbal description or local OCR instead.
- **Diagram storage**: All generated diagrams are local files (`.excalidraw`, `.tldr`, `.drawio`, `.md`). No cloud storage unless explicitly configured.
- **PII in diagrams**: Check for credentials, internal IPs, or customer data visible in whiteboard photos before processing.
