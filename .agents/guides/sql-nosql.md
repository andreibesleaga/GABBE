# Guide: SQL / NoSQL / Database Patterns
<!-- Migration-first development, PostgreSQL patterns, Redis, MongoDB -->

---

## Core Principle: Migration-First Development

**Define the schema first, derive the code from it — not the reverse.**

```
1. Design schema (ERD or text description)
2. Write migration file (SQL or ORM migration)
3. Generate/update ORM models from schema
4. Write domain entities reflecting the schema
5. Write tests against migration-created schema
```

This ensures: reproducible environments, rollback safety, and team synchronization.

---

## SQL — PostgreSQL Best Practices

### Naming Conventions

```sql
-- Tables: plural, snake_case
CREATE TABLE user_accounts (...);
CREATE TABLE order_items (...);

-- Columns: snake_case, descriptive
user_id         -- not "uid" or "userId"
created_at      -- always timestamp with timezone
updated_at      -- auto-maintained
deleted_at      -- for soft deletes (nullable = not deleted)

-- Indexes: idx_[table]_[column(s)]
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Foreign keys: fk_[child_table]_[parent_table]
ALTER TABLE orders ADD CONSTRAINT fk_orders_users
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Unique constraints: uq_[table]_[column(s)]
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
```

### Migration Safety Rules

```sql
-- SAFE: Adding nullable column (backward compatible)
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL;

-- SAFE: Adding column with default
ALTER TABLE users ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT false;

-- UNSAFE: Adding NOT NULL column without default (blocks migration on non-empty table)
-- BAD: ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NOT NULL;

-- SAFE rename strategy: add → populate → rename → drop
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255) NULL;
-- Step 2: Populate (run as data migration)
UPDATE users SET full_name = CONCAT(first_name, ' ', last_name);
-- Step 3 (next deploy): Add NOT NULL constraint
ALTER TABLE users ALTER COLUMN full_name SET NOT NULL;
-- Step 4 (next deploy): Drop old columns
ALTER TABLE users DROP COLUMN first_name, DROP COLUMN last_name;
```

### Index Strategy

```sql
-- Index columns used in WHERE, ORDER BY, JOIN ON, GROUP BY
-- Rule: if your EXPLAIN shows "Seq Scan" on a large table, add an index

-- Composite index: column order matters — put most selective column first
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
-- This index helps:   WHERE user_id = X AND status = Y
-- This index helps:   WHERE user_id = X (leftmost prefix)
-- This does NOT help: WHERE status = Y (no leftmost prefix)

-- Partial index: index only relevant rows
CREATE INDEX idx_orders_pending ON orders(created_at)
  WHERE status = 'pending';

-- Expression index: for case-insensitive search
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Check slow queries: log_min_duration_statement = 1000ms in postgresql.conf
-- Or: pg_stat_statements extension
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 20;
```

### PostgreSQL Advanced Patterns

```sql
-- JSONB for flexible attributes (use sparingly — prefer normalized schema)
CREATE TABLE product_attributes (
  product_id UUID REFERENCES products(id),
  attributes JSONB NOT NULL DEFAULT '{}'
);
CREATE INDEX idx_product_attrs_gin ON product_attributes USING gin(attributes);
-- Query: WHERE attributes @> '{"color": "red"}'

-- Full-text search (avoid Elasticsearch for simple cases)
ALTER TABLE articles ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(body, ''))
  ) STORED;
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);
-- Query: WHERE search_vector @@ plainto_tsquery('english', 'search term')

-- Window functions (avoid N+1 for ranking/aggregation)
SELECT
  user_id,
  order_total,
  RANK() OVER (PARTITION BY user_id ORDER BY order_total DESC) as rank
FROM orders;

-- Upsert (avoid race conditions on concurrent inserts)
INSERT INTO cache_entries (key, value, expires_at)
VALUES ($1, $2, $3)
ON CONFLICT (key) DO UPDATE
  SET value = EXCLUDED.value, expires_at = EXCLUDED.expires_at;
```

---

## Redis — Caching Patterns

### When to Use Redis

```
Cache: expensive computed results, session data, rate limit counters
Queue: job queues (BullMQ, Laravel Queue)
Pub/Sub: real-time notifications, event broadcasting
Rate limiting: sliding window counters
Leaderboards: sorted sets for rankings
```

### Key Naming Conventions

```
Format: [service]:[entity]:[id]:[field]

Examples:
  user:profile:123              → User profile cache
  session:abc-token-xyz         → Session data
  rate_limit:login:192.168.1.1  → Rate limit counter
  job:email:456                 → Job data
  lock:payment:order-789        → Distributed lock

Always set TTL:
  SETEX user:profile:123 3600 "{...}"    # expires in 1 hour
  SET rate_limit:login:ip INCR EX 60    # expires in 1 minute
```

### Cache-Aside Pattern

```typescript
// Read: check cache → if miss, query DB → populate cache
async function getUserById(id: string): Promise<User> {
  const cacheKey = `user:profile:${id}`;
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUniqueOrThrow({ where: { id } });
  await redis.setex(cacheKey, 3600, JSON.stringify(user)); // 1 hour TTL
  return user;
}

// Write: update DB → invalidate cache (don't update cache on write)
async function updateUser(id: string, data: UpdateUserData): Promise<User> {
  const user = await db.user.update({ where: { id }, data });
  await redis.del(`user:profile:${id}`); // Invalidate — not update
  return user;
}
```

### Rate Limiting with Redis

```typescript
// Sliding window rate limiter
async function checkRateLimit(key: string, limit: number, windowSecs: number): Promise<boolean> {
  const now = Date.now();
  const windowStart = now - (windowSecs * 1000);

  const pipeline = redis.pipeline();
  pipeline.zremrangebyscore(key, 0, windowStart);  // Remove old entries
  pipeline.zadd(key, now, `${now}`);               // Add current
  pipeline.zcard(key);                              // Count in window
  pipeline.expire(key, windowSecs);                // Auto-cleanup

  const results = await pipeline.exec();
  const count = results![2][1] as number;
  return count <= limit;
}
```

---

## MongoDB — Schema Design Patterns

### When to Use MongoDB

```
Good fit:
  - Document-oriented data (products with variable attributes)
  - Hierarchical/nested data (comments with nested replies)
  - Rapidly evolving schema (prototyping, early-stage products)
  - High write throughput with flexible schema

Poor fit:
  - Complex relationships requiring joins (use PostgreSQL)
  - Financial/accounting data requiring ACID transactions
  - Data requiring complex aggregations (use PostgreSQL window functions)
```

### Schema Design Principles

```javascript
// Embed when: documents are always accessed together, 1:1 or 1:few
{
  _id: ObjectId("..."),
  userId: "uuid",
  // Embedded address — always read with user
  address: {
    street: "123 Main St",
    city: "Austin",
    country: "US"
  }
}

// Reference when: documents accessed independently, 1:many (large), many:many
// User document (separate collection)
{ _id: ObjectId("user-1"), name: "Alice" }

// Order document (references user)
{ _id: ObjectId("order-1"), userId: "user-1", total: 99.99 }
// Query: db.orders.find({ userId: "user-1" })
```

### Indexes

```javascript
// Always index fields used in queries
db.users.createIndex({ email: 1 }, { unique: true });
db.orders.createIndex({ userId: 1, createdAt: -1 }); // compound
db.products.createIndex({ name: "text", description: "text" }); // text search

// Partial index (only index documents matching filter)
db.orders.createIndex(
  { createdAt: 1 },
  { partialFilterExpression: { status: "pending" } }
);
```

---

## Migration Safety Checklist

```
Before running any migration in production:
[ ] Tested on copy of production data (or realistic dataset size)
[ ] Rollback script written and tested
[ ] All application tests pass with new schema
[ ] Lock duration estimated (ALTER TABLE on large tables can lock for minutes)
[ ] Migration window planned (low-traffic period)
[ ] Backup confirmed before migration
[ ] Monitoring in place to detect errors immediately after migration
[ ] Rollback decision criteria defined ("if X happens, rollback immediately")
```

---

## Agent-Readable Schema Documentation

Document your schema in a format agents can read and use:

```markdown
## Database Schema — [Project Name]

### Table: users
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | UUID | PK, not null | Primary key, auto-generated |
| email | VARCHAR(255) | UNIQUE, not null | User's email (lowercased) |
| password_hash | VARCHAR(255) | not null | bcrypt hash (never plaintext) |
| role | ENUM('admin','user','guest') | not null, default: 'user' | User's role |
| email_verified_at | TIMESTAMPTZ | nullable | null = not verified |
| created_at | TIMESTAMPTZ | not null, default: NOW() | Auto-set on insert |
| updated_at | TIMESTAMPTZ | not null | Auto-updated by trigger |

**Relationships:**
- users → has many → orders (orders.user_id FK)

**Business rules:**
- email must be unique and lowercased before storage
- password_hash must NEVER be returned in API responses
- Unverified users cannot access protected routes
```
