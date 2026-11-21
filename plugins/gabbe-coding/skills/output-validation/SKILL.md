---
name: output-validation
description: "Validate LLM output against a schema with bounded retries, and mask personal data before logs and external APIs. Use when model output feeds code, a tool or a database, or when personal data could reach a log or a third-party API."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/coding/output-validation.skill.md"
  tags: "coding"
  core: "false"
  context_cost: "medium"
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

## Limits and safety
- Cap retries, token spend and wall-clock time per output, and fail closed with an error when the cap is reached.
- Validation does not replace encoding: the code that consumes the output still parameterises SQL and escapes HTML and shell arguments.
- Mask before any external API or log; leave raw-value fields out of structured logs by schema, and report entity types and counts, never raw values.
- For an untrusted sink redact rather than substitute a placeholder; masking misses entities, so the result is risk-reduced, not PII-free.
- Send the retry prompt the schema and the error description, not the rejected output verbatim.
- A schema-valid object is not true or authorised; an irreversible action still needs an independent check and the human's approval.
