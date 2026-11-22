---
name: ai-safety-guardrails
description: "Add input, output, retrieval and execution rails around an LLM feature: PII scrubbing, output checks, and human approval for high-stakes actions. Use when building or reviewing a feature that sends user data to a model or acts on model output."
triggers: [ai guardrails, llm guardrails, pii scrubbing, output rails, human in the loop approval, ai safety]
tags: [security]
role: prod-ethicist
context_cost: low
---
# ai-safety-guardrails Skill

## Goal
This skill protects the system from its own AI.

## Where it fits
Phase and gate: S02 and S03 (rails in the design and spec), S05 (build), S07 (review). Evidence: a table of rails (input, output, dialog, retrieval, execution) in `docs/security/THREAT_MODEL.md`, and a test for each rail. Part of `security-baseline.skill.md` for AI software.

## Steps
## 1. Input Guardrails (Defense)

> **KNOWN-WEAK, necessary-not-sufficient layers.** Delimiters/"Sandwich Defense" and
> pattern-matching jailbreak filters are *trivially bypassed* and must never be the sole or
> authoritative defense — treat them as cheap pre-filters only. The authoritative controls are
> structural (instruction hierarchy, dual-LLM quarantine, least-privilege tokens, egress
> filtering, HITL on trifecta-complete actions). See `prompt-injection-defense.skill` (which
> states: "Pattern-matching filters and 'ask the LLM to detect the injection' are known-weak and
> trivially bypassed") for the layered defense these rails must enforce.

- **Prompt Injection**: "Ignore previous instructions".
  - *Defense (weak pre-filter only)*: Delimiters (XML tags), "Sandwich Defense" (System Prompt + User Input + System Reminder). Bypassable — back it with the structural controls above.
- **Jailbreaks**: "Do this in 'DAN' mode".
  - *Defense (weak pre-filter only)*: Pattern matching for known jailbreak signatures. Catches only known strings; never rely on it alone.
- **PII Scrubbing**: Regex scan input for SSN, Credit Cards, Emails *before* sending to LLM.

## 2. Output Guardrails (Verification)
- **Reasoning-variance reduction (NOT a factual-hallucination check)**: "Self-Consistency" (sample N times, take the majority answer) reduces *reasoning variance* on tasks with a single correct answer. It does **not** detect factual hallucination — if the model is confidently wrong, all N samples agree and the majority is still wrong. For factual grounding, use retrieval/citation checks and external verification, not self-consistency.
- **Tone Policing**: Sentiment analysis on output. (Block Toxic/Aggressive responses).
- **Format Validation**: Ensure JSON is valid JSON.

## 3. Libraries & Tools
- **NeMo Guardrails (NVIDIA)**
- **Guardrails AI (Python)**
- **Presidio (PII)**

## 4. System Design
- **Human in the Loop (HITL)**: For high-stakes actions (Transfer Money), AI *proposes*, Human *approves*.
- **Least Privilege**: The Agent's API Token should NOT have admin access.

## 5. The Rails Taxonomy

Rather than treating guardrails as a single filter, model them as **rails** — NeMo-Guardrails-style middleware that sits around the LLM and intercepts each stage of the interaction. Defense-in-depth means more than one rail is active, so a bypass at one stage is still caught at another.

- **Input rails**: inspect and transform what reaches the model — prompt-injection and jailbreak detection, PII scrubbing, topic/policy gating on the incoming request. See `prompt-injection-defense.skill` for the layered direct/indirect injection defenses these rails enforce.
- **Output rails**: inspect and transform what the model returns — schema/format validation, PII masking before logs and external APIs, toxicity/tone checks, and system-prompt-leakage prevention. See `output-validation.skill` for the schema-validation + retry-on-failure and PII-masking mechanics.
- **Dialog rails**: govern conversational flow — allowed topics, refusal/redirect behavior, and keeping multi-turn context on-policy.
- **Retrieval rails**: vet RAG context before it reaches the model — source provenance, untrusted-content marking, and filtering poisoned or out-of-policy documents.
- **Execution rails**: gate tool/action invocation — tool allowlisting, parameter validation, egress filtering, and human-approval on high-impact or trifecta-complete actions.

For how these controls map onto named AI-risk standards (OWASP LLM Top 10, NIST AI RMF, MITRE ATLAS, ISO/IEC 42001, EU AI Act), see the guide ai-risk-standards-map.

## Constraints
- More than one rail is active, so one bypass is caught by another.
- High-stakes actions need the human's approval in code, not in a prompt.

## Output Format
The table of rails with the test for each, and the list of actions that need human approval.

## Limits and safety
- If the guardrail service fails or times out, the application refuses. It never sends unchecked model output on.
- Redaction placeholders are random. They must not be derived from the value they replace.
- A model's statement that an action is "authorised" is not authorisation. Check the user's session and permissions in code.
- Pattern filters are pre-filters only; structural controls decide.
- Report a spike in rejected prompts to the human.
