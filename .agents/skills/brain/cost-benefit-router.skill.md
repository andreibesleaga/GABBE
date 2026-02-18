---
name: cost-benefit-router
description: Intelligent routing of tasks between Local (OS) and Remote (Cloud) resources based on complexity, privacy, and cost constraints.
triggers: [route task, optimize cost, choose model, local or remote]
context_cost: low
---

# Cost-Benefit Router

> **Purpose**: Decide the most efficient execution path for a given task.
> **Philosophy**: "Don't use a cannon to kill a mosquito."

## Logic Flow

### 1. Complexity Scoring (0-10)
Analyze the prompt/task:
- **0-3 (Low)**: Typos, simple regex, one-line fixes, known boilerplate.
  - *Recommendation*: **LOCAL** (Llama-3-8b, Mistral, Grep/Sed).
- **4-7 (Medium)**: React components, API integration, unit tests, refactoring.
  - *Recommendation*: **HYBRID** (Draft Local -> Polish Remote) or mid-tier Cloud.
- **8-10 (High)**: System architecture, security review, complex debugging, creative writing.
  - *Recommendation*: **REMOTE SOTA** (Claude 3.5 Sonnet, GPT-4o).

### 2. Context Analysis
- **Privacy Critical?** (PII, Credentials, Proprietary Core) -> **FORCE LOCAL**.
- **Context Size?** (>32k tokens) -> **REMOTE** (or Local with RAG).

### 3. Routing Table

| Score | Privacy | Context | Decision | Rationale |
|---|---|---|---|---|
| Low | Any | Low | **LOCAL** | Speed, Free, Good enough. |
| Med | Low | Med | **REMOTE (Mini)** | Fast cloud models (Haiku/Flash). |
| Med | High | Any | **LOCAL (Large)** | Llama-3-70b (if available). |
| High | Low | High | **REMOTE (SOTA)** | Intelligence required via API. |
| High | High | Any | **LOCAL (Max)** | Best available local quantization. |

## Usage

**Input**:
```json
{
  "task": "Fix a typo in README_FULL.md",
  "files": ["README_FULL.md"],
  "user_preference": "auto"
}
```

**Output**:
```json
{
  "route": "LOCAL",
  "model": "mistral-tiny",
  "reason": "Low complexity task, no reasoning required."
}
```

## Self-Correction
If a routed task FAILS (e.g., Local model produces garbage):
1.  Log failure.
2.  **Escalate**: Retry with next tier up (Local -> Remote Mini -> Remote SOTA).
3.  Update heuristics.
