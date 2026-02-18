# AI Safety Policy & Guardrails

> **Purpose**: This document defines the boundaries and safety rules for AI Agents operating within this project.

## 1. Data Privacy (PII)
*   **Rule**: Agents MUST NOT log, store, or output Personally Identifiable Information (PII) in plain text.
*   **Definition**: PII includes email addresses, phone numbers, credit card numbers, SSNs, and home addresses.
*   **Action**: If PII is detected in logs or outputs, redact it immediately (e.g., `user@example.com` -> `[REDACTED_EMAIL]`).

## 2. Code Safety
*   **Rule**: Agents MUST NOT commit secrets, API keys, or credentials to version control.
*   **Action**: Run `gitleaks` or regex checks before every commit.
*   **Rule**: Agents MUST NOT introduce "destructive" code patterns (e.g., `rm -rf /`, dropping production tables) without explicit human confirmation.

## 3. Hallucination Guardrails
*   **Rule**: Agents MUST verify libraries and API endpoints exist before recommending them.
*   **Action**: Use `search_web` or `run_command` (npm/pip) to validate existence.

## 4. Ethical Standards
*   **Rule**: Agents MUST NOT generate content or code that promotes bias, discrimination, or harm.

## 5. Deployment Gates
*   [ ] Security Scan passed
*   [ ] No Secrets detected
*   [ ] Safety Policy reviewed by Human
