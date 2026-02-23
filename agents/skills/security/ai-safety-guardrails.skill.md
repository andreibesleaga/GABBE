---
name: ai-safety-guardrails
description: Security-by-design for AI (Prompt Injection defense, Hallucination checks, PII filters).
triggers: [ai safety guardrails]
tags: [security]
role: prod-ethicist
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
- **Rebertha (PII)**

## 4. System Design
- **Human in the Loop (HITL)**: For high-stakes actions (Transfer Money), AI *proposes*, Human *approves*.
- **Least Privilege**: The Agent's API Token should NOT have admin access.

## Security & Guardrails

### 1. Skill Security (AI Safety Guardrails)
- **Guardrail Circumvention Prevention**: The infrastructure running the `NeMo Guardrails` or `Rebertha` PII scrubbing must be physically and logically separated from the primary LLM execution environment. If the primary LLM is successfully jailbroken, it must not possess the system-level permissions required to disable its own outgoing telemetry or content filters.
- **Filter Evasion Monitoring**: The agent must continuously audit the logs of the Input Guardrails. A sudden spike in rejected prompts or specific keywords (e.g., "DAN", "Ignore previous") must trigger an automated escalation to the Security Operations Center (SOC), indicating an active, coordinated prompt injection attack.

### 2. System Integration Security
- **Fail-Closed Architecture**: If the Output Guardrail service (e.g., the JSON format validator or sentiment analyzer) crashes or times out, the primary application must default to a "Fail-Closed" state. The system is strictly prohibited from bypassing the offline guardrail to deliver unchecked LLM output directly to the end-user.
- **PII Scrubbing Reversibility**: When `Rebertha` or similar tools redact PII from a user prompt before sending it to an external LLM, the mapping mechanism (e.g., swapping `John Doe` for `[USER_1]`) must utilize cryptographically secure, high-entropy tokens. Attackers must not be able to infer the original PII by reverse-engineering the redaction dictionary.

### 3. LLM & Agent Guardrails
- **Meta-Jailbreak Detection**: Aggressive attackers may attempt to jailbreak the primary LLM by using the guardrail system itself as an attack vector (e.g., embedding a prompt injection payload inside a legitimate string of PII to bypass the initial filter). The agent must apply recursive, multi-layered inspection to all structured inputs.
- **Hallucinated Authorization**: The agent must recognize that an LLM generating a perfectly formatted JSON response declaring `"action": "transfer_funds", "authorized": true` does NOT equate to a cryptographic authorization grant. The overarching system must never trust the LLM's assertion of authority; it must cryptographically verify the user's session token independently.
