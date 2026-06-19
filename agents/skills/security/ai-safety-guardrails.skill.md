---
name: ai-safety-guardrails
description: Security-by-design for AI (Prompt Injection defense, Hallucination checks, PII filters).
triggers: [ai safety guardrails]
tags: [security]
role: prod-ethicist
context_cost: low
---
# ai-safety-guardrails Skill

## Goal
This skill protects the system from its own AI.

## Steps
## 1. Input Guardrails (Defense)
- **Prompt Injection**: "Ignore previous instructions".
  - *Defense*: Delimiters (XML tags), "Sandwich Defense" (System Prompt + User Input + System Reminder).
- **Jailbreaks**: "Do this in 'DAN' mode".
  - *Defense*: Pattern matching for known jailbreak signatures.
- **PII Scrubbing**: Regex scan input for SSN, Credit Cards, Emails *before* sending to LLM.

## 2. Output Guardrails (Verification)
- **Hallucination Check**: "Self-Consistency" (Ask 3 times, take majority).
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

## Security & Guardrails

### 1. Skill Security (AI Safety Guardrails)
- **Guardrail Circumvention Prevention**: The infrastructure running the `NeMo Guardrails` or `Presidio` PII scrubbing must be physically and logically separated from the primary LLM execution environment. If the primary LLM is successfully jailbroken, it must not possess the system-level permissions required to disable its own outgoing telemetry or content filters.
- **Filter Evasion Monitoring**: The agent must continuously audit the logs of the Input Guardrails. A sudden spike in rejected prompts or specific keywords (e.g., "DAN", "Ignore previous") must trigger an automated escalation to the Security Operations Center (SOC), indicating an active, coordinated prompt injection attack.

### 2. System Integration Security
- **Fail-Closed Architecture**: If the Output Guardrail service (e.g., the JSON format validator or sentiment analyzer) crashes or times out, the primary application must default to a "Fail-Closed" state. The system is strictly prohibited from bypassing the offline guardrail to deliver unchecked LLM output directly to the end-user.
- **PII Scrubbing Reversibility**: When `Presidio` or similar tools redact PII from a user prompt before sending it to an external LLM, the mapping mechanism (e.g., swapping `John Doe` for `[USER_1]`) must utilize cryptographically secure, high-entropy tokens. Attackers must not be able to infer the original PII by reverse-engineering the redaction dictionary.

### 3. LLM & Agent Guardrails
- **Meta-Jailbreak Detection**: Aggressive attackers may attempt to jailbreak the primary LLM by using the guardrail system itself as an attack vector (e.g., embedding a prompt injection payload inside a legitimate string of PII to bypass the initial filter). The agent must apply recursive, multi-layered inspection to all structured inputs.
- **Hallucinated Authorization**: The agent must recognize that an LLM generating a perfectly formatted JSON response declaring `"action": "transfer_funds", "authorized": true` does NOT equate to a cryptographic authorization grant. The overarching system must never trust the LLM's assertion of authority; it must cryptographically verify the user's session token independently.
