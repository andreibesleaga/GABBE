# Sketch-to-Diagram Conversion Report

**Date**: [YYYY-MM-DD]
**Input**: [Description of input image — whiteboard photo, napkin sketch, wireframe scan]
**Recognition Tool**: image-recognition MCP ([Anthropic / OpenAI / Cloudflare])
**Output Format**: [Excalidraw / Mermaid / Draw.io]

## 1. Original Image Description

[Agent's description of the hand-drawn sketch as returned by the vision API. Include key observations about shapes, text, arrows, groupings, and spatial layout.]

## 2. Recognized Elements

### Nodes
| # | Label | Shape | Group | Notes |
|---|---|---|---|---|
| 1 | [text] | [rectangle/circle/diamond] | [group name] | [any notes] |
| 2 | | | | |

### Edges (Connections)
| # | From | To | Label | Direction |
|---|---|---|---|---|
| 1 | [source node] | [target node] | [edge label] | [→ / ← / ↔] |
| 2 | | | | |

### Groups / Frames
| # | Group Name | Contains |
|---|---|---|
| 1 | [name] | [node labels] |

## 3. Human Verification

- [ ] All nodes correctly identified
- [ ] All connections correctly mapped
- [ ] Text labels accurately recognized
- [ ] Groupings match original intent
- [ ] Missing elements added manually: [list]
- [ ] Corrections applied: [list]

## 4. Generated Diagram

**Output file**: [path/to/output.excalidraw or .md or .drawio]

[If Mermaid, paste the generated code block here:]
```mermaid
[generated diagram code]
```

## 5. Confidence & Caveats

| Aspect | Confidence | Notes |
|---|---|---|
| Node detection | [HIGH/MEDIUM/LOW] | [e.g., "All rectangles clearly visible"] |
| Text recognition | [HIGH/MEDIUM/LOW] | [e.g., "Two labels partially occluded"] |
| Connection mapping | [HIGH/MEDIUM/LOW] | [e.g., "One ambiguous arrow direction"] |
| Overall | [HIGH/MEDIUM/LOW] | |
