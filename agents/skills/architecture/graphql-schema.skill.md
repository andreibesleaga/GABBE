---
name: graphql-schema
description: Schema design, federation, and resolution strategies.
triggers: [graphql schema]
tags: [architecture]
role: eng-api
---
# graphql-schema Skill

## Goal
This skill prevents "Graph Spaghetti" and ensuring performant Graph APIs.

## Steps
## 1. Schema Design
- **Consumption-First**: Design for the UI needs, not the DB schema.
- **Naming**: `User.posts` (Good), `User.getPosts` (Bad - it's a field, not a method).
- **Nullability**:
  - Default to **Nullable** for fields (resilience: if one field fails, partial data returns).
  - Use **Non-Null (!)** only for IDs and essential arguments.

## 2. N+1 Problem (The Graph Killer)
- **Scenario**: Querying `users { posts { comments } }`.
- **Solution**: **DataLoader** pattern.
  - Batches IDs from multiple resolvers.
  - Runs *one* DB query: `SELECT * FROM posts WHERE user_id IN (1, 2, 3)`.
  - Distributes results back to resolvers.

## 3. Pagination
- Avoid `offset`/`limit`.
- Use **Relay Connection Specification** (Cursor-based):
  ```graphql
  users(first: 10, after: "cursor") {
    edges {
      node { name }
      cursor
    }
    pageInfo { hasNextPage }
  }
  ```

## 4. Security
- **Depth Limiting**: Block queries deeper than 5 levels (prevent cyclic recursion DoS).
- **Cost Analysis**: Assign points to fields. Block query if Cost > 1000.
- **Introspection**: Disable in Production.

## 5. Federation (Apollo)
- Use when splitting Graph across microservices.
- **Entity**: A type shared across subgraphs (`@key(fields: "id")`).
- **Gateway**: Composes the Supergraph.

## Security & Guardrails

### 1. Skill Security (GraphQL Schema)
- **Query Depth & Complexity Enforcement**: The agent must mandate strict limits on GraphQL Query Depth (e.g., max 5 levels) and Query Cost Analysis (assigning point values to resolvers). Without these, an attacker can craft maliciously nested queries (e.g., `author { posts { comments { author { posts... } } } }`) that instantly crash the server (GraphQL DoS).
- **Introspection Information Disclosure**: The agent must enforce that Introspection queries are strictly clamped or completely disabled in production environments. Leaving Introspection open is equivalent to publishing the entire database schema to attackers, enabling them to perfectly map out BOLA (Broken Object Level Authorization) targets.

### 2. System Integration Security
- **Resolver-Level Authorization**: The agent must explicitly define authorization checks *inside* the individual field resolvers, not just at the HTTP endpoint level. Because GraphQL allows querying arbitrary fields, granting a user access to the `User` query doesn't mean they should have access to the `User.socialSecurityNumber` field. Field-level RBAC is mandatory.
- **Mutation Idempotency & Rate Limiting**: The agent must ensure that GraphQL Mutations modify state safely and are subject to distinct rate limiting from standard queries. Mutations should require idempotency keys to prevent double-charging or logic race conditions, especially because GraphQL batches multiple mutations in a single HTTP request.

### 3. LLM & Agent Guardrails
- **Federation Subgraph Bypass**: When structuring Apollo Federation (Step 5), the LLM might assume the Gateway handles all security and the Subgraphs can trust all incoming traffic. The agent must correct this fatal flaw: Subgraphs must mutually authenticate the Gateway (e.g., via Router tokens) to prevent attackers from bypassing the Gateway's auth layer and hitting a Subgraph directly.
- **Nullability Masking Hallucination**: The LLM might suggest making sensitive fields (like `passwordHash` or `isSuperAdmin`) accessible but returning `null` if the user is unauthorized. The agent must reject this. From a security perspective, it is better to return an explicit Authorization Error or hide the field via Schema directives (`@auth`) than to silently return `null`.
