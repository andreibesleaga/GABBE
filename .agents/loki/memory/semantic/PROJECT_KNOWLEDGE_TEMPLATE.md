# Project Knowledge — Semantic Memory
<!-- Crystallized, verified facts about this project -->
<!-- Updated by: orch-researcher, research.skill, any agent after verifying a fact -->
<!-- Format: append new sections. Never remove entries — mark as SUPERSEDED if outdated. -->
<!-- This file is loaded during session-resume.skill to give agents instant context. -->

---

## Meta

| Field | Value |
|---|---|
| **Project** | [Project name] |
| **Last Updated** | [YYYY-MM-DD] |
| **Updated by** | [agent/human] |

---

## Technology Stack

| Layer | Technology | Version | Source Verified |
|---|---|---|---|
| Runtime | [e.g., Node.js] | [e.g., 22.x LTS] | [nodejs.org/docs] |
| Framework | [e.g., Fastify] | [e.g., 5.x] | [fastify.dev] |
| ORM | [e.g., Prisma] | [e.g., 6.x] | [prisma.io/docs] |
| Database | [e.g., PostgreSQL] | [e.g., 16] | [postgresql.org] |
| Cache | [e.g., Redis] | [e.g., 7.x] | [redis.io/docs] |
| Testing | [e.g., Vitest] | [e.g., 2.x] | [vitest.dev] |
| Language | [e.g., TypeScript] | [e.g., 5.x] | [typescriptlang.org] |

---

## API / Library Facts
<!-- Facts about library APIs verified from authoritative sources (Tier 1/2) -->
<!-- Prevents hallucination of deprecated or non-existent methods -->

### [Library Name] v[X.x]

**Verified fact**: [description]
```typescript
// Example of the verified API usage
const result = await library.method({ option: value });
```
**Source**: [official docs URL or Context-7 MCP]
**Added**: [YYYY-MM-DD] by [agent]

---

### [Another Library]

**Verified fact**: [description]
**Source**: [source]
**Added**: [YYYY-MM-DD]

---

## Database Schema Facts
<!-- Key facts about the database schema that agents need to know -->

```
Key tables:
  [table_name]: [purpose, key columns, constraints]
  [table_name]: [purpose, key columns]

Naming convention: [snake_case with module prefix, e.g., users_accounts]
Migration tool: [Prisma Migrate / Flyway / etc.]
Migration directory: [path/to/migrations/]

Known quirks:
  - [e.g., The `metadata` JSONB column allows null but defaults to '{}'::jsonb]
  - [e.g., Soft deletes via `deleted_at` timestamp — never hard delete users]
```

---

## Architecture Constraints
<!-- Verified rules this project enforces — agents must not violate these -->

```
Import rules (enforced by agentic-linter):
  domain/     → no external imports
  application/ → imports domain only
  adapters/   → imports domain + application
  infrastructure/ → imports domain interfaces only
  main/       → imports all layers (composition root)

Module communication:
  - Cross-module: through index.ts public API only
  - Events: via EventBus for side effects
  - Never: direct cross-module internal imports

Forbidden patterns:
  - [e.g., No raw SQL — use Prisma only]
  - [e.g., No console.log — use logger.ts]
  - [e.g., No any type in TypeScript]
```

---

## Third-Party Integration Facts
<!-- Key facts about external services this project integrates with -->

### [Service Name] (e.g., Stripe)

```
API version: [v1, v2, etc.]
Authentication: [Bearer token / API key / OAuth]
Key endpoints used:
  - [endpoint]: [purpose]
  - [endpoint]: [purpose]
Webhook secret env var: [VAR_NAME]
Rate limits: [requests/sec or requests/hour]
Known quirks:
  - [e.g., Stripe webhook events may arrive out of order — always check event.created]
```
**Source**: [official docs URL]

---

## Security Facts
<!-- Project-specific security decisions and constraints -->

```
Auth mechanism: [e.g., JWT with HS256, 15-min access token, 7-day refresh token]
Session storage: [e.g., Redis with TTL matching token expiry]
Password hashing: [e.g., bcrypt with 12 salt rounds]
Rate limiting: [e.g., 100 req/15min per IP, 20 req/min per user]

NEVER in logs:
  - Passwords, tokens, API keys
  - PII: email, phone, SSN, DOB
  - Payment card data

Input validation boundary: [e.g., at HTTP layer using Zod — all controller inputs validated]
```

---

## Performance Facts
<!-- Verified performance characteristics and optimizations -->

```
Known slow paths:
  - [e.g., GET /api/orders without index on user_id — added idx_orders_user_id in migration 003]

Caching strategy:
  - [e.g., User profile cached in Redis with 5-min TTL, invalidated on profile update]

N+1 prevention:
  - [e.g., Always use Prisma include/select for nested relations — never load in loop]

Benchmark baselines:
  - [e.g., POST /api/orders: p50=45ms, p99=180ms (measured 2024-01-15)]
```

---

## Environment Variables
<!-- Required env vars — do NOT put values here, only the var names and purpose -->

```
Required:
  DATABASE_URL          - PostgreSQL connection string
  REDIS_URL             - Redis connection string
  JWT_SECRET            - HS256 signing secret (min 256 bits)
  [SERVICE]_API_KEY     - [purpose]

Optional:
  LOG_LEVEL             - debug|info|warn|error (default: info)
  PORT                  - HTTP server port (default: 3000)

Never hardcode. Never commit .env to git.
```

---

## Lessons Learned
<!-- Facts crystallized from past debugging sessions — prevents repeating mistakes -->
<!-- See CONTINUITY.md for the full failure log. This is the "distilled wisdom" version. -->

| Pattern | Context | What to do |
|---|---|---|
| [e.g., Prisma cursor pagination] | [when paginating large result sets] | [Use `{ cursor: { id }, take: N, skip: 1 }` — skip:1 skips the cursor record] |
| [e.g., Redis SETNX race condition] | [distributed locks] | [Use SET ... NX EX atomic command — SETNX + EXPIRE is not atomic] |

---

## SUPERSEDED Facts
<!-- Keep old entries here with SUPERSEDED marker instead of deleting -->
<!-- Helps agents understand why things changed -->

```
[DATE] SUPERSEDED: [old fact] — replaced by [new fact] because [reason]
```
