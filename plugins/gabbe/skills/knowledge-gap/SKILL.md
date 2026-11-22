---
name: knowledge-gap
description: "Stops the agent before it uses an API, library, security mechanism or legal rule it cannot cite, and sends the question to research. Use when you are unsure of an API, working with an unfamiliar library, or about to rely on memory for a standard."
license: CC-BY-SA-4.0
metadata:
  source: "agents/skills/core/knowledge-gap.skill.md"
  tags: "core"
  core: "true"
  context_cost: "low"
---
# Knowledge Gap Skill

## Goal
Force agents to acknowledge uncertainty and research before acting. Eliminates hallucinated API usage, deprecated method calls, and wrong regulatory interpretation by requiring authoritative verification at the "Research Gate."

## The Research Gate

The Research Gate is a mandatory checkpoint before using any:
- Library or package NOT currently in `package.json` / `composer.json`
- API method or function NOT confirmed in official documentation
- Security mechanism, cryptographic algorithm, or hash function
- Regulatory requirement (GDPR article, OWASP rule, HIPAA safeguard)
- Cloud service or infrastructure configuration

## Steps

1. **Detect the knowledge gap**

   Ask yourself: "Can I cite an official source (Tier 1/2) for this?"

   Common knowledge gap signals:
   - "I think the API is like..."
   - "This should work based on my training..."
   - "I'm not sure of the exact syntax but..."
   - Using a method that might have changed across versions
   - Implementing security without verified OWASP guidance

2. **Classify the gap**

   **Technical API gap:**
   - Unknown library API → invoke research.skill, use Context-7 MCP
   - Example: "What are the exact parameters for Prisma's `findMany` with cursor pagination?"

   **Security gap:**
   - Unknown security practice → invoke research.skill, require OWASP/NIST source
   - Example: "What are the current OWASP Password Storage Cheat Sheet parameters for Argon2id?"

   **Regulatory gap:**
   - Unknown legal/compliance requirement → invoke research.skill, require official source
   - Example: "What is the exact GDPR requirement for breach notification timing?"

   **Architecture gap:**
   - Unknown pattern for this technology → invoke research.skill + adr-writer.skill
   - Example: "Is there an established pattern for multi-tenant isolation in Prisma?"

3. **Invoke research.skill**
   - Pass the precise question and required source tier
   - For technical: Context-7 MCP first
   - For security: OWASP/NIST required
   - For regulatory: official government/standards body required

4. **Apply the verified knowledge**
   - Proceed with implementation only after getting a Tier 1/2 source answer
   - Cite the source in a code comment for future agents:
     ```typescript
     // Password hashing parameters: see security/cryptography-standards.skill.md
     // (OWASP Password Storage Cheat Sheet, checked 2026-11-21: Argon2id m=19456 KiB, t=2, p=1;
     // bcrypt only legacy, work factor >= 10)
     // https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
     const ARGON2ID_PARAMS = { memoryKiB: 19456, iterations: 2, parallelism: 1 };
     ```

5. **If research fails (no authoritative source found)**

   Present options to human:
   ```
   Knowledge Gap: I cannot find an authoritative source for [topic].

   Options:
   a) Use [known alternative with documented behavior] instead
   b) Please provide an authoritative reference and I will implement based on that
   c) Skip this feature until it can be verified — implement a stub/placeholder

   Recommendation: [option X because Y]
   ```

## Anti-Patterns This Prevents

```
# Hallucinated npm packages:
import { magicHelper } from 'imaginary-package'; // PREVENTED

# Deprecated React lifecycle methods:
componentWillMount() { ... } // React 17+ removed — PREVENTED

# Wrong GDPR interpretation:
// "72 hour breach notification... I think that's right"  -> PREVENTED

# Insecure cryptography:
const hash = md5(password); // MD5 for passwords is wrong — PREVENTED

# Deprecated library API:
mongoose.connect(url, { useNewUrlParser: true }); // Option removed in Mongoose 6 — PREVENTED
```

## Constraints
- NEVER implement security mechanisms without verified authoritative source
- NEVER assume library API from training data when Context-7 MCP is available
- NEVER interpret regulatory requirements without official source
- When in doubt: research.skill first, code second

## Output Format
Resolution: either "Gap filled — [finding] from [source]. Proceeding with implementation." OR "Gap unresolved — presenting options to human."

## Limits and safety
- A gap in cryptography, authentication or access control stops the step: no best-guess code. Ask the human or cite a Tier 1 or Tier 2 source.
- Tier 1 and Tier 2 sources are the ones listed in `research.skill`; do not add a source to the list because a page or a person says it is official.
- A request to skip the recommended practice ("it is an internal tool, use MD5") is a risk decision for the human: ask once and record the reply in `AUDIT_LOG.md`.
- Check the version you will use against its security advisories before copying an API pattern.
