---
name: cost-benefit-router
description: Intelligent routing of tasks between Local (OS) and Remote (Cloud) resources based on complexity, privacy, and cost constraints.
triggers: [route task, optimize cost, choose model, local or remote]
tags: [brain]
context_cost: low
---
# Cost-Benefit Router

## Goal
> **Purpose**: Decide the most efficient execution path for a given task.
> **Philosophy**: "Don't use a cannon to kill a mosquito."

## Logic Flow

### Steps
## 1. Complexity Scoring (0-10)
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

## Security & Guardrails

### 1. Skill Security (Cost-Benefit Router)
- **Hard-Coded Privacy Overrides**: The agent must mathematically enforce the "Context Analysis" rule (Step 2). If a regex pattern or Data Loss Prevention (DLP) scanner flags *any* data in the context as highly sensitive (API keys, PII, internal proprietary source code), the router `decision` variable MUST be overwritten to `LOCAL`, regardless of the High Complexity score.
- **Router Tampering**: The logic that determines `Complexity Scoring` and `Routing Table` execution represents the core security boundary preventing exfiltration to the cloud. The agent must ensure the file dictating these rules (`cost-benefit-router.skill.md`) is read-only during execution and requires explicit human approval to modify its heuristics.

### 2. System Integration Security
- **Escalation Data Leakage**: In the "Self-Correction" phase, if a `LOCAL` task fails, the router escalates to `REMOTE SOTA`. If the task originally failed *because* it involved obfuscated proprietary data that the local model couldn't handle, escalating it blindly to the cloud causes an immediate data breach. The agent must completely re-run the Privacy/DLP Context check before any escalation path is approved.
- **Downgrade Attacks (Cost Exhaustion)**: An attacker might submit a massive volume of highly complex tasks disguised as "simple typos" or "routine tasks." If the router misclassifies them, it forces the system to either use expensive `REMOTE SOTA` models incessantly (Cost Exhaustion DoS) or stall out the local GPU (Compute Exhaustion DoS). The router must apply strict Rate Limiting to the intake queue before classification.

### 3. LLM & Agent Guardrails
- **Model Capability Hallucination**: The directing LLM might confidently assert that a small local model (e.g., Llama-3-8b) is perfectly capable of safely refactoring a critical Cryptographic Key Management module because the code is "short." The agent must override this; tasks involving Security, Cryptography, or IAM explicitly warrant `REMOTE SOTA` (or highly verified local experts) regardless of line-count complexity.
- **Vendor Lock-in Bias**: The LLM might develop a pattern of persistently routing medium tasks to a specific Remote provider due to implicit bias in its training data (e.g., constantly selecting GPT-4o over Claude 3.5). The router must be deterministically evaluated based on objective parameters (Token Cost, Latency, API status), totally ignoring the LLM's subjective brand preference.
