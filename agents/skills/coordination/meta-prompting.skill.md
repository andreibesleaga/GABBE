---
name: meta-prompting
description: Agents optimizing prompts for other agents (Chain of Thought, Tree of Thoughts).
triggers: [meta prompting]
tags: [coordination]
role: orch-planner
---
# meta-prompting Skill

## Goal
This skill enables "Meta-Cognition": thinking about how to think.

## Steps
## 1. Optimization Strategies
- **CoT (Chain of Thought)**: "Let's think step by step." (Force reasoning before answer).
- **ToT (Tree of Thoughts)**: "Generate 3 possible solutions. Evaluate each. Pick the best."
- **Few-Shot**: Provide 3 examples of "Input -> Output" to guide the model.

## 2. Dynamic Prompt Construction
Instead of static prompts, build them based on context:
1.  **Role**: "You are a world-class [Role]."
2.  **Context**: "We are building [Project]. The tech stack is [Stack]."
3.  **Constraint**: "Do not use [Forbidden Lib]. Answer in [Format]."

## 3. Self-Correction Prompts
- "Review your previous answer. Did you meet all requirements? If not, rewrite it."
- "Are there any security vulnerabilities in the code you just wrote?"

## 4. Tool Use Prompts
- "You have access to `grep`. Use it to find the definition of `User` class before guessing."

## Security & Guardrails

### 1. Skill Security (Meta-Prompting)
- **Injection Isolation in Templates**: When dynamically constructing prompts (Role + Context + Constraints), all variable data (like Project stack or forbidden libs) must be properly escaped and isolated using XML/JSON boundaries to prevent template injection.
- **Self-Correction Consistency**: Self-correction prompts MUST prioritize checking for safety constraints (PII leakage, malicious code) above simple formatting or accuracy checks.

### 2. System Integration Security
- **Dynamic Context Verification**: Ensure that any dynamic context retrieved for the prompt (e.g., pulling code from a repo) has already passed through access-control checks confirming the user is authorized to view that context.
- **Compute Budgeting**: Tree of Thoughts (ToT) generates exponential pathways. Implement strict branching limits and token budget caps to prevent Denial of Service due to massive API cost spikes.

### 3. LLM & Agent Guardrails
- **Prompt Masking**: If providing "Few-Shot" examples from past episodic memory, explicitly scrub and mask all real user data, credentials, and identifiable information before inclusion in the meta-prompt.
- **Tool Sandbox Priming**: When advising on tool usage (e.g., "Use `grep` before guessing"), the meta-prompting engine must forcefully remind the downstream agent of the strict security boundaries of that tool (e.g., "...but only search within `/app/src/`").
