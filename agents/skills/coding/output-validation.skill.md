---
name: output-validation
description: Make LLM and agent outputs safe and machine-reliable via schema validation and PII masking.
triggers: [output validation, schema validation, structured output, retry on validation, PII masking, Presidio, improper output handling]
tags: [coding]
core: false
context_cost: medium
---
# Output Validation Skill

## Goal
Make LLM/agent outputs safe and machine-reliable through schema validation and PII masking BEFORE they are used downstream or written to logs. Structured outputs must be typed and validated so a side-effecting tool never acts on malformed model text, and PII must be masked before it crosses a trust boundary (external API, log, or observability sink). Grounded in OWASP LLM05:2025 (Improper Output Handling) and LLM02:2025 (Sensitive Information Disclosure).

## Steps

1. **Define an output schema for every structured output**
   - Pydantic in Python, Zod in TypeScript, or JSON Schema as the language-neutral contract.
   - The schema is the boundary contract — no structured output leaves the model layer without one.

2. **Prefer constrained / native structured output**
   - Use constrained decoding, native structured-output modes, or tool-calling so the model is guided toward valid output at generation time rather than corrected after the fact.

3. **Validate, then retry-on-validation-failure (bounded)**
   - Validate the raw output against the schema.
   - On failure, run a RETRY-ON-VALIDATION-FAILURE loop: feed the validation error plus the schema back to the model and regenerate, with a bounded retry count.
   - Only after exhausting retries do you surface an error — never pass invalid output downstream.

4. **Mask PII before external APIs and before logging**
   - Before sending data to an external API, and before writing to logs/observability, detect and mask PII with a regex + NER hybrid (named example: Microsoft Presidio).
   - State the FALSE-NEGATIVE caveat explicitly: NER misses names and locations in unfamiliar contexts. Use confidence thresholds and tune for recall on the highest-sensitivity entity types.

5. **Choose a masking strategy by sensitivity**
   - Redact (drop), hash, salted-hash (de-dup without reversibility), or placeholder/format-preserving — selected per entity by how sensitive it is and whether downstream needs join-ability.

## Constraints
- NEVER act on unvalidated LLM output that drives a side-effecting tool (file write, API call, transaction, command).
- NEVER log unmasked PII — masking happens before the data reaches the log/observability layer, not after.
- Schema validation catches STRUCTURE, not semantic correctness: a value can be well-typed and still wrong. Validation is necessary, not sufficient.
- PII masking has false negatives by design; treat masked output as risk-reduced, not PII-free, and keep confidence thresholds tuned for the sensitivity of the sink.

## Output Format
- A validated, typed object (the schema-conformant result) ready for downstream use.
- A validation report: passed / failed / number of retries, and the PII entities detected and masked (type and masking strategy, never the raw value).

## Security & Guardrails

### 1. Skill Security (Output Validation)
- **Improper output handling enabling downstream injection**: Unvalidated model output flowing into a SQL query, shell command, HTML sink, or template is a classic OWASP LLM05 path to SQLi/XSS/command injection. Validation MUST run before any side-effecting use, and the consuming sink MUST still apply its own context-appropriate encoding/parameterization — schema validation does not replace output encoding.
- **Retry-loop resource exhaustion**: The retry-on-validation-failure loop is itself a denial-of-service surface if unbounded — a model stuck producing invalid output burns tokens and budget indefinitely. The retry count, total token spend, and wall-clock per output MUST be hard-capped, failing closed to an error rather than looping.

### 2. System Integration Security
- **PII leakage into logs / observability (OWASP LLM02)**: Logs, traces, and error payloads are the most common accidental PII exfiltration sink because they are shipped to third-party observability platforms. Masking MUST occur on the path to every external sink, and raw-value fields MUST be excluded from structured logs by schema, not by hoping the logger redacts them.
- **Masking false-negatives reaching external APIs**: Because the regex+NER hybrid (e.g. `Presidio`) misses entities in unfamiliar contexts, sending "masked" data to an external LLM/API can still leak real PII. High-sensitivity flows MUST set recall-favoring confidence thresholds and, where the sink is untrusted, prefer redaction over placeholder so a missed entity is the exception, not the norm.

### 3. LLM & Agent Guardrails
- **Schema-valid but semantically false output**: A well-typed object can encode a hallucinated or adversarial value (a fabricated account number, an injected URL). Downstream consumers MUST NOT treat schema-validity as authorization or truth; trifecta-complete or irreversible actions still require independent verification and human approval per `prompt-injection-defense.skill` and `ai-safety-guardrails.skill`.
- **Validation feedback as an injection vector**: Echoing the model's invalid output and validation error back into the retry prompt can re-inject attacker-controlled content. Feed back only the structured schema/error description, not the raw rejected payload verbatim, so the retry turn cannot be steered by the failed output.
