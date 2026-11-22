# Guide: Privacy & Data Protection (2025)
<!-- GDPR, CCPA, PII Handling, Data Minimization -->

---

## 1. Principles of Data Protection
Adhere to the core principles established by global privacy frameworks (GDPR, CCPA/CPRA, HIPAA).

### Data Minimization
- **Rule**: Only collect data you absolutely need for the specific feature you are building.
- **Action**: Do not add "just in case" fields to user profiles (e.g., collecting Birth Date when only Age > 18 verification is needed).

### Purpose Limitation
- **Rule**: Data collected for Purpose A cannot be used for Purpose B without explicit consent.
- **Action**: Ensure database models map data to specific user consents.

### Privacy by Design
- **Rule**: Privacy is not an afterthought. It is embedded into the architecture.
- **Action**: Default user settings should be the most privacy-friendly option (e.g., opt-in instead of opt-out tracking).

## 2. Handling PII (Personally Identifiable Information)
PII directly or indirectly identifies a human being (Name, Email, IP Address, Location, Device ID).

- **Logging**: **NEVER log PII**. Configure loggers to scrub emails, passwords, SSNs, and tokens before they hit stdout or centralized logging (Datadog/Splunk).
- **Encryption**: Encrypt highly sensitive PII (SSN, medical status, precise location) at the application level before writing to the database.
- **Searchability**: Encrypted PII is hard to search. Consider "Blind Indexing" (storing a **keyed HMAC** — e.g., HMAC-SHA-256 with a secret key — of the data alongside the encrypted data) to allow equality searches without revealing the plaintext. Use a keyed HMAC rather than a plain (unkeyed) hash, so an attacker who dumps the index cannot brute-force low-entropy values (emails, SSNs) offline.

## 3. Data Subject Rights
Your architecture must support these rights programmatically:

- **Right to Access/Portability**: Users must be able to download their data in a machine-readable format (JSON, CSV).
- **Right to Erasure (Right to be Forgotten)**: Define a clear "Hard Delete" vs "Soft Delete" policy. When a user requests deletion, PII must be scrubbed from backups within the legal time frame (usually 30 days).
  - *Pattern*: Instead of deleting the relational row (which breaks foreign keys), overwrite PII fields with nulls or random UUIDs, leaving the de-identified usage data intact. Note: if a **stable** UUID still links the rows to a retained identity/history, the result is **pseudonymization** (still personal data under GDPR), not anonymization — true anonymization must sever any path back to the individual.

## 4. Anonymization & Pseudonymization
- **Anonymization**: Irreversible removal of PII. The data can no longer be linked to an individual. Useful for analytics.
- **Pseudonymization**: Replacing PII with an artificial identifier (e.g., substituting user ID `123` with a random hash in analytics events). Retains statistical value while protecting identity.

## 5. Third-Party Sharing
- Validate the privacy posture of external APIs. When sending user data to Stripe, Segment, or LLMs, ensure strict Data Processing Agreements (DPAs) are in place.
- **LLMs**: Never send raw PII to public AI models (like OpenAI consumer APIs). Use Enterprise tiers with zero-retention policies or scrub PII locally before sending prompts.
