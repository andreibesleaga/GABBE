---
name: cryptography-standards
description: Choose and check cryptographic algorithms, password hashing and TLS settings. Use when code encrypts data, hashes passwords, stores keys or sets a TLS policy.
triggers: [encrypt data, hash passwords, set tls policy, cryptography, key management, password hashing]
tags: [security]
context_cost: low
---
# cryptography-standards

## Goal
Apply, enforce, and maintain robust cryptographic strategies to protect data at rest and data in transit across all services.

## Where it fits
Phase and gate: S02 (choices recorded in an ADR), S05 (code), S07 (review). Evidence: the ADR and the static test that fails on a banned algorithm. Guide: `guides/security/cryptography-standards.md`.

## Steps
1. **Identify Requirement**: Determine if data requires at-rest hashing, symmetric encryption, or transit protection.
2. **Algorithm Selection**: Use modern, maintained primitives. For password hashing the OWASP Password Storage Cheat Sheet (checked 2026-11-21) orders them: Argon2id first (at least 19 MiB memory, 2 iterations, parallelism 1); scrypt (N=2^17, r=8, p=1) if Argon2id is not available; bcrypt only on legacy systems (work factor at least 10, 72-byte input limit); PBKDF2-HMAC-SHA256 with at least 600,000 iterations when FIPS compliance is required. Record the parameters and who benchmarked them. For encryption use AES-256-GCM or a maintained library's default authenticated mode. **TLS (the one rule of the kit; other skills point here):** default to TLS 1.3; TLS 1.2 may be allowed for compatibility; disable TLS 1.0 and 1.1 (RFC 8996) and SSLv2 and SSLv3; keep end-of-life clients on a separate endpoint with no access to sensitive data (OWASP Transport Layer Security Cheat Sheet, checked 2026-11-21). A compliance target (for example a government or PCI scope) may set a stricter rule; the project records it in an ADR.
3. **Key Management**: Document integration paths to secure KMS or Vaults; never hardcode cryptographic keys.
4. **Verification**: Write static tests that fail the build if deprecated algorithms (MD5, SHA1) are used.

## Constraints
- Algorithm and parameter choices are written in an ADR with the source and date checked.
- A check fails the build when a banned algorithm appears in new security code.

## Output Format
The ADR with algorithms, parameters and key storage, and the static test that bans weak algorithms.

## Limits and safety
- Never write a custom algorithm. Use a maintained library.
- Do not write generated test keys or secrets to files or to the chat.
- Use a secure random source (`secrets` in Python, `crypto.randomBytes` in Node), never `Math.random()` or `random`, for tokens and keys.
- Hashing is for passwords; encryption is for data that must be read back. Do not mix them up.
- No fallback to a weaker algorithm or protocol for old clients without the human's recorded decision.
